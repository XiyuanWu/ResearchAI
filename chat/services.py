from django.conf import settings
from google import genai
from google.genai import types

from chat.tools import TOOLS, get_current_time
from chat.retrieval import retrieve_relevant_chunks

# 5.3 Prompting
SYSTEM_PROMPT = """
You are ResearchAI, a research assistant for AI engineers.
Help the user think through research questions clearly.
Be concise, structured, and honest about uncertainty.
If context is missing, ask a short clarifying question.
Do not invent citations or sources.
""".strip()

# 7.3 Retrieval & Answering (Answer using retrieved data)
def build_rag_message(message: str, top_k: int = 3) -> str:
    relevant_chunks = retrieve_relevant_chunks(message, top_k=top_k)
    # if no retrieve message, return regular chat mode
    if not relevant_chunks: return message

    context_parts = []
    for number, chunk in enumerate(relevant_chunks, start=1):
        metadata = chunk["metadata"]
        source = metadata.get("chunk_index", "unknown")
        chunk_index = metadata.get("chunk_index", "unknown")

        context_parts.append(
            f"[Context] {number}\n"
            f"Source: {source}\n"
            f"Chunk: {chunk_index}\n"
            f"{chunk["text"]}"
        )

    context = "\n\n".join(context_parts)

    return f"""
        Use the retrieved context below ONLY if it is relevant to the question.
        If it is not relevant, just answer normally and do NOT mention the context.
        Do not invent information or sources.
        RETRIEVED CONTEXT:
        {context}
        USER QUESTION:
        {message}
        """.strip()

# 6.2 Tool Execution (return tool result to model)
def generate_response(message: str, previous_message: list | None = None) -> str:

    # 1. if key not exists, return error
    if not settings.GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is missing")

    # 2. treat empty history as an empty list to avoid errors
    previous_message = previous_message or []

    # 3. build contents for model and user message
    contents = []
    for msg in previous_message:
        role = msg["role"]
        if role == "assistant": role = "model"
        contents.append({
            "role": role,
            "parts": [{"text": msg["content"]}]
        })

    rag_message = build_rag_message(message)
    contents.append({
        "role": "user",
        "parts": [{"text": rag_message}]
    })

    # 4.1 first api call - model return text OR a function call
    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        tools=TOOLS,
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
    ) 
        
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    response = client.models.generate_content(
        model = settings.GEMINI_MODEL,
        contents = contents,
        config = config
    )

    # 4.2. if no tool needed, normal answer
    if not response.function_calls:
        text = (response.text or "").strip()
        if not text:
            raise ValueError("Empty response from model")
        return text

    # 5.1 otherwise run the tool
    fc = response.function_calls[0]
    if fc.name == "get_current_time":
        tool_result = get_current_time()
    else:
        tool_result = f"Unknown tool: {fc.name}"

    # 5.2. append the tool result to contents
    contents.append(response.candidates[0].content)
    contents.append(types.Content(
        role="user",
        parts = [
            types.Part.from_function_response(name=fc.name, response={"result": tool_result})
        ]
    ))

    # 6. second api call - give back contents to model and model write as natural language answer
    final = client.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=contents,
        config=config,
    )

    text = (final.text or "").strip()
    if not text: 
        raise ValueError("Empty response from model")

    return text


# # 5.2 Conversation Memory (add conversation context)
# def generate_response(message: str, previous_message: list | None = None) -> str:

#     # 1. if key not exists, return error
#     if not settings.GEMINI_API_KEY:
#         raise ValueError("GEMINI_API_KEY is missing")

#     # 2. treat empty history as an empty list to avoid errors
#     previous_message = previous_message or []

#     # 3.1 convert history to model's(gemini) format
#     contents = []
#     for msg in previous_message:
#         role = msg["role"]
#         if role == "assistant": role = "model"
#         contents.append({
#             "role": role,
#             "parts": [{"text": msg["content"]}]
#         })

#     # 3.2 add current user message
#     contents.append({
#         "role": "user",
#         "parts": [{"text": message}]
#     })

#     # 4. call model(gemini) and pass in all contents
#     client = genai.Client(api_key=settings.GEMINI_API_KEY)
#     response = client.models.generate_content(
#         model = settings.GEMINI_MODEL,
#         contents = contents,
#         config = types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT) # pass in prompt
#     )

#     # 5. get text and check response
#     text = (response.text or "").strip()
#     if not text: 
#         raise ValueError("Empty response from model")

#     return text


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