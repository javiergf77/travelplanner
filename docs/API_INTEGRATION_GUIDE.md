# 🌐 API Integration Guide
## Real Data Sources for Travel Planner

This guide shows you how to replace mock data with real APIs - **all FREE for demos!**

---

## 🎯 Quick Start: Amadeus API (BEST Choice)

**Why Amadeus?**
- ✅ FREE tier: 10,000 calls/month
- ✅ Real flight prices
- ✅ Real hotel prices
- ✅ No credit card required
- ✅ Production-grade data

### Setup Steps:

1. **Sign Up** (5 minutes)
   - Go to: https://developers.amadeus.com/register
   - Create free account
   - Confirm email

2. **Get API Keys** (2 minutes)
   - Login to dashboard
   - Go to "My Apps" → "Create New App"
   - Copy your **API Key** and **API Secret**

3. **Test Connection** (1 minute)
   ```bash
   pip install amadeus
   ```

4. **Replace Mock Data** (already prepared!)
   - Edit `tools/web_search.py`
   - Add your API keys to `.env` file
   - See code examples below

---

## 📦 **1. FLIGHTS: Amadeus Flight Offers**

### Code Example:
```python
# File: tools/web_search.py (REAL VERSION)

from amadeus import Client, ResponseError
import os

# Initialize Amadeus client
amadeus = Client(
    client_id=os.getenv('AMADEUS_API_KEY'),
    client_secret=os.getenv('AMADEUS_API_SECRET')
)

def search_flights_real(origin, destination, depart_date, return_date):
    """
    Search REAL flights using Amadeus API
    """
    try:
        response = amadeus.shopping.flight_offers_search.get(
            originLocationCode=origin,      # e.g., "DFW" (Dallas)
            destinationLocationCode=destination,  # e.g., "RDU" (Raleigh)
            departureDate=depart_date,      # "2025-11-05"
            returnDate=return_date,         # "2025-11-08"
            adults=1,
            max=5  # Top 5 results
        )
        
        flights = []
        for offer in response.data:
            itinerary = offer['itineraries'][0]
            segments = itinerary['segments']
            
            flights.append({
                "airline": segments[0]['carrierCode'],  # "DL" = Delta
                "flight": segments[0]['number'],
                "depart_time": segments[0]['departure']['at'],
                "arrive_time": segments[-1]['arrival']['at'],
                "price": float(offer['price']['total']),
                "currency": offer['price']['currency'],
                "stops": len(segments) - 1,  # 0 = direct
                "duration": itinerary['duration']
            })
        
        return flights
        
    except ResponseError as error:
        print(f"❌ Amadeus API Error: {error}")
        return []  # Fallback to mock
```

### Airport Codes Needed:
```python
# Common US airports (use IATA codes)
AIRPORTS = {
    "Dallas": "DFW",
    "Raleigh": "RDU", 
    "New York": "JFK",
    "Los Angeles": "LAX",
    "Chicago": "ORD",
    "San Francisco": "SFO",
    "Miami": "MIA",
    "Seattle": "SEA"
}
```

---

## 🏨 **2. HOTELS: Amadeus Hotel Search**

### Code Example:
```python
def search_hotels_real(destination, checkin, checkout, budget):
    """
    Search REAL hotels using Amadeus API
    """
    try:
        # Step 1: Get hotels by city
        city_search = amadeus.reference_data.locations.hotels.by_city.get(
            cityCode=destination  # "RDU" or city name
        )
        
        # Step 2: Get offers for first 5 hotels
        hotel_ids = [hotel['hotelId'] for hotel in city_search.data[:5]]
        
        offers = amadeus.shopping.hotel_offers_search.get(
            hotelIds=','.join(hotel_ids),
            checkInDate=checkin,
            checkOutDate=checkout,
            adults=1
        )
        
        hotels = []
        for offer in offers.data:
            hotel_offer = offer['offers'][0]
            
            hotels.append({
                "name": offer['hotel']['name'],
                "brand": offer['hotel'].get('chainCode', 'Independent'),
                "nightly_rate": float(hotel_offer['price']['total']) / 
                                (parse_date_diff(checkin, checkout)),
                "total_price": float(hotel_offer['price']['total']),
                "currency": hotel_offer['price']['currency'],
                "location": f"{offer['hotel']['cityName']}",
                "amenities": offer['hotel'].get('amenities', [])
            })
        
        return hotels
        
    except ResponseError as error:
        print(f"❌ Amadeus API Error: {error}")
        return []  # Fallback to mock
```

---

## 🌤️ **3. WEATHER: OpenWeatherMap (FREE)**

### Setup:
1. Sign up: https://openweathermap.org/api
2. Get FREE API key (instant)
3. 1,000 calls/day FREE

### Code Example:
```python
# File: tools/trip_research.py (REAL VERSION)

import requests
import os
from datetime import datetime

def get_weather_forecast_real(destination: str, travel_date: str) -> str:
    """
    Get REAL weather forecast using OpenWeatherMap
    """
    api_key = os.getenv('OPENWEATHER_API_KEY')
    
    try:
        # Get 5-day forecast
        url = f"http://api.openweathermap.org/data/2.5/forecast"
        params = {
            "q": destination,
            "appid": api_key,
            "units": "imperial"  # Fahrenheit
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        # Find forecast closest to travel_date
        target_date = datetime.strptime(travel_date, "%Y-%m-%d")
        
        for forecast in data['list']:
            forecast_date = datetime.fromtimestamp(forecast['dt'])
            
            if forecast_date.date() == target_date.date():
                weather = forecast['weather'][0]
                main = forecast['main']
                
                return f"""**Weather Forecast for {destination}:**

🌤️ Conditions for {travel_date}:
- Temperature: {main['temp_min']:.0f}-{main['temp_max']:.0f}°F
- Feels Like: {main['feels_like']:.0f}°F
- Conditions: {weather['description'].title()}
- Humidity: {main['humidity']}%
- Wind: {forecast['wind']['speed']} mph
- Precipitation: {forecast.get('pop', 0) * 100:.0f}% chance

💡 Recommendation: {"Pack an umbrella!" if forecast.get('pop', 0) > 0.5 else "Enjoy the weather!"}

*Source: OpenWeatherMap*
"""
        
        return f"Weather forecast not available for {travel_date}"
        
    except Exception as e:
        print(f"❌ Weather API Error: {e}")
        # Fallback to mock
        return get_weather_forecast(destination, travel_date)
```

---

## 🍽️ **4. RESTAURANTS: Yelp Fusion API (FREE)**

### Setup:
1. Sign up: https://www.yelp.com/developers/v3/manage_app
2. Create app (instant approval)
3. 500 calls/day FREE

### Code Example:
```python
import requests

def get_restaurants_real(destination: str, cuisine_type: str = "business dining") -> str:
    """
    Get REAL restaurant data from Yelp
    """
    api_key = os.getenv('YELP_API_KEY')
    
    try:
        url = "https://api.yelp.com/v3/businesses/search"
        headers = {"Authorization": f"Bearer {api_key}"}
        params = {
            "location": destination,
            "categories": "restaurants",
            "sort_by": "rating",
            "limit": 5
        }
        
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        
        results = [f"**{destination} - Top Rated Restaurants:**\n"]
        
        for i, biz in enumerate(data['businesses'], 1):
            price = biz.get('price', '$$')
            rating = biz.get('rating', 4.0)
            
            results.append(
                f"{i}. **{biz['name']}** - {', '.join(biz['categories'][:2])}"
            )
            results.append(
                f"   📍 {biz['location']['address1']} | "
                f"💰 {price} | ⭐ {rating}/5"
            )
            results.append("")
        
        results.append("*Source: Yelp*")
        return "\n".join(results)
        
    except Exception as e:
        print(f"❌ Yelp API Error: {e}")
        return get_restaurants(destination, cuisine_type)  # Fallback
```

---

## 🎭 **5. THINGS TO DO: Foursquare (FREE)**

### Setup:
1. Sign up: https://developer.foursquare.com/
2. Create app
3. 5,000 calls/day FREE (generous!)

### Code Example:
```python
def get_things_to_do_real(destination: str, trip_purpose: str = "") -> str:
    """
    Get REAL attractions from Foursquare
    """
    api_key = os.getenv('FOURSQUARE_API_KEY')
    
    try:
        url = "https://api.foursquare.com/v3/places/search"
        headers = {"Authorization": api_key}
        params = {
            "near": destination,
            "categories": "10000,12000,13000",  # Arts, Entertainment, Landmarks
            "limit": 10
        }
        
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        
        activities = [f"**Things to Do in {destination}:**\n"]
        
        for place in data['results']:
            name = place['name']
            category = place['categories'][0]['name']
            address = place['location']['formatted_address']
            
            activities.append(f"• **{name}** ({category})")
            activities.append(f"  {address}")
            activities.append("")
        
        activities.append("*Source: Foursquare*")
        return "\n".join(activities)
        
    except Exception as e:
        print(f"❌ Foursquare API Error: {e}")
        return get_things_to_do(destination, trip_purpose)  # Fallback
```

---

## 🔐 **Environment Setup**

Create `.env` file in project root:

```bash
# .env file (NEVER commit this to git!)

# Amadeus (flights + hotels)
AMADEUS_API_KEY=your_key_here
AMADEUS_API_SECRET=your_secret_here

# OpenWeatherMap (weather)
OPENWEATHER_API_KEY=your_key_here

# Yelp (restaurants)
YELP_API_KEY=your_key_here

# Foursquare (things to do)
FOURSQUARE_API_KEY=your_key_here
```

Then load in your Python:
```python
from dotenv import load_dotenv
load_dotenv()

# Now os.getenv() will work!
```

Install python-dotenv:
```bash
pip install python-dotenv
```

---

## 📊 **API Cost Calculator**

### Demo/Testing (100 searches/day):
```
Amadeus:        FREE  (10,000/month limit)
OpenWeather:    FREE  (1,000/day limit)
Yelp:           FREE  (500/day limit)
Foursquare:     FREE  (5,000/day limit)
─────────────────────────────────────
TOTAL:          $0.00/month 🎉
```

### Light Production (1,000 searches/day):
```
Amadeus:        FREE  (still under 10k/month)
OpenWeather:    FREE  (still under 1k/day)
Yelp:           $50   (need paid tier)
Foursquare:     FREE  (still under 5k/day)
─────────────────────────────────────
TOTAL:          $50/month
```

### Heavy Production (10,000 searches/day):
```
Amadeus:        $500  (need production plan)
OpenWeather:    $100  (professional plan)
Yelp:           $200  (premium plan)
Foursquare:     $100  (premium plan)
─────────────────────────────────────
TOTAL:          $900/month
```

---

## 🚀 **Integration Priority**

For your demo, integrate in this order:

1. **✅ Weather (OpenWeatherMap)** - Easiest, instant gratification
2. **✅ Restaurants (Yelp)** - Easy, great demo value
3. **✅ Flights (Amadeus)** - Medium complexity, huge impact
4. **✅ Hotels (Amadeus)** - Same API as flights
5. **✅ Things to Do (Foursquare)** - Nice to have

**Time estimate: 2-4 hours total** (all APIs combined)

---

## 🛡️ **Security Best Practices**

1. **NEVER commit `.env` file to git**
   ```bash
   echo ".env" >> .gitignore
   ```

2. **Use environment variables in production**
   - Azure: App Settings
   - AWS: Parameter Store
   - Docker: env_file

3. **Rotate API keys monthly**

4. **Set rate limits in your code**
   ```python
   import time
   from functools import wraps
   
   def rate_limit(calls_per_second=1):
       def decorator(func):
           last_call = [0]
           
           @wraps(func)
           def wrapper(*args, **kwargs):
               elapsed = time.time() - last_call[0]
               if elapsed < 1.0 / calls_per_second:
                   time.sleep(1.0 / calls_per_second - elapsed)
               last_call[0] = time.time()
               return func(*args, **kwargs)
           
           return wrapper
       return decorator
   
   @rate_limit(calls_per_second=2)
   def search_flights_real(...):
       # Will never exceed 2 calls/second
   ```

---

## 📚 **Additional Resources**

- **Amadeus Docs:** https://developers.amadeus.com/self-service/
- **OpenWeather Docs:** https://openweathermap.org/api
- **Yelp Docs:** https://www.yelp.com/developers/documentation/v3
- **Foursquare Docs:** https://developer.foursquare.com/docs

---

## 💡 **Next Steps Tomorrow**

1. ☐ Sign up for Amadeus (5 min)
2. ☐ Sign up for OpenWeatherMap (2 min)
3. ☐ Sign up for Yelp (3 min)
4. ☐ Create `.env` file with keys
5. ☐ Test weather API first (easiest)
6. ☐ Integrate one API at a time
7. ☐ Keep mock data as fallback!

**Total setup time: ~30 minutes** ⏱️

---

## 🎯 **Bottom Line**

**For your $10 budget:** Use all FREE tiers, spend $0, get real data! 🚀

Only pay when you get budget approval for production scaling.

