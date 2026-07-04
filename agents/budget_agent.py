from utils.gemini import ask_gemini

def budget_agent(destination, days, budget, travelers):
    prompt = f"""
    You are an expert travel budget planner.

    Destination: {destination}
    Days: {days}
    Budget: {budget}
    Travelers: {travelers}

    Give:

    1. Estimated Flight Cost
    2. Hotel Cost
    3. Food Cost
    4. Local Transport
    5. Shopping
    6. Emergency Fund
    7. Total Estimated Expense

    Keep the response concise.
    """

    return ask_gemini(prompt)