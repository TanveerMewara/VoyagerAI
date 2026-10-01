from functools import lru_cache
import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai import errors, types

load_dotenv()

MODEL_NAME = "gemini-2.5-flash"


@lru_cache(maxsize=1)
def get_client():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("Set GOOGLE_API_KEY before generating a travel plan.")
    return genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(
            timeout=60000,
            retry_options=types.HttpRetryOptions(attempts=1)
        )
    )


def ask_gemini(prompt, on_chunk=None, max_output_tokens=8192):
    config = types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(thinking_budget=0),
        max_output_tokens=max_output_tokens
    )
    client = get_client()
    for attempt in range(3):
        parts = []
        try:
            if on_chunk is None:
                response = client.models.generate_content(
                    model=MODEL_NAME, contents=prompt, config=config
                )
                if not response.text:
                    raise RuntimeError("The model returned no text. Please try again.")
                return response.text

            for chunk in client.models.generate_content_stream(
                model=MODEL_NAME, contents=prompt, config=config
            ):
                if chunk.text:
                    parts.append(chunk.text)
                    on_chunk("".join(parts))
            if not parts:
                raise RuntimeError("The model returned no text. Please try again.")
            return "".join(parts)
        except errors.APIError as error:
            if error.code != 503:
                raise
            # Only restart a request if no text has reached the user yet.
            if parts:
                raise RuntimeError(
                    "Gemini became busy and interrupted this response. Please try again."
                ) from error
            if attempt == 2:
                raise RuntimeError(
                    "Gemini is temporarily busy. Please try again in a moment."
                ) from error
            time.sleep(0.5 * (2 ** attempt))


def ask_followup(previous_plan, user_question, on_chunk=None):
    prompt = f"""
You are Voyager AI. Answer the latest question directly using the existing plan.
Be concise unless the user requests detail. Do not repeat the entire plan.
State uncertainty about live prices or availability.

Existing travel plan:
{previous_plan}

User question:
{user_question}
"""
    return ask_gemini(prompt, on_chunk=on_chunk, max_output_tokens=2048)
