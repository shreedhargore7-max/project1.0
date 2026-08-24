# ============================================================
# OPENROUTER CLIENT
# ============================================================

import os
from dotenv import load_dotenv
from openai import OpenAI


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv(
    os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        ".env"
    )
)


# ============================================================
# CONFIGURATION
# ============================================================

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    raise ValueError(
        "OPENROUTER_API_KEY not found in app/.env"
    )


# ============================================================
# OPENROUTER CLIENT
# ============================================================

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)


# ============================================================
# FREE MODEL
# ============================================================

MODEL = "openrouter/free"


# ============================================================
# GENERATE ANSWER
# ============================================================

def generate_answer(
    prompt: str,
    max_tokens: int = 2048
) -> str:

    print("[OPENROUTER] Generating answer...")
    print(f"[OPENROUTER] Model: {MODEL}")
    print(f"[OPENROUTER] Max tokens: {max_tokens}")

    try:

        response = client.chat.completions.create(
            model=MODEL,

            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            max_tokens=max_tokens,

            temperature=0.7,
        )

        if not response.choices:
            return "No answer was generated."

        answer = response.choices[0].message.content

        if not answer:
            return "No answer was generated."

        print("[OPENROUTER] Answer generated successfully.")

        return answer.strip()

    except Exception as e:

        print("[OPENROUTER] API error:")
        print(str(e))

        return (
            "I couldn't generate the answer because "
            f"the AI service returned an error: {e}"
        )