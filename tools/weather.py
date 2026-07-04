# import requests

# def get_weather(destination):
#     """
#     Dummy weather function.
#     Later we'll connect a real Weather API.
#     """

#     weather_data = {
#         "Japan": "22°C ☀️ Sunny",
#         "Paris": "18°C 🌤 Partly Cloudy",
#         "Dubai": "38°C ☀️ Hot",
#         "London": "14°C 🌧 Light Rain",
#         "Goa": "31°C 🌦 Humid"
#     }

#     return weather_data.get(destination, "Weather information unavailable.")

import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("WEATHER_API_KEY")


def get_weather(city):

    url = "https://api.openweathermap.org/data/2.5/weather"

    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric"
    }

    try:
        response = requests.get(url, params=params)

        data = response.json()

        if response.status_code != 200:
            return f"❌ Weather not available for {city}"

        temperature = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        weather = data["weather"][0]["description"].title()
        wind = data["wind"]["speed"]

        return f"""
🌡 Temperature : {temperature}°C

☁ Condition : {weather}

💧 Humidity : {humidity}%

🌬 Wind Speed : {wind} m/s
"""

    except Exception:
        return "Unable to fetch weather."