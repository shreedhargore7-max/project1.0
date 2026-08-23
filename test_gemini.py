import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

print("API key loaded:", bool(api_key))
print("API key length:", len(api_key) if api_key else 0)

client = genai.Client(
    api_key=api_key
)

response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents="Say hello in one sentence."
)

print("\nGemini response:")
print(response.text)