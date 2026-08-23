import os
import requests
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY not found in .env")


OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

MODEL = "openai/gpt-4o-mini"


def generate_answer(prompt: str) -> str:
    """
    Generate an answer using OpenRouter.

    This keeps the same function name as the old Gemini client,
    so the rest of the agent does not need to change.
    """

    print("[OPENROUTER] Generating answer...")

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
        "temperature": 0.7,
    }

    try:
        response = requests.post(
            OPENROUTER_URL,
            headers=headers,
            json=data,
            timeout=60,
        )

        if response.status_code != 200:
            print("[OPENROUTER] API error:")
            print(response.text)

            return "I couldn't generate an answer right now."

        result = response.json()

        answer = result["choices"][0]["message"]["content"]

        print("[OPENROUTER] Answer generated successfully.")

        return answer.strip()

    except Exception as e:
        print(f"[OPENROUTER] Error: {e}")

        return "I couldn't generate an answer right now."