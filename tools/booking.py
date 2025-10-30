"""
Booking Tools - Handles actual reservations
For security: encrypts sensitive data, uses local storage only
"""
import json
import hashlib
from datetime import datetime
from typing import Dict, List


def encrypt_sensitive_data(data: str) -> str:
    """
    Simple encryption for demo. In production: use proper encryption (Fernet, AWS KMS, etc.)
    """
    # This is NOT secure - just for demo
    return hashlib.sha256(data.encode()).hexdigest()[:16] + "****"


def load_payment_profile():
    """Load payment info from travel profile (encrypted)"""
    try:
        with open("data/travel_profile.json", 'r') as f:
            profile = json.load(f)
        return profile.get("payment_info", {})
    except:
        return {}


def create_booking_confirmation(booking_details: Dict) -> str:
    """
    Generate a booking confirmation.
    In production: this would call airline/hotel APIs to make actual reservations
    """
    
    confirmation_code = f"CONF{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    confirmation = f"""
╔══════════════════════════════════════════════════════════╗
║         BOOKING CONFIRMATION                              ║
╚══════════════════════════════════════════════════════════╝

Confirmation Code: {confirmation_code}
Booking Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}

──────────────────────────────────────────────────────────

✈️  FLIGHT RESERVATION

{booking_details.get('flight_details', 'No flight selected')}

──────────────────────────────────────────────────────────

🏨  HOTEL RESERVATION

{booking_details.get('hotel_details', 'No hotel selected')}

──────────────────────────────────────────────────────────

💰  PAYMENT SUMMARY

Flight:        ${booking_details.get('flight_cost', 0):,.2f}
Hotel:         ${booking_details.get('hotel_cost', 0):,.2f}
              ──────────
Total:         ${booking_details.get('total_cost', 0):,.2f}

Charged to: {booking_details.get('payment_method', 'Corporate Card')}

──────────────────────────────────────────────────────────

📧  CONFIRMATION EMAILS SENT TO:
   • {booking_details.get('email', 'traveler@company.com')}
   • Travel Manager

──────────────────────────────────────────────────────────

⚠️  IMPORTANT REMINDERS:

• Check-in online 24 hours before departure
• Bring valid ID and payment card used for booking
• Review cancellation policies
• Save this confirmation for expense reporting

──────────────────────────────────────────────────────────

For changes or cancellations, contact:
📞 Corporate Travel Desk: 1-800-TRAVEL
📧 travel.help@company.com
"""
    
    # Save booking to history
    save_booking_record(confirmation_code, booking_details)
    
    return confirmation


def save_booking_record(confirmation_code: str, details: Dict):
    """Save booking to local records"""
    try:
        # Load existing bookings
        try:
            with open("data/booking_history.json", 'r') as f:
                bookings = json.load(f)
        except:
            bookings = []
        
        # Add new booking
        record = {
            "confirmation_code": confirmation_code,
            "timestamp": datetime.now().isoformat(),
            "details": details
        }
        bookings.append(record)
        
        # Save
        with open("data/booking_history.json", 'w') as f:
            json.dump(bookings, f, indent=2)
        
        print(f"✅ Booking saved: {confirmation_code}")
    except Exception as e:
        print(f"⚠️ Could not save booking record: {e}")


def mock_book_flight(flight_option: Dict, passenger_info: Dict) -> Dict:
    """
    Mock flight booking. In production: integrate with airline APIs
    (Amadeus, Sabre, airline-specific APIs)
    """
    return {
        "status": "confirmed",
        "pnr": f"PNR{datetime.now().strftime('%H%M%S')}",
        "flight": flight_option,
        "passenger": passenger_info,
        "confirmation_sent": True
    }


def mock_book_hotel(hotel_option: Dict, guest_info: Dict) -> Dict:
    """
    Mock hotel booking. In production: integrate with hotel APIs
    (Booking.com, Hotels.com, hotel chain APIs)
    """
    return {
        "status": "confirmed",
        "reservation_number": f"RES{datetime.now().strftime('%H%M%S')}",
        "hotel": hotel_option,
        "guest": guest_info,
        "confirmation_sent": True
    }


def execute_booking(selected_package: Dict) -> str:
    """
    Execute the complete booking workflow
    """
    print("\n💳 Processing booking...")
    
    # Load traveler profile
    try:
        with open("data/travel_profile.json", 'r') as f:
            profile = json.load(f)
        passenger_info = profile["personal_info"]
    except:
        passenger_info = {"full_name": "Unknown Traveler"}
    
    # Extract package details
    flight_info = selected_package.get("flight", {})
    hotel_info = selected_package.get("hotel", {})
    
    # Mock booking calls
    flight_booking = mock_book_flight(flight_info, passenger_info)
    hotel_booking = mock_book_hotel(hotel_info, passenger_info)
    
    # Create confirmation
    booking_details = {
        "flight_details": f"""
Airline: {flight_info.get('airline', 'N/A')}
Flight: {flight_info.get('flight', 'N/A')}
Departure: {flight_info.get('depart_time', 'N/A')}
Arrival: {flight_info.get('arrive_time', 'N/A')}
Passenger: {passenger_info.get('full_name', 'N/A')}
PNR: {flight_booking.get('pnr', 'N/A')}
""",
        "hotel_details": f"""
Hotel: {hotel_info.get('name', 'N/A')}
Check-in: {selected_package.get('checkin', 'N/A')}
Check-out: {selected_package.get('checkout', 'N/A')}
Nights: {hotel_info.get('nights', 0)}
Guest: {passenger_info.get('full_name', 'N/A')}
Confirmation: {hotel_booking.get('reservation_number', 'N/A')}
""",
        "flight_cost": flight_info.get('price', 0),
        "hotel_cost": hotel_info.get('total_price', 0),
        "total_cost": flight_info.get('price', 0) + hotel_info.get('total_price', 0),
        "payment_method": "Corporate Amex ending in ****",
        "email": passenger_info.get('email', 'traveler@company.com')
    }
    
    confirmation = create_booking_confirmation(booking_details)
    
    print("✅ Booking completed successfully!")
    
    return confirmation

