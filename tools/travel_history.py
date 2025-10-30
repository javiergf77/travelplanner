"""
Travel History Analysis Tools
Loads and analyzes user's past travel patterns
"""
import json
from typing import Dict, List
from collections import Counter


def load_travel_history(csv_path: str = "data/sample_travel_history.xlsx") -> List[Dict]:
    """
    Load travel history from CSV/Excel file.
    For now, we'll parse CSV format (Excel saved as CSV)
    """
    try:
        # Try to read as CSV first (simpler)
        import csv
        trips = []
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                trips.append(row)
        print(f"✅ Loaded {len(trips)} trips from history")
        return trips
    except Exception as e:
        print(f"⚠️ Could not load travel history: {e}")
        # Return sample data
        return [
            {
                "Trip Code": "TRP001",
                "Origin": "Chicago",
                "Destination": "New York",
                "Airline": "Delta",
                "Hotel": "Marriott Marquis",
                "Flight Class": "Economy",
                "Rental Car": "Enterprise",
                "Trip Date": "2024-03-15",
                "Total Cost": "1250"
            }
        ]


def load_travel_profile(profile_path: str = "data/travel_profile.json") -> Dict:
    """Load traveler's profile with preferences and payment info"""
    try:
        with open(profile_path, 'r', encoding='utf-8') as f:
            profile = json.load(f)
        print(f"✅ Loaded travel profile for {profile['personal_info']['full_name']}")
        return profile
    except Exception as e:
        print(f"⚠️ Could not load travel profile: {e}")
        return {
            "personal_info": {"full_name": "Unknown User"},
            "travel_preferences": {},
            "payment_info": {},
            "passport_info": {}
        }


def analyze_preferences(travel_history: List[Dict]) -> Dict:
    """
    Analyze travel history to determine user preferences:
    - Preferred airlines
    - Preferred hotel chains
    - Preferred rental car companies
    - Typical flight class
    - Average trip cost
    """
    if not travel_history:
        return {
            "preferred_airlines": [],
            "preferred_hotels": [],
            "preferred_rental_cars": [],
            "typical_flight_class": "Economy",
            "average_trip_cost": 0
        }
    
    airlines = []
    hotels = []
    rental_cars = []
    flight_classes = []
    costs = []
    
    for trip in travel_history:
        if trip.get("Airline"):
            airlines.append(trip["Airline"])
        if trip.get("Hotel"):
            hotels.append(trip["Hotel"].split()[0])  # Get brand name (first word)
        if trip.get("Rental Car") and trip["Rental Car"].lower() != "none":
            rental_cars.append(trip["Rental Car"])
        if trip.get("Flight Class"):
            flight_classes.append(trip["Flight Class"])
        if trip.get("Total Cost"):
            try:
                costs.append(float(trip["Total Cost"]))
            except:
                pass
    
    # Count frequencies
    airline_counts = Counter(airlines).most_common(3)
    hotel_counts = Counter(hotels).most_common(3)
    rental_counts = Counter(rental_cars).most_common(3)
    flight_class_counts = Counter(flight_classes).most_common(1)
    
    preferences = {
        "preferred_airlines": [{"name": a, "count": c} for a, c in airline_counts],
        "preferred_hotels": [{"brand": h, "count": c} for h, c in hotel_counts],
        "preferred_rental_cars": [{"company": r, "count": c} for r, c in rental_counts],
        "typical_flight_class": flight_class_counts[0][0] if flight_class_counts else "Economy",
        "average_trip_cost": sum(costs) / len(costs) if costs else 0,
        "total_trips": len(travel_history)
    }
    
    return preferences


def format_preferences_summary(preferences: Dict) -> str:
    """Format preferences into a human-readable summary"""
    lines = ["**Travel History Analysis:**\n"]
    
    lines.append(f"📊 Total trips analyzed: {preferences['total_trips']}")
    lines.append(f"💰 Average trip cost: ${preferences['average_trip_cost']:.2f}")
    lines.append(f"✈️ Typical flight class: {preferences['typical_flight_class']}\n")
    
    if preferences['preferred_airlines']:
        lines.append("**Preferred Airlines:**")
        for airline in preferences['preferred_airlines']:
            lines.append(f"  • {airline['name']} ({airline['count']} trips)")
    
    if preferences['preferred_hotels']:
        lines.append("\n**Preferred Hotels:**")
        for hotel in preferences['preferred_hotels']:
            lines.append(f"  • {hotel['brand']} ({hotel['count']} stays)")
    
    if preferences['preferred_rental_cars']:
        lines.append("\n**Preferred Rental Cars:**")
        for car in preferences['preferred_rental_cars']:
            lines.append(f"  • {car['company']} ({car['count']} rentals)")
    
    return "\n".join(lines)


# CrewAI tool wrappers
def get_traveler_preferences() -> str:
    """
    Tool for CrewAI agents to retrieve and analyze traveler preferences.
    Returns a formatted summary of travel history and preferences.
    """
    history = load_travel_history()
    profile = load_travel_profile()
    preferences = analyze_preferences(history)
    
    summary = format_preferences_summary(preferences)
    
    # Add loyalty program info from profile
    loyalty = profile.get("travel_preferences", {}).get("loyalty_programs", {})
    if loyalty:
        summary += "\n\n**Loyalty Programs:**"
        for program_type, programs in loyalty.items():
            for program in programs:
                summary += f"\n  • {program}"
    
    return summary

