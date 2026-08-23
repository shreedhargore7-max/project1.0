import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")

if not api_key:
    raise ValueError("OPENROUTER_API_KEY not found in .env")

url = "https://openrouter.ai/api/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
}

data = {
    "model": "openai/gpt-4o-mini",
    "messages": [
        {
            "role": "user",
            "content": "Explain machine learning in very simple words."
        }
    ]
}

response = requests.post(
    url,
    headers=headers,
    json=data,
    timeout=60
)

print("STATUS:", response.status_code)

if response.ok:
    result = response.json()

    answer = result["choices"][0]["message"]["content"]

    print("\nOPENROUTER RESPONSE:")
    print(answer)

else:
    print("\nOPENROUTER ERROR:")
    print(response.text)