# from dotenv import load_dotenv
# import os

# import google.generativeai as genai

# load_dotenv()

# genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# model = genai.GenerativeModel("gemini-2.5-flash")


# def ask_gemini(prompt):
#     response = model.generate_content(prompt)
#     return response.text

# from dotenv import load_dotenv
# import os

# import google.generativeai as genai

# load_dotenv()

# api_key = os.getenv("GOOGLE_API_KEY")

# print("=" * 50)
# print("Loaded API Key:", api_key[:15] + "...")
# print("=" * 50)

# genai.configure(api_key=api_key)

# model = genai.GenerativeModel("gemini-2.5-flash")


# def ask_gemini(prompt):
#     response = model.generate_content(prompt)
#     return response.text

# def ask_followup(previous_plan, user_question):

#     prompt = f"""
# You are Voyager AI.

# Below is the travel plan already generated.

# {previous_plan}

# The user now asks:

# {user_question}

# Answer ONLY the user's new request while keeping the previous travel plan in mind.
# """

#     response = model.generate_content(prompt)

#     return response.text

from dotenv import load_dotenv
import os
import google.generativeai as genai

load_dotenv()

genai.configure(
    api_key=os.getenv("GOOGLE_API_KEY")
)

model = genai.GenerativeModel("gemini-2.5-flash")


# ----------------------------------------
# Generate Complete Travel Plan
# ----------------------------------------

def ask_gemini(prompt):

    response = model.generate_content(prompt)

    return response.text


# ----------------------------------------
# Chat With Existing Travel Plan
# ----------------------------------------

def ask_followup(previous_plan, user_question):

    prompt = f"""
You are Voyager AI.

Here is the travel plan:

{previous_plan}

The user now asks:

{user_question}

Answer only the user's latest question while keeping the existing travel plan in context.
"""

    response = model.generate_content(prompt)

    return response.text