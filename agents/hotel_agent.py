from utils.gemini import ask_gemini

def hotel_agent(destination, budget, travelers):

    prompt = f"""
    You are a luxury travel consultant.

    Destination:
    {destination}

    Budget:
    {budget}

    Travelers:
    {travelers}

    Recommend:

    - 5 hotels
    - Estimated price
    - Why each hotel is good
    - Nearby attractions

    Keep the answer concise.
    """

    return ask_gemini(prompt)