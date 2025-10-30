from datetime import datetime, timedelta

def search_flights(origin, destination, depart_date, return_date):
    """
    Mock/local-friendly flight search with realistic 2025 pricing.
    Replace with duckduckgo-search or real API later.
    """
    # Realistic 2025 pricing: $400-500 for most domestic round-trip flights
    import random
    
    # 80% of flights in $400-500 range, 20% higher
    prices = []
    for _ in range(3):
        if random.random() < 0.8:
            prices.append(random.randint(400, 500))
        else:
            prices.append(random.randint(650, 850))
    
    prices.sort()
    
    return [
        {
            "airline": "Delta",
            "flight": "DL123",
            "depart_time": f"{depart_date} 08:00",
            "arrive_time": f"{depart_date} 11:10",
            "price": prices[0],
            "stops": 0,
            "duration": "2h 10m"
        },
        {
            "airline": "United",
            "flight": "UA455",
            "depart_time": f"{depart_date} 10:45",
            "arrive_time": f"{depart_date} 13:50",
            "price": prices[1],
            "stops": 0,
            "duration": "2h 5m"
        },
        {
            "airline": "American",
            "flight": "AA222",
            "depart_time": f"{depart_date} 14:30",
            "arrive_time": f"{depart_date} 18:00",
            "price": prices[2],
            "stops": 1,
            "duration": "3h 30m"
        },
    ]


def search_hotels(destination, checkin, checkout, budget):
    """
    Mock/local-friendly hotel search.
    """
    # estimate nights
    try:
        d1 = datetime.strptime(checkin, "%Y-%m-%d")
        d2 = datetime.strptime(checkout, "%Y-%m-%d")
        nights = (d2 - d1).days
        nights = nights if nights > 0 else 1
    except Exception:
        nights = 3

    budget_val = 150
    try:
        if budget:
            budget_val = int(float(budget) / nights)
    except Exception:
        pass

    return [
        {
            "name": f"{destination} Business Hotel",
            "nights": nights,
            "total_price": budget_val * nights,
            "location": destination,
        },
        {
            "name": f"{destination} Corporate Inn",
            "nights": nights,
            "total_price": (budget_val + 30) * nights,
            "location": destination,
        },
        {
            "name": f"{destination} Airport Hotel",
            "nights": nights,
            "total_price": (budget_val - 20) * nights,
            "location": destination,
        },
    ]