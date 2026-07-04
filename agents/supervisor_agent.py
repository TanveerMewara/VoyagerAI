# from agents.planner_agent import planner_agent
# from agents.budget_agent import budget_agent
# from agents.hotel_agent import hotel_agent
# from tools.weather import get_weather
# from utils.report_generator import generate_report

# def supervisor_agent(destination,
#                      days,
#                      budget,
#                      travelers,
#                      interests,
#                      departure):

#     itinerary = planner_agent(
#         destination,
#         days,
#         interests
#     )

#     budget_plan = budget_agent(
#         destination,
#         days,
#         budget,
#         travelers
#     )

#     hotel_plan = hotel_agent(
#         destination,
#         budget,
#         travelers
#     )

#     weather = "🌤 TEST WEATHER WORKING"

#     report = generate_report(
#     itinerary,
#     budget_plan,
#     hotel_plan,
#     weather
#     )

#     return report

# #     final_response = f"""
# # # 🌍 Voyager AI Travel Plan

# # ---

# # ## 📅 Itinerary

# # {itinerary}

# # ---

# # ## 💰 Budget Estimate

# # {budget_plan}

# # ---

# # ## 🏨 Hotel Recommendations

# # {hotel_plan}

# # ---

# # ## 🌤 Weather

# # {weather}

# # """

# #     return final_response

from utils.gemini import ask_gemini
from tools.weather import get_weather


def supervisor_agent(
    destination,
    days,
    budget,
    travelers,
    interests,
    departure
):

    weather = get_weather(destination)

    prompt = f"""
You are an expert AI Travel Planner.

Create a complete travel plan using the following details.

Destination: {destination}

Days: {days}

Budget: {budget}

Travelers: {travelers}

Departure City: {departure}

Interests: {interests}

Current Weather:
{weather}

Generate the response in this exact format.

---

# 📅 Itinerary

Provide a day-wise itinerary.

---

# 💰 Budget Breakdown

Estimate expenses for:

- Flights
- Hotel
- Food
- Local Transport
- Activities

Mention Total Cost.

---

# 🏨 Hotel Recommendations

Recommend 3 hotels with:

- Name
- Approximate Price
- Why Recommended

---

# 🌤 Weather

Explain how the weather affects the trip.

---

# 🎒 Travel Tips

Give useful travel tips.
"""

    return ask_gemini(prompt)