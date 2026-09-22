from django.conf import settings
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

# 5.3 + 8.1 Prompting
SYSTEM_PROMPT = """
You are ResearchAI, a research assistant for AI engineers.
Help the user think through research questions clearly.
Be concise, structured, and honest about uncertainty.
If context is missing, ask a short clarifying question.
Do not invent citations or sources.
""".strip()

# 8.1 LangChain Basics (models and prompts)
def generate_response(message: str, previous_message: list | None = None) -> str:

    # 1. if key is missing, return error
    if not settings.GEMINI_API_KEY: raise ValueError("GEMINI_API_KEY is missing")

    # 2. treat empty history as an empty list to avoid errors
    previous_message = previous_message or []

    # 3. build langchain message
    # instead manually add model/user message before, we can just use AIMessage/HumanMessage to add directly
    messages = [SystemMessage(content=SYSTEM_PROMPT)]
    for msg in previous_message:
        role = msg["role"]
        content = msg["content"]
        if role == "assistant": messages.append(AIMessage(content=content))
        else: messages.append(HumanMessage(content=content))

    # 4. add current user question
    messages.append(HumanMessage(content=message))

    # 5. create Gemini chat and sent the full message list
    model = ChatGoogleGenerativeAI(
        model=settings.GEMINI_MODEL,
        google_api_key=settings.GEMINI_API_KEY
    )
    response = model.invoke(messages)

    # 6. return the assistant text
    text = (response.text or "").strip()
    if not text: raise ValueError("Empty response from model")

    return text