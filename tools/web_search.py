"""
Web Search and Scraping Tools
Uses DuckDuckGo for privacy-focused searching
"""
from typing import List, Dict
import re


def search_flights(origin: str, destination: str, depart_date: str, return_date: str) -> List[Dict]:
    """
    Search for flights using web scraping.
    In production: scrape Google Flights, Kayak, or use API
    For now: enhanced mock with realistic 2025 pricing
    """
    try:
        from duckduckgo_search import DDGS
        
        # Search for flight prices
        query = f"flights from {origin} to {destination} {depart_date}"
        print(f"Searching: {query}")
        
        # In production, parse results for actual flight data
        # For now, return enhanced mock data
        
    except Exception as e:
        print(f"Web search unavailable: {e}")
    
    # Generate realistic flight options with 2025 pricing
    import random
    
    airlines_routes = {
        "Delta": {"code_prefix": "DL", "price_mult": 1.0, "is_premium": False},
        "United": {"code_prefix": "UA", "price_mult": 1.08, "is_premium": False},
        "American": {"code_prefix": "AA", "price_mult": 1.05, "is_premium": False},
        "Southwest": {"code_prefix": "WN", "price_mult": 0.92, "is_premium": False},
        "JetBlue": {"code_prefix": "B6", "price_mult": 0.95, "is_premium": False}
    }
    
    # Calculate realistic distance (miles)
    distance_estimates = {
        ("Chicago", "New York"): 790,
        ("Chicago", "San Francisco"): 1850,
        ("Chicago", "Los Angeles"): 1745,
        ("Chicago", "Miami"): 1200,
        ("Chicago", "Seattle"): 1735,
        ("Dallas", "Raleigh"): 1050,
        ("Dallas", "New York"): 1380,
        ("Dallas", "Los Angeles"): 1240,
    }
    
    route_key = (origin, destination)
    # Check reverse direction too
    if route_key not in distance_estimates:
        route_key = (destination, origin)
    base_distance = distance_estimates.get(route_key, 1000)
    
    # 2025 Realistic pricing: $400-500 for most domestic round-trip flights
    # Base price around $450, then adjust by airline and add randomization
    base_price = 450  # Average 2025 domestic round-trip price
    
    flights = []
    for airline, info in list(airlines_routes.items())[:5]:
        # 80% of flights should be in $400-500 range, 20% can be higher
        price_variation = random.random()
        
        if price_variation < 0.8:  # 80% - normal pricing
            # $400-500 range
            price = int(base_price * info["price_mult"] * random.uniform(0.88, 1.12))
        else:  # 20% - premium/peak pricing
            # Higher prices $650-850
            price = int(base_price * info["price_mult"] * random.uniform(1.5, 1.9))
        
        flight_num = f"{info['code_prefix']}{random.randint(100, 999)}"
        
        # Generate realistic times
        hours = [6, 8, 10, 13, 15, 18, 20]
        depart_hour = random.choice(hours)
        flight_duration = base_distance / 500  # ~500 mph
        arrive_hour = (depart_hour + int(flight_duration)) % 24
        
        # Direct flights are often slightly more expensive
        is_direct = random.random() < 0.7  # 70% direct
        if is_direct:
            stops = 0
            actual_duration = flight_duration
        else:
            stops = 1
            actual_duration = flight_duration + random.uniform(1.5, 3.0)  # Layover time
            price = int(price * 0.92)  # Connecting flights slightly cheaper
        
        flights.append({
            "airline": airline,
            "flight": flight_num,
            "depart_time": f"{depart_date} {depart_hour:02d}:{random.randint(0,59):02d}",
            "arrive_time": f"{depart_date} {arrive_hour:02d}:{random.randint(0,59):02d}",
            "price": price,
            "cabin_class": "Economy",
            "stops": stops,
            "duration": f"{int(actual_duration)}h {int((actual_duration % 1) * 60)}m"
        })
    
    # Sort by price
    flights.sort(key=lambda x: x['price'])
    
    return flights


def search_hotels(destination: str, checkin: str, checkout: str, budget: str) -> List[Dict]:
    """
    Search for hotels using web scraping.
    In production: scrape Booking.com, Hotels.com, or use API
    Now includes realistic 2025 pricing with corporate rates
    """
    try:
        from duckduckgo_search import DDGS
        
        query = f"hotels in {destination} near downtown"
        print(f"Searching: {query}")
        
        # In production, parse results for actual hotel data
        
    except Exception as e:
        print(f"Web search unavailable: {e}")
    
    # Calculate nights
    from datetime import datetime
    import random
    
    try:
        d1 = datetime.strptime(checkin, "%Y-%m-%d")
        d2 = datetime.strptime(checkout, "%Y-%m-%d")
        nights = (d2 - d1).days
        nights = nights if nights > 0 else 1
    except:
        nights = 3
    
    # Realistic 2025 hotel chains with corporate rates and standard rates
    hotels = [
        # Corporate discount rates ($160-200) - these should appear first
        {
            "brand": "Marriott", 
            "name": f"Courtyard by Marriott {destination}",
            "stars": 3,
            "base_rate": random.randint(165, 185),  # Corporate rate
            "corporate_rate": True,
            "note": "Corporate Rate"
        },
        {
            "brand": "Hilton",
            "name": f"Hampton Inn {destination} Downtown",
            "stars": 3,
            "base_rate": random.randint(170, 195),  # Corporate rate
            "corporate_rate": True,
            "note": "Corporate Rate"
        },
        # Standard market rates ($220-280)
        {
            "brand": "Marriott",
            "name": f"Marriott {destination} Downtown",
            "stars": 4,
            "base_rate": random.randint(220, 260),
            "corporate_rate": False,
            "note": "Standard Rate"
        },
        {
            "brand": "Hilton",
            "name": f"Hilton {destination}",
            "stars": 4,
            "base_rate": random.randint(230, 270),
            "corporate_rate": False,
            "note": "Standard Rate"
        },
        # Premium options ($280-350)
        {
            "brand": "Hyatt",
            "name": f"Hyatt Regency {destination}",
            "stars": 4,
            "base_rate": random.randint(280, 320),
            "corporate_rate": False,
            "note": "Premium"
        },
    ]
    
    results = []
    for hotel in hotels:
        nightly_rate = hotel["base_rate"]
        
        amenities = ["WiFi", "Gym", "Business Center"]
        if hotel["stars"] >= 4:
            amenities.extend(["Restaurant", "Room Service"])
        if hotel["corporate_rate"]:
            amenities.append("Corporate Discount Applied")
        
        results.append({
            "name": hotel["name"],
            "brand": hotel["brand"],
            "stars": hotel["stars"],
            "nightly_rate": nightly_rate,
            "total_price": nightly_rate * nights,
            "nights": nights,
            "location": f"{destination} Downtown",
            "amenities": amenities,
            "corporate_rate": hotel["corporate_rate"],
            "rate_type": hotel["note"],
            "distance_to_center": f"{round(0.3 + random.random() * 1.5, 1)} mi"
        })
    
    # Sort by total price (corporate rates will naturally be first)
    results.sort(key=lambda x: x['total_price'])
    
    return results


def search_rental_cars(destination: str, pickup_date: str, dropoff_date: str, preferred_company: str = None) -> List[Dict]:
    """
    Search for rental cars.
    Policy: Max $75/day, Compact or Mid-size only
    Preferred: Hertz, Enterprise, National
    """
    from datetime import datetime
    import random
    
    try:
        d1 = datetime.strptime(pickup_date, "%Y-%m-%d")
        d2 = datetime.strptime(dropoff_date, "%Y-%m-%d")
        days = (d2 - d1).days
        days = days if days > 0 else 1
    except:
        days = 3
    
    # Company policy: Max $75/day, preferred vendors (Hertz, Enterprise, National)
    companies = [
        {"name": "Hertz", "daily": 72, "preferred": True},
        {"name": "Enterprise", "daily": 65, "preferred": True},
        {"name": "National", "daily": 68, "preferred": True},
    ]
    
    # Vehicle options (all under $75/day)
    vehicles = [
        {"class": "Compact", "models": ["Toyota Corolla", "Honda Civic", "Nissan Sentra"]},
        {"class": "Mid-size", "models": ["Toyota Camry", "Honda Accord", "Chevrolet Malibu"]},
    ]
    
    results = []
    for company in companies:
        vehicle = random.choice(vehicles)
        model = random.choice(vehicle["models"])
        
        # Add small random variation to pricing
        daily_rate = company["daily"] + random.randint(-3, 3)
        daily_rate = min(daily_rate, 75)  # Enforce $75/day limit
        
        results.append({
            "company": company["name"],
            "vehicle_class": vehicle["class"],
            "model": f"{model} or similar",
            "daily_rate": daily_rate,
            "total_cost": daily_rate * days,
            "days": days,
            "location": f"{destination} Airport",
            "unlimited_miles": True,
            "preferred": company.get("preferred", False),
            "policy_compliant": daily_rate <= 75  # Always true now
        })
    
    # Sort by preference match, then price
    if preferred_company:
        results.sort(key=lambda x: (x["company"] != preferred_company, x["total_cost"]))
    else:
        results.sort(key=lambda x: x['total_cost'])
    
    return results

