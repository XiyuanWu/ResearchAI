from django.conf import settings
from google import genai

# 4.2 LLM Interaction (sent prompt to model)
# user sent a text to gemini and gemini return a text
def generate_reponse(message: str) -> str:
    if not settings.GEMINI_API_key:
        raise ValueError("GEMINI_API_KEY is missing")

    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    response = client.models.generate_content(
        model = settings.GEMINI_MODEL,
        contents = message,
    )
    text = (response.text or "").strip()
    if not text: raise ValueError("Empty response from model")
    return text