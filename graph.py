from langgraph.graph import StateGraph, END
from typing import TypedDict

from agents.planner_agent import planner_agent
from agents.budget_agent import budget_agent
from agents.hotel_agent import hotel_agent
from tools.weather import get_weather
from utils.report_generator import generate_report


class TravelState(TypedDict):
    destination: str
    days: int
    budget: str
    travelers: str
    interests: str
    departure: str

    itinerary: str
    budget_plan: str
    hotel_plan: str
    weather: str
    report: str


# ---------------- Planner ----------------

def planner_node(state):

    state["itinerary"] = planner_agent(
        state["destination"],
        state["days"],
        state["interests"]
    )

    return state


# ---------------- Budget ----------------

def budget_node(state):

    state["budget_plan"] = budget_agent(
        state["destination"],
        state["days"],
        state["budget"],
        state["travelers"]
    )

    return state


# ---------------- Hotel ----------------

def hotel_node(state):

    state["hotel_plan"] = hotel_agent(
        state["destination"],
        state["budget"],
        state["travelers"]
    )

    return state


# ---------------- Weather ----------------

def weather_node(state):

    state["weather"] = get_weather(
        state["destination"]
    )

    return state


# ---------------- Report ----------------

def report_node(state):

    state["report"] = generate_report(
        state["itinerary"],
        state["budget_plan"],
        state["hotel_plan"],
        state["weather"]
    )

    return state


builder = StateGraph(TravelState)

builder.add_node("planner", planner_node)
builder.add_node("budget", budget_node)
builder.add_node("hotel", hotel_node)
builder.add_node("weather", weather_node)
builder.add_node("report", report_node)

builder.set_entry_point("planner")

builder.add_edge("planner", "budget")
builder.add_edge("budget", "hotel")
builder.add_edge("hotel", "weather")
builder.add_edge("weather", "report")

builder.add_edge("report", END)

travel_graph = builder.compile()