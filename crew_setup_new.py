"""
Enhanced Travel Crew Setup with full CrewAI integration
This version uses proper agents with Ollama LLM
"""
from datetime import datetime
from tools.policy_rag import load_policy_chunks

print("🚀 Initializing Enhanced Travel Planner...")

# Preload policy chunks
POLICY_CHUNKS = load_policy_chunks("data/company_policy.md")


def run_travel_crew(
    user_query: str,
    origin: str,
    destination: str,
    depart_date: str,
    return_date: str,
    trip_purpose: str,
    budget: str,
    mode: str = "local",
    use_crewai: bool = True,
    use_yaml_config: bool = True,  # NEW: Use YAML-based crew structure
) -> str:
    """
    Main orchestrator with three modes:
    1. CrewAI with YAML config (recommended): Clean, maintainable structure
    2. CrewAI programmatic: Python-defined agents (legacy)
    3. Simple mode: Direct tool calls (fastest, no LLM needed)
    """
    
    trip_params = {
        "user_query": user_query,
        "origin": origin,
        "destination": destination,
        "depart_date": depart_date,
        "return_date": return_date,
        "purpose": trip_purpose or user_query,
        "budget": budget,
        "mode": mode,
        "created_at": datetime.utcnow().isoformat(),
    }
    
    if use_crewai:
        # Full CrewAI workflow with agents
        try:
            if use_yaml_config:
                # Use YAML-based crew (like debate app)
                from crew import run_travel_crew_yaml
                return run_travel_crew_yaml(trip_params, mode)
            else:
                # Use programmatic crew (legacy)
                from agents.travel_agents import run_travel_crew_ai
                return run_travel_crew_ai(trip_params, mode)
        except Exception as e:
            error_msg = f"""
❌ CrewAI mode failed: {str(e)}

**Possible issues:**
1. Ollama is not running. Start it with: `ollama serve`
2. Model not downloaded. Install with: `ollama pull llama3.2`
3. CrewAI packages not installed. Run: `pip install -r requirements.txt`

**Falling back to Simple mode...**
"""
            print(error_msg)
            # Fallback to simple mode
            use_crewai = False
    
    if not use_crewai:
        # Simple mode - direct tool execution (no LLM)
        return run_simple_mode(trip_params)


def run_simple_mode(trip_params: dict) -> str:
    """
    Simple mode: Direct tool execution without LLM agents
    Faster and doesn't require Ollama
    """
    from tools.travel_history import get_traveler_preferences, analyze_preferences, load_travel_history
    from tools.web_search import search_flights, search_hotels, search_rental_cars
    from tools.trip_research import research_destination
    from tools.policy_rag import check_policy_compliance
    
    output = []
    output.append("# 🧭 Travel Plan (Simple Mode)\n")
    
    # 1. Get preferences
    output.append("## 👤 Your Travel Preferences\n")
    preferences = get_traveler_preferences()
    output.append(preferences)
    output.append("\n---\n")
    
    # 2. Search flights
    output.append(f"## ✈️ Flight Options: {trip_params['origin']} → {trip_params['destination']}\n")
    flights = search_flights(
        trip_params['origin'],
        trip_params['destination'],
        trip_params['depart_date'],
        trip_params['return_date']
    )
    
    # Get preference data to prioritize
    history = load_travel_history()
    prefs = analyze_preferences(history)
    preferred_airlines = [a['name'] for a in prefs.get('preferred_airlines', [])]
    
    # Sort flights: direct first, preferred airlines, then price
    # Direct flights within $150 of cheapest are prioritized
    def flight_priority(f):
        is_preferred = 0 if f['airline'] in preferred_airlines else 1
        is_direct = 0 if f.get('stops', 1) == 0 else 1  # Direct flights first
        
        # Parse duration to minutes for comparison
        duration_str = f.get('duration', '3h 0m')
        try:
            hours = int(duration_str.split('h')[0])
            mins = int(duration_str.split('h')[1].replace('m', '').strip()) if 'm' in duration_str else 0
            total_minutes = hours * 60 + mins
        except:
            total_minutes = 180  # Default 3 hours
        
        # Priority: direct flights, preferred airlines, duration, then price
        return (is_direct, is_preferred, total_minutes, f['price'])
    
    flights_sorted = sorted(flights, key=flight_priority)
    
    output.append("**Top 5 Flight Options** (⭐ = preferred airline | 🎯 = direct flight):\n")
    
    # Flight comparison table
    output.append("| # | Airline | Departure | Arrival | Duration | Stops | Price |")
    output.append("| --- | --- | --- | --- | --- | --- | --- |")
    
    for i, f in enumerate(flights_sorted[:5], 1):
        star = "⭐" if f['airline'] in preferred_airlines else ""
        direct = "🎯" if f.get('stops', 0) == 0 else ""
        indicators = f"{star}{direct}".strip()
        
        airline_display = f"{indicators} {f['airline']}" if indicators else f['airline']
        stops_text = "Direct" if f.get('stops', 0) == 0 else f"{f.get('stops', 0)} stop"
        
        output.append(
            f"| {i} | {airline_display} | {f['depart_time']} | {f['arrive_time']} | "
            f"{f.get('duration', 'N/A')} | {stops_text} | **${f['price']}** |"
        )
    
    output.append("\n---\n")
    
    # 3. Search hotels
    output.append(f"## 🏨 Hotel Options in {trip_params['destination']}\n")
    hotels = search_hotels(
        trip_params['destination'],
        trip_params['depart_date'],
        trip_params['return_date'],
        trip_params['budget']
    )
    
    # Prioritize by preferred brands
    preferred_hotels = [h['brand'] for h in prefs.get('preferred_hotels', [])]
    
    def hotel_priority(h):
        is_preferred = 0 if h['brand'] in preferred_hotels else 1
        return (is_preferred, h['total_price'])
    
    hotels_sorted = sorted(hotels, key=hotel_priority)
    
    output.append("**Top 5 Hotel Options** (⭐ = preferred brand | 💼 = corporate rate):\n")
    
    # Hotel comparison table
    output.append("| # | Hotel | Stars | Nightly Rate | Nights | Total | Type |")
    output.append("| --- | --- | --- | --- | --- | --- | --- |")
    
    for i, h in enumerate(hotels_sorted[:5], 1):
        star = "⭐" if h['brand'] in preferred_hotels else ""
        corp = "💼" if h.get('corporate_rate', False) else ""
        indicators = f"{star}{corp}".strip()
        
        hotel_display = f"{indicators} {h['name']}" if indicators else h['name']
        rate_type = h.get('rate_type', 'Standard')
        
        output.append(
            f"| {i} | {hotel_display} | {'⭐' * h['stars']} | "
            f"${h['nightly_rate']} | {h['nights']} | **${h['total_price']}** | {rate_type} |"
        )
    
    output.append("\n---\n")
    
    # 3b. Search rental cars
    output.append(f"## 🚗 Rental Car Options\n")
    cars = search_rental_cars(
        trip_params['destination'],
        trip_params['depart_date'],
        trip_params['return_date']
    )
    
    # Prioritize by preferred companies (if in history)
    preferred_cars = [c['company'] for c in prefs.get('preferred_rental_cars', [])]
    
    def car_priority(c):
        is_preferred = 0 if c['company'] in preferred_cars else 1
        return (is_preferred, c['total_cost'])
    
    cars_sorted = sorted(cars, key=car_priority)
    
    output.append("**All 3 Rental Car Options** (⭐ = preferred company | All under $75/day policy):\n")
    
    # Rental car comparison table
    output.append("| # | Company | Vehicle | Daily Rate | Days | Total | Location |")
    output.append("| --- | --- | --- | --- | --- | --- | --- |")
    
    for i, c in enumerate(cars_sorted[:3], 1):
        star = "⭐" if c['company'] in preferred_cars else ""
        company_display = f"{star} {c['company']}" if star else c['company']
        vehicle_info = f"{c['vehicle_class']}: {c['model']}"
        
        output.append(
            f"| {i} | {company_display} | {vehicle_info} | "
            f"${c['daily_rate']} | {c['days']} | **${c['total_cost']}** | {c['location']} |"
        )
    
    output.append("\n---\n")
    
    # 4. Policy check
    output.append("## 🛡️ Policy Compliance Check\n")
    policy_result = check_policy_compliance(trip_params, POLICY_CHUNKS)
    output.append(f"**Status:** {policy_result['status']}\n")
    
    if policy_result.get('violations'):
        output.append("**⚠️ Violations:**")
        for v in policy_result['violations']:
            output.append(f"- {v}")
        output.append("")
    
    if policy_result.get('notes'):
        output.append("**📋 Notes:**")
        for n in policy_result['notes']:
            output.append(f"- {n}")
        output.append("")
    
    output.append("\n---\n")
    
    # 5. Weather Forecast (ALWAYS show prominently)
    from tools.trip_research import get_weather_forecast, get_restaurants, get_things_to_do, get_travel_warnings
    
    output.append("## 🌤️ Weather Forecast\n")
    weather = get_weather_forecast(trip_params['destination'], trip_params['depart_date'])
    output.append(weather)
    output.append("\n---\n")
    
    # 6. Top 5 Restaurants (ALWAYS show prominently)
    output.append("## 🍽️ Top 5 Recommended Restaurants\n")
    restaurants = get_restaurants(trip_params['destination'])
    output.append(restaurants)
    output.append("\n---\n")
    
    # 7. Additional Destination Info
    output.append("## 📍 Additional Destination Information\n")
    output.append(get_travel_warnings(trip_params['destination']))
    output.append("\n")
    output.append(get_things_to_do(trip_params['destination'], trip_params['purpose']))
    
    output.append("\n---\n")
    
    # 8. Recommended packages
    output.append("## 🎯 Recommended Travel Packages\n")
    output.append("**Complete packages with flights, hotels, and rental cars:**\n\n")
    
    # Build package table - compact format with shortened names
    output.append("| Package | Flight | Hotel | Car | **Total** |")
    output.append("| --- | --- | --- | --- | --- |")
    
    for i in range(min(3, len(flights_sorted), len(hotels_sorted), len(cars_sorted))):
        flight = flights_sorted[i]
        hotel = hotels_sorted[i]
        car = cars_sorted[i]
        total = flight['price'] + hotel['total_price'] + car['total_cost']
        
        # Shorten names to fit table - full details shown below
        airline_short = flight['airline'].replace('Airlines', '').replace('Air Lines', '').strip()
        hotel_short = hotel['name'].split()[0] if len(hotel['name']) > 20 else hotel['name']
        
        output.append(
            f"| **Package {i+1}:**<br>{airline_short} + {hotel_short} + {car['company']} | "
            f"${flight['price']} | "
            f"${hotel['total_price']} | "
            f"${car['total_cost']} | "
            f"**${total:,.0f}** |"
        )
    
    output.append("\n### Package Details:\n")
    
    for i in range(min(3, len(flights_sorted), len(hotels_sorted), len(cars_sorted))):
        flight = flights_sorted[i]
        hotel = hotels_sorted[i]
        car = cars_sorted[i]
        total = flight['price'] + hotel['total_price'] + car['total_cost']
        
        output.append(f"#### Package {i+1}: ${total:,.2f}")
        output.append(f"- ✈️ **Flight:** {flight['airline']} {flight['flight']} - ${flight['price']}")
        output.append(f"  - {flight['depart_time']} → {flight['arrive_time']}")
        stops_text = "Direct ✈️" if flight.get('stops', 0) == 0 else f"{flight.get('stops', 0)} stop(s)"
        output.append(f"  - Duration: {flight.get('duration', 'N/A')} | {stops_text}")
        
        output.append(f"- 🏨 **Hotel:** {hotel['name']} - ${hotel['total_price']} total")
        output.append(f"  - ${hotel['nightly_rate']}/night × {hotel['nights']} nights")
        
        output.append(f"- 🚗 **Rental Car:** {car['company']} - ${car['total_cost']} total")
        output.append(f"  - {car['vehicle_class']}: {car['model']}")
        output.append(f"  - ${car['daily_rate']}/day × {car['days']} days")
        
        # Preference matching
        matches = []
        if flight['airline'] in preferred_airlines:
            matches.append("preferred airline")
        if hotel['brand'] in preferred_hotels:
            matches.append("preferred hotel")
        if car['company'] in preferred_cars:
            matches.append("preferred car rental")
        
        if matches:
            output.append(f"- ⭐ **Matches:** {', '.join(matches)}")
        output.append("")
    
    output.append("\n---\n")
    output.append(f"_Mode: Simple (Direct Tools) | No LLM required_")
    
    return "\n".join(output)

