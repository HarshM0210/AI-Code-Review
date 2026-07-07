import os
import time
import json
import re
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import APIError

# ------------------------------------------------------------
# Load .env from project root
# ------------------------------------------------------------
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError(
        f"""
GEMINI_API_KEY not found.

Expected .env file at:
{env_path}

Example:

GEMINI_API_KEY=AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxxxxx
"""
    )

# Create Gemini client
client = genai.Client(api_key=API_KEY)

MODEL = "gemini-2.5-flash"


# ------------------------------------------------------------
# Generate with Retry
# ------------------------------------------------------------
def generate_with_retry(
    prompt: str,
    system_instruction: str = None,
    retries: int = 3,
) -> str:
    """
    Generate content from Gemini with retry and exponential backoff.
    """

    for attempt in range(retries):
        try:
            config = types.GenerateContentConfig(
                temperature=0.1,
                response_mime_type="application/json",
            )

            if system_instruction:
                config.system_instruction = system_instruction

            response = client.models.generate_content(
                model=MODEL,
                contents=prompt,
                config=config,
            )

            if not response.text:
                raise ValueError("Gemini returned an empty response.")

            return response.text

        except APIError as e:
            print(f"Gemini API Error (Attempt {attempt+1}/{retries}): {e}")

            if attempt == retries - 1:
                raise

            time.sleep(2 ** attempt)

        except Exception as e:
            print(f"Unexpected Error (Attempt {attempt+1}/{retries}): {e}")

            if attempt == retries - 1:
                raise

            time.sleep(2 ** attempt)


# ------------------------------------------------------------
# Safe JSON Parsing
# ------------------------------------------------------------
def parse_json_safely(raw_text: str) -> dict:
    """
    Removes markdown wrappers and safely parses JSON.
    """

    if not raw_text:
        return {"error": "Empty response from Gemini"}

    text = raw_text.strip()

    # Remove ```json ... ```
    text = re.sub(r"^```json", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^```", "", text)
    text = re.sub(r"```$", "", text)

    text = text.strip()

    # Extract first JSON object
    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end != -1:
        text = text[start : end + 1]

    try:
        return json.loads(text)

    except json.JSONDecodeError as e:
        return {
            "error": f"JSON Decode Error: {str(e)}",
            "raw_text": raw_text,
        }