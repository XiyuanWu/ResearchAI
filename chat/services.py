from django.conf import settings
from google import genai
from google.genai import types

# 5.3 Prompting
SYSTEM_PROMPT = """
You are ResearchAI, a research assistant for AI engineers.
Help the user think through research questions clearly.
Be concise, structured, and honest about uncertainty.
If context is missing, ask a short clarifying question.
Do not invent citations or sources.
""".strip()

# 5.2 Conversation Memory (add conversation context)
def generate_response(message: str, previous_message: list | None = None) -> str:

    # 1. if key not exists, return error
    if not settings.GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is missing")

    # 2. treat empty history as an empty list to avoid errors
    previous_message = previous_message or []

    # 3.1 convert history to model's(gemini) format
    contents = []
    for msg in previous_message:
        role = msg["role"]
        if role == "assistant": role = "model"
        contents.append({
            "role": role,
            "parts": [{"text": msg["content"]}]
        })

    # 3.2 add current user message
    contents.append({
        "role": "user",
        "parts": [{"text": message}]
    })

    # 4. call model(gemini) and pass in all contents
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    response = client.models.generate_content(
        model = settings.GEMINI_MODEL,
        contents = contents,
        config = types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT) # pass in prompt
    )

    # 5. get text and check response
    text = (response.text or "").strip()
    if not text: 
        raise ValueError("Empty response from model")

    return text


# # 4.2 LLM Interaction (sent prompt to model)
# # user sent a text to gemini and gemini return a text
# def generate_response(message: str) -> str:
#     if not settings.GEMINI_API_KEY:
#         raise ValueError("GEMINI_API_KEY is missing")

#     client = genai.Client(api_key=settings.GEMINI_API_KEY)
#     response = client.models.generate_content(
#         model = settings.GEMINI_MODEL,
#         contents = message,
#     )
#     text = (response.text or "").strip()
#     if not text: raise ValueError("Empty response from model")
#     return text