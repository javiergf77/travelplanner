from datetime import datetime
from tools.travel_tools import search_flights, search_hotels
from tools.policy_rag import check_policy_compliance, load_policy_chunks

# if you need proper CrewAI classes, import them here
# from crewai import Agent, Task, Crew

# Preload policy at module import time
print("🚀 Initializing Travel Planner...")
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
) -> str:
    """
    Main orchestrator: builds a trip proposal, checks policy, returns final text.
    In your real setup this was CrewAI agents; here we keep same logic in one function
    so you can run without the full crew if needed.
    """

    # 1) Planner: normalize / enrich trip request
    trip = {
        "origin": origin,
        "destination": destination,
        "depart_date": depart_date,
        "return_date": return_date,
        "purpose": trip_purpose or user_query,
        "budget": budget,
        "mode": mode,
        "created_at": datetime.utcnow().isoformat(),
    }

    # 2) Policy Checker via RAG
    policy_result = check_policy_compliance(trip, POLICY_CHUNKS)

    # 3) Search flights / hotels
    flights = search_flights(origin, destination, depart_date, return_date)
    hotels = search_hotels(destination, depart_date, return_date, budget)

    # 4) Draft "booking" / itinerary
    itinerary_lines = []
    itinerary_lines.append(f"Trip: {origin} → {destination}")
    itinerary_lines.append(f"Dates: {depart_date} → {return_date}")
    itinerary_lines.append(f"Purpose: {trip_purpose or user_query}")
    if budget:
        itinerary_lines.append(f"Budget: ${budget}")

    itinerary_lines.append("\n**Flight options (sampled)**")
    for f in flights[:3]:
        itinerary_lines.append(
            f"- {f['airline']} {f['flight']} | {f['depart_time']} → {f['arrive_time']} | ${f['price']}"
        )

    itinerary_lines.append("\n**Hotel options (sampled)**")
    for h in hotels[:3]:
        itinerary_lines.append(
            f"- {h['name']} | {h['nights']} nights | ${h['total_price']} | {h['location']}"
        )

    # 5) Combine with policy insights
    final_msg = []
    final_msg.append("### ✈️ Travel Plan (Draft)")
    final_msg.append("\n".join(itinerary_lines))
    final_msg.append("\n---\n")
    final_msg.append("### 🛡 Policy Check")
    final_msg.append(f"- Status: **{policy_result['status']}**")
    if policy_result.get("violations"):
        final_msg.append("**Violations / Warnings:**")
        for v in policy_result["violations"]:
            final_msg.append(f"  - {v}")
    if policy_result.get("notes"):
        final_msg.append("\n**Notes:**")
        for n in policy_result["notes"]:
            final_msg.append(f"  - {n}")

    final_msg.append("\n---\n")
    final_msg.append(f"_LLM mode used_: **{mode}**")

    return "\n".join(final_msg)