from concurrent.futures import ThreadPoolExecutor

from utils.gemini import ask_gemini
from tools.weather import get_weather


def supervisor_agent(
    destination,
    days,
    budget,
    travelers,
    interests,
    departure,
    on_chunk=None
):
    prompt = f"""
You are an expert travel planner. Return a concise, useful plan immediately.
Destination: {destination}
Days: {days}
Budget: {budget}
Traveler type: {travelers}
Departure city: {departure}
Interests: {interests}

Use exactly these Markdown sections separated by ---:
# Itinerary
For every day, give one short bullet each for morning, afternoon and evening.
Include arrival and departure. Avoid introductions and repeated trip details.
# Budget Breakdown
Give a compact table: return travel, hotel, food, local transport, activities,
contingency and total. Keep arithmetic consistent. Budget {max(0, days - 1)}
hotel nights unless an extra night is explicitly needed. State headcount
assumptions for Family/Friends; the group size is unknown.
# Hotel Recommendations
Give three options with an approximate nightly price and one-line reason.
Prices and availability are estimates, not verified live quotes.
# Travel Tips
Give five short actionable tips, including checking current opening times.
Do not claim to have checked live opening times or ticket prices.
Do not include a weather section or invent current weather readings;
a separate weather tool adds the current observation after your response.
"""
    # Fetch weather in parallel so the first model text does not wait for it.
    with ThreadPoolExecutor(max_workers=1) as executor:
        weather_future = executor.submit(get_weather, destination)
        report = ask_gemini(
            prompt, on_chunk=on_chunk,
            max_output_tokens=min(8192, max(2048, 1024 + days * 180))
        )
        try:
            weather = weather_future.result()
        except Exception:
            weather = "Weather information unavailable."
    report += (
        "\n\n---\n\n# Weather\n\n" + weather
        + "\n\nCurrent conditions only, not a forecast for your travel dates. "
        "Check the forecast before departure; pack layers and rain protection as needed."
    )
    if on_chunk is not None:
        on_chunk(report)
    return report
