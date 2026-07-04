from utils.gemini import ask_gemini

def planner_agent(destination, days, interests):
    prompt = f"""
    You are an expert travel planner.

    Create a detailed {days}-day itinerary for {destination}.

    User Interests:
    {interests}

    Instructions:
    - Give each day a title.
    - Morning activities.
    - Afternoon activities.
    - Evening activities.
    - Keep it realistic.
    - Make it enjoyable.

    Return only the itinerary.
    """

    return ask_gemini(prompt)