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
        goal="Create comprehensive, well-formatted travel plans with specific recommendations",
        backstory="""You are an expert travel coordinator with 15 years of experience 
        in corporate travel management. You excel at understanding traveler preferences, 
        finding the best options within budget, and ensuring policy compliance.
        
        IMPORTANT: When presenting final recommendations, you provide detailed, 
        well-formatted responses with specific flight and hotel options, prices, 
        and clear explanations. You NEVER just list tool actions - you always 
        synthesize information into a complete narrative travel plan.""",
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
    Destination research specialist
    """
    return Agent(
        role="Destination Research Specialist",
        goal="Provide comprehensive destination intelligence and travel recommendations",
        backstory="""You are a worldly travel researcher who has visited hundreds of 
        cities. You provide practical, up-to-date information about destinations including 
        weather, safety, dining, and activities. You focus on information that helps 
        business travelers make the most of their trips.""",
        tools=[destination_research_tool],
        llm=llm,
        verbose=True,
        allow_delegation=False
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
        Research {trip_params['destination']} for travel dates {trip_params['depart_date']} 
        to {trip_params['return_date']}.
        
        Provide:
        - Weather forecast
        - Travel warnings/advisories
        - Top 5 business-friendly restaurants
        - Things to do (evening/downtime activities)
        - Ground transportation tips
        """,
        expected_output="""Comprehensive destination guide with weather, dining, 
        activities, safety info, and transportation recommendations""",
        agent=agents['research']
    )
    
    # Task 4: Final recommendation
    final_task = Task(
        description=f"""
        Using the information from previous tasks, create a comprehensive travel plan for the trip from {trip_params['origin']} to {trip_params['destination']}.
        
        REQUIRED FORMAT - You MUST include ALL sections below:
        
        1. **Flight Options:** List 3 options with departure/arrival times and prices
        
        2. **Hotel Options:** List 3 options with nightly rates and total costs
        
        3. **Rental Car Options:** MANDATORY - List ALL 3 options (Hertz, Enterprise, National) with daily rates and total costs.
           You MUST show all three companies in a comparison chart - not just the preferred one.
        
        4. **Total Package Cost:** MANDATORY TABLE FORMAT (use markdown table):
        
        | Option | Flight | Hotel | Rental Car | Total |
        | --- | --- | --- | --- | --- |
        | **Package 1:** [Airline] + [Hotel] + [Car Co.] | $XXX | $XXX | $XXX | $XXX |
        | **Package 2:** [Airline] + [Hotel] + [Car Co.] | $XXX | $XXX | $XXX | $XXX |
        | **Package 3:** [Airline] + [Hotel] + [Car Co.] | $XXX | $XXX | $XXX | $XXX |
        
        5. **Policy Compliance:** Summary of any issues or approvals needed (ensure car rentals are under $75/day)
        
        6. **Destination Guide:** Brief weather, dining, and activity highlights
        
        7. **Next Steps:** Clear booking instructions
        
        CRITICAL: The table in section 4 is MANDATORY. Always include it with exact pricing for all components.
        Use markdown formatting with headers, bullet points, and emphasis.
        Do NOT just return tool actions - provide the complete formatted response.
        """,
        expected_output="""A complete, formatted travel plan in markdown with:
        - Clear headers for each section
        - 3 specific flight options with all details
        - 3 specific hotel options with all details
        - ALL 3 rental car options (Hertz, Enterprise, National) in a comparison chart - DO NOT show just one
        - MANDATORY: Markdown table showing Total Package Cost for all 3 combinations (flight + hotel + car)
        - Policy compliance summary (ensure car rentals are under $75/day)
        - Destination highlights
        - Action items for booking
        
        CRITICAL: The rental car comparison chart must show ALL THREE companies (Hertz, Enterprise, National).
        Do not show only the preferred option - the user needs to see all choices.
        The table format is critical for user decision-making.
        This should be a final, polished response ready for the traveler to read.""",
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
        
        # If output is still just a tool action (not a proper narrative), fall back to simple mode
        if "Action:" in output and len(output) < 1000:
            print("⚠️ Agent returned tool actions instead of narrative response.")
            print("⚠️ Falling back to Simple Mode for proper formatting...")
            from crew_setup_new import run_simple_mode
            return run_simple_mode(trip_params)
        
        return output
        
    except Exception as e:
        print(f"❌ CrewAI execution error: {e}")
        import traceback
        traceback.print_exc()
        return f"Error during travel planning: {str(e)}\n\nPlease ensure Ollama is running locally (ollama serve)"

