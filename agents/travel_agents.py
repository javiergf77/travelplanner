"""
CrewAI Agents for Travel Planning System
"""
from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import tool
import os


def get_llm(mode: str = "local"):
    """
    Get LLM based on mode.
    - local: Use Ollama (llama3.2, mistral, etc.)
    - online: Use OpenAI/Anthropic (requires API key)
    """
    if mode == "local":
        # Use Ollama - make sure it's running locally
        # Format: ollama/model:tag (required for CrewAI)
        return LLM(
            model="ollama/llama3.2:latest",
            base_url="http://localhost:11434",
            temperature=0.7,
        )
    else:
        # For online mode, you could use OpenAI
        # return LLM(model="openai/gpt-4", temperature=0.7)
        # For now, fallback to Ollama
        print("⚠️ Online mode not configured, using local Ollama")
        return LLM(model="ollama/llama3.2:latest", base_url="http://localhost:11434")


# Import tools
from tools.travel_history import get_traveler_preferences, load_travel_profile, load_travel_history, analyze_preferences
from tools.trip_research import research_destination, get_weather_forecast, get_restaurants, get_travel_warnings
from tools.web_search import search_flights, search_hotels, search_rental_cars
from tools.policy_rag import check_policy_compliance


@tool("Get Traveler Preferences")
def traveler_preferences_tool() -> str:
    """
    Retrieves the traveler's historical preferences including:
    - Preferred airlines
    - Preferred hotel chains
    - Preferred rental car companies
    - Typical flight class
    - Loyalty program information
    """
    return get_traveler_preferences()


@tool("Search Flights")
def flight_search_tool(origin: str, destination: str, depart_date: str, return_date: str) -> str:
    """
    Search for available flights between origin and destination.
    Returns flight options with prices, times, and airlines.
    """
    flights = search_flights(origin, destination, depart_date, return_date)
    
    if not flights:
        return "No flights found"
    
    result = [f"Found {len(flights)} flight options:\n"]
    for i, flight in enumerate(flights, 1):
        result.append(f"{i}. {flight['airline']} {flight['flight']}")
        result.append(f"   Departure: {flight['depart_time']}")
        result.append(f"   Arrival: {flight['arrive_time']}")
        result.append(f"   Duration: {flight.get('duration', 'N/A')}")
        result.append(f"   Price: ${flight['price']}")
        result.append(f"   Stops: {flight.get('stops', 0)}")
        result.append("")
    
    return "\n".join(result)


@tool("Search Hotels")
def hotel_search_tool(destination: str, checkin: str, checkout: str, budget: str) -> str:
    """
    Search for available hotels in the destination.
    Returns hotel options with prices, ratings, and amenities.
    """
    hotels = search_hotels(destination, checkin, checkout, budget)
    
    if not hotels:
        return "No hotels found"
    
    result = [f"Found {len(hotels)} hotel options:\n"]
    for i, hotel in enumerate(hotels, 1):
        result.append(f"{i}. {hotel['name']}")
        result.append(f"   Brand: {hotel['brand']} | Rating: {'⭐' * hotel['stars']}")
        result.append(f"   Price: ${hotel['nightly_rate']}/night × {hotel['nights']} nights = ${hotel['total_price']}")
        result.append(f"   Location: {hotel['location']} ({hotel['distance_to_center']} from center)")
        result.append(f"   Amenities: {', '.join(hotel['amenities'])}")
        result.append("")
    
    return "\n".join(result)


@tool("Research Destination")
def destination_research_tool(destination: str, travel_date: str, trip_purpose: str) -> str:
    """
    Comprehensive destination research including:
    - Weather forecast
    - Travel warnings and advisories
    - Restaurant recommendations
    - Things to do
    - Ground transportation options
    """
    return research_destination(destination, travel_date, trip_purpose)


@tool("Check Policy Compliance")
def policy_check_tool(trip_details: str) -> str:
    """
    Check if trip complies with company travel policy.
    Validates budget, flight class, hotel rates, etc.
    """
    # Parse trip_details (simple key:value format)
    trip = {}
    for line in trip_details.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            trip[key.strip()] = value.strip()
    
    from tools.policy_rag import POLICY_CHUNKS
    result = check_policy_compliance(trip, POLICY_CHUNKS)
    
    output = [f"Policy Check Status: {result['status']}\n"]
    
    if result.get('violations'):
        output.append("⚠️ Violations:")
        for v in result['violations']:
            output.append(f"  - {v}")
    
    if result.get('notes'):
        output.append("\n📋 Notes:")
        for n in result['notes']:
            output.append(f"  - {n}")
    
    return "\n".join(output)


def create_travel_planner_agent(llm) -> Agent:
    """
    Main coordinator agent - orchestrates the entire travel planning process
    """
    return Agent(
        role="Travel Planning Coordinator",
        goal="Create comprehensive, well-formatted travel plans using REAL data from tools",
        backstory="""You are an expert travel coordinator with 15 years of experience 
        in corporate travel management. You excel at understanding traveler preferences, 
        finding the best options within budget, and ensuring policy compliance.
        
        CRITICAL RULES:
        1. Use ACTUAL data from tools - real airline names, flight numbers, hotel names, prices
        2. NEVER use placeholders like XXX, [Airline], [Hotel], or [Model]
        3. Extract specific information from tool results (e.g., "United UA123 - $450")
        4. Create formatted responses with icons (✈️, 🏨, 🚗, 🎯, ⭐)
        5. Always calculate and show total costs (flight + hotel + car)
        
        You NEVER just list tool actions - you synthesize information into complete, 
        polished travel plans with all real data filled in.""",
        tools=[
            traveler_preferences_tool,
            flight_search_tool,
            hotel_search_tool,
            destination_research_tool,
            policy_check_tool
        ],
        llm=llm,
        verbose=True,
        allow_delegation=True
    )


def create_policy_agent(llm) -> Agent:
    """
    Policy enforcement specialist
    """
    return Agent(
        role="Policy Compliance Officer",
        goal="Ensure all travel plans comply with company travel policy",
        backstory="""You are a detail-oriented compliance specialist who knows the 
        company travel policy inside and out. You help travelers stay within guidelines 
        while finding creative solutions when exceptions are needed. You're firm but fair.""",
        tools=[policy_check_tool],
        llm=llm,
        verbose=True,
        allow_delegation=False
    )


def create_research_agent(llm) -> Agent:
    """
    Destination research specialist - optimized for speed
    """
    return Agent(
        role="Destination Research Specialist",
        goal="Quickly retrieve destination information using the research tool",
        backstory="""You are an efficient travel researcher with access to a comprehensive 
        research tool. You call the destination_research_tool with the destination and dates, 
        then return its output directly. You work fast and focus on speed.""",
        tools=[destination_research_tool],
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=5  # Limit iterations to prevent hanging
    )


def create_booking_agent(llm) -> Agent:
    """
    Booking specialist (handles final reservation)
    """
    return Agent(
        role="Booking Specialist",
        goal="Execute travel bookings accurately and efficiently",
        backstory="""You are a meticulous booking agent who handles reservations 
        with precision. You double-check all details, ensure loyalty programs are 
        applied, and provide clear confirmation information. You make booking stress-free.""",
        llm=llm,
        verbose=True,
        allow_delegation=False
    )


def create_travel_tasks(agents: dict, trip_params: dict) -> list:
    """
    Create the task workflow for travel planning
    """
    
    # Task 1: Analyze preferences and search options
    search_task = Task(
        description=f"""
        Plan a business trip with these parameters:
        - Origin: {trip_params['origin']}
        - Destination: {trip_params['destination']}
        - Departure: {trip_params['depart_date']}
        - Return: {trip_params['return_date']}
        - Purpose: {trip_params['purpose']}
        - Budget: ${trip_params['budget']}
        
        Steps:
        1. Get traveler's preferences and history (airlines, hotels, rental cars)
        2. Search for flight options
        3. Search for hotel options
        4. Search for rental car options (Hertz, Enterprise, National - max $75/day) - MUST show all 3 companies
        5. Prioritize options that match traveler's preferences
        6. Present top 3 travel packages (flight + hotel + rental car combinations)
        """,
        expected_output="""A list of 3 recommended travel packages, each with:
        - Flight details (airline, times, price, direct vs connecting)
        - Hotel details (name, location, nightly rate, total)
        - Rental car details (company, vehicle, daily rate, total)
        - Total package cost (flight + hotel + car)
        - Why this option matches traveler preferences""",
        agent=agents['planner']
    )
    
    # Task 2: Policy compliance check
    policy_task = Task(
        description=f"""
        Review the recommended travel packages and verify they comply with company policy.
        Check: flight class restrictions, hotel rate limits, total budget, advance booking.
        Flag any violations and suggest alternatives if needed.
        """,
        expected_output="""Policy compliance report for each package with:
        - Compliance status (approved/needs review)
        - Any violations or warnings
        - Recommendations for policy-compliant alternatives""",
        agent=agents['policy'],
        context=[search_task]
    )
    
    # Task 3: Destination research
    research_task = Task(
        description=f"""
        Use the research_destination_tool to get information about {trip_params['destination']} 
        for travel dates {trip_params['depart_date']} to {trip_params['return_date']}.
        
        Simply call: research_destination_tool(destination="{trip_params['destination']}", 
        travel_date="{trip_params['depart_date']}", trip_purpose="{trip_params['purpose']}")
        
        Return the tool output directly without modification.
        """,
        expected_output="""The complete output from research_destination_tool including weather forecast, 
        top 5 restaurants, things to do, and travel warnings. Return exactly as provided by the tool.""",
        agent=agents['research']
    )
    
    # Task 4: Final recommendation
    final_task = Task(
        description=f"""
        Create a comprehensive travel plan from {trip_params['origin']} to {trip_params['destination']} 
        using ACTUAL data from previous tasks.
        
        CRITICAL: Use real flight numbers, hotel names, prices from the tool results. DO NOT use placeholders like XXX or [Airline].
        
        Format your response with these sections using icons:
        
        ## 🎯 Recommended Travel Packages
        
        **Complete packages with flights, hotels, and rental cars:**
        
        Create a compact table with 3 packages. Use this format:
        
        | Package | Flight | Hotel | Car | **Total** |
        | --- | --- | --- | --- | --- |
        
        Keep it simple:
        - Package column: "Package 1:<br>United + Courtyard + Hertz" (use <br> for line break)
        - Flight column: "$450" (just the number)
        - Hotel column: "$525" (just the number)
        - Car column: "$195" (just the number, shortened header saves space)
        - Total column: "**$1,170**" (bold, has more room now)
        
        ### Package Details:
        
        For each package, include:
        - ✈️ **Flight:** Use actual airline, flight number, and price from tools
        - 🏨 **Hotel:** Use actual hotel name, nightly rate, total cost from tools
        - 🚗 **Rental Car:** Use actual company name, vehicle type, daily rate from tools
        - ⭐ **Matches:** List any that match travel history preferences
        
        Also include these sections with data from previous tasks:
        - ## ✈️ Flight Options (show 3-5 flights in a table)
        - ## 🏨 Hotel Options (show 3-5 hotels in a table)
        - ## 🚗 Rental Car Options (show all 3: Hertz, Enterprise, National)
        - ## 🛡️ Policy Compliance (status from policy check)
        - ## 🌤️ Weather Forecast (from research tool)
        - ## 🍽️ Top 5 Restaurants (from research tool)
        - ## 📍 Things to Do (from research tool)
        - ## 📋 Booking Steps
        """,
        expected_output="""A complete travel plan with real data from the tools. Use icons (✈️, 🏨, 🚗, 🎯, ⭐).
        Include package comparison table with ACTUAL prices, airlines, hotels, and rental companies.
        NO placeholders - all data must be real from tool results.""",
        agent=agents['planner'],
        context=[search_task, policy_task, research_task]
    )
    
    return [search_task, policy_task, research_task, final_task]


def run_travel_crew_ai(trip_params: dict, mode: str = "local") -> str:
    """
    Execute the full CrewAI workflow for travel planning
    """
    print(f"\n🚀 Starting CrewAI Travel Planning (Mode: {mode})")
    print(f"📍 Trip: {trip_params['origin']} → {trip_params['destination']}")
    
    # Initialize LLM
    llm = get_llm(mode)
    
    # Create agents
    agents = {
        'planner': create_travel_planner_agent(llm),
        'policy': create_policy_agent(llm),
        'research': create_research_agent(llm),
        'booking': create_booking_agent(llm)
    }
    
    # Create tasks
    tasks = create_travel_tasks(agents, trip_params)
    
    # Create and run crew
    crew = Crew(
        agents=list(agents.values())[:3],  # planner, policy, research
        tasks=tasks,
        process=Process.sequential,
        verbose=True
    )
    
    try:
        result = crew.kickoff()
        
        # Extract the actual output from CrewOutput object
        if hasattr(result, 'raw'):
            output = result.raw
        elif hasattr(result, 'output'):
            output = result.output
        else:
            output = str(result)
        
        print(f"\n✅ CrewAI completed successfully!")
        print(f"📊 Output length: {len(output)} characters")
        
        # Only fall back if output is clearly broken (very short or just tool syntax)
        if len(output) < 500 or (output.count("Action:") > 3):
            print("⚠️ CrewAI output appears incomplete.")
            print("⚠️ Falling back to Simple Mode...")
            from crew_setup_new import run_simple_mode
            return run_simple_mode(trip_params)
        
        return output
        
    except Exception as e:
        print(f"❌ CrewAI execution error: {e}")
        import traceback
        traceback.print_exc()
        return f"Error during travel planning: {str(e)}\n\nPlease ensure Ollama is running locally (ollama serve)"

