"""
Travel Planning Crew - Using CrewAI Project Structure
"""
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.tools import tool

# Import tools
from tools.travel_history import get_traveler_preferences
from tools.trip_research import research_destination
from tools.web_search import search_flights, search_hotels
from tools.policy_rag import check_policy_compliance, load_policy_chunks

# Tool wrappers for CrewAI
@tool("Get Traveler Preferences")
def traveler_preferences_tool() -> str:
    """
    Retrieves the traveler's historical preferences including:
    - Preferred airlines, hotels, rental cars
    - Typical flight class
    - Loyalty program information
    """
    return get_traveler_preferences()


@tool("Search Flights")
def flight_search_tool(origin: str, destination: str, depart_date: str, return_date: str) -> str:
    """Search for available flights between origin and destination."""
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
    """Search for available hotels in the destination."""
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
    """Comprehensive destination research including weather, dining, activities, and warnings."""
    return research_destination(destination, travel_date, trip_purpose)


@tool("Check Policy Compliance")
def policy_check_tool(trip_details: str) -> str:
    """Check if trip complies with company travel policy."""
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


@CrewBase
class TravelPlannerCrew():
    """Travel Planning Crew with YAML configuration"""
    
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'
    
    def __init__(self, mode: str = "local"):
        self.mode = mode
        self.llm = self._get_llm()
    
    def _get_llm(self):
        """Initialize LLM based on mode"""
        if self.mode == "local":
            return LLM(
                model="ollama/llama3.2:latest",
                base_url="http://localhost:11434",
                temperature=0.7,
            )
        else:
            print("⚠️ Online mode not configured, using local Ollama")
            return LLM(model="ollama/llama3.2:latest", base_url="http://localhost:11434")
    
    @agent
    def travel_planner(self) -> Agent:
        return Agent(
            config=self.agents_config['travel_planner'],
            tools=[
                traveler_preferences_tool,
                flight_search_tool,
                hotel_search_tool,
                destination_research_tool,
                policy_check_tool
            ],
            llm=self.llm,
            verbose=True,
            allow_delegation=True
        )
    
    @agent
    def policy_officer(self) -> Agent:
        return Agent(
            config=self.agents_config['policy_officer'],
            tools=[policy_check_tool],
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
    
    @agent
    def research_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config['research_specialist'],
            tools=[destination_research_tool],
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
    
    @agent
    def booking_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config['booking_specialist'],
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
    
    @task
    def search_options(self) -> Task:
        return Task(
            config=self.tasks_config['search_options'],
            agent=self.travel_planner()
        )
    
    @task
    def check_policy(self) -> Task:
        return Task(
            config=self.tasks_config['check_policy'],
            agent=self.policy_officer()
        )
    
    @task
    def research_destination(self) -> Task:
        return Task(
            config=self.tasks_config['research_destination'],
            agent=self.research_specialist()
        )
    
    @task
    def final_recommendation(self) -> Task:
        return Task(
            config=self.tasks_config['final_recommendation'],
            agent=self.travel_planner()
        )
    
    @crew
    def crew(self) -> Crew:
        """Creates the Travel Planner crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )


def run_travel_crew_yaml(trip_params: dict, mode: str = "local") -> str:
    """
    Execute travel planning using YAML-based crew structure
    """
    print(f"\n🚀 Starting CrewAI Travel Planning (YAML Config Mode: {mode})")
    print(f"📍 Trip: {trip_params['origin']} → {trip_params['destination']}")
    
    try:
        # Create crew with trip parameters
        crew = TravelPlannerCrew(mode=mode)
        
        # Set up inputs for YAML templates
        inputs = {
            'origin': trip_params['origin'],
            'destination': trip_params['destination'],
            'depart_date': trip_params['depart_date'],
            'return_date': trip_params['return_date'],
            'purpose': trip_params['purpose'],
            'budget': trip_params['budget']
        }
        
        # Run the crew
        result = crew.crew().kickoff(inputs=inputs)
        
        # Extract output
        if hasattr(result, 'raw'):
            output = result.raw
        elif hasattr(result, 'output'):
            output = result.output
        else:
            output = str(result)
        
        print(f"\n✅ CrewAI completed successfully!")
        print(f"📊 Output length: {len(output)} characters")
        
        # Fallback if agent returns tool actions
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

