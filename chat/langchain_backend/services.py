from django.conf import settings
from langchain.agents import create_agent
from langchain_core.messages import AIMessage, HumanMessage
# from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import START, END, StateGraph
from langchain_google_genai import ChatGoogleGenerativeAI

from chat.langchain_backend.tools import TOOLS
from chat.langchain_backend.rag import get_retriever
from chat.langchain_backend.nodes import GraphState, model_node, retrieve_node, tool_node

# 5.3 + 8.1 Prompting
SYSTEM_PROMPT = """
You are ResearchAI, a research assistant for AI engineers.
Help the user think through research questions clearly.
Be concise, structured, and honest about uncertainty.
If context is missing, ask a short clarifying question.
Do not invent citations or sources.
""".strip()

# 8.3 RAG with LangChain (rag chain)
def generate_response(message: str, previous_message: list | None = None) -> str:

    # 1. if key is missing, return error
    if not settings.GEMINI_API_KEY: raise ValueError("GEMINI_API_KEY is missing")

    # 2. treat empty history as an empty list to avoid errors
    previous_message = previous_message or []

    # 3. convert history into LangChain message
    # instead manually add model/user message before, we can just use AIMessage/HumanMessage to add directly
    history = []
    for msg in previous_message:
        role = msg["role"]
        content = msg["content"]
        if role == "assistant": history.append(AIMessage(content=content))
        else: history.append(HumanMessage(content=content))

    # 5. create Gemini chat and sent the full message list
    model = ChatGoogleGenerativeAI(
        model=settings.GEMINI_MODEL,
        google_api_key=settings.GEMINI_API_KEY
    )

    # 6. create a agent
    # create_agent combine models, tools, system prompts
    agent = create_agent(
        model=model,
        tools=TOOLS,
        system_prompt=SYSTEM_PROMPT
    )
    
    # 7. connect stored chunks and the user question
    docs = get_retriever().invoke(message)
    context = "\n\n".join(
        f"Source: {doc.metadata.get('source', 'unknown')}\n{doc.page_content}"
        for doc in docs
    ) or "No relevant context found."

    # combine chunk text and user question as rag message
    rag_message = f"""
    Use the retrieved context only if it is relevant.
    If it is not relevant, answer normally and do not mention it.

    RETRIEVED CONTEXT:
    {context}

    USER QUESTION:
    {message}
    """.strip()

    # agent answer based on rag message and save to result
    result = agent.invoke({
        "messages": [*history, HumanMessage(content=rag_message)],
    })

    # final message that return to frontend, display to user
    final_message = result["messages"][-1]
    text = (final_message.text or "").strip()
    if not text:
        raise ValueError("Empty response from model")
    return text

# 9.2 Agent Workflow (stop condition)
MAX_TOOL_ROUNDS = 5

def route_after_model(state: GraphState) -> str:
    last = state["messages"][-1]
    if not last.tool_calls: return END
    if state.get("tool_rounds", 0) >= MAX_TOOL_ROUNDS:
        raise ValueError("Agent exceeded maximum tool rounds")
    return "tools"

# # 9.2 Agent Workflow (branching)
# def route_after_model(state: GraphState) -> str:
#     last = state["messages"][-1]
#     if last.tool_calls: return "tools"
#     return END

graph = StateGraph(GraphState)
graph.add_node("retrieve", retrieve_node)
graph.add_node("model", model_node)
graph.add_node("tools", tool_node)
graph.add_edge(START, "retrieve")
graph.add_edge("retrieve", "model")
graph.add_conditional_edges("model", route_after_model)
graph.add_edge("tools", "model")


# # 9.1 Graph Basics (edges)
# graph = StateGraph(GraphState)
# graph.add_node("retrieve", retrieve_node)
# graph.add_node("model", model_node)
# graph.add_edge(START, "retrieve")
# graph.add_edge("retrieve", "model")

# # 8.2 Tools and Agents (langChain agents)
# def generate_response(message: str, previous_message: list | None = None) -> str:

#     # 1. if key is missing, return error
#     if not settings.GEMINI_API_KEY: raise ValueError("GEMINI_API_KEY is missing")

#     # 2. treat empty history as an empty list to avoid errors
#     previous_message = previous_message or []

#     # 3. convert history into LangChain message
#     # instead manually add model/user message before, we can just use AIMessage/HumanMessage to add directly
#     history = []
#     for msg in previous_message:
#         role = msg["role"]
#         content = msg["content"]
#         if role == "assistant": history.append(AIMessage(content=content))
#         else: history.append(HumanMessage(content=content))

#     # 5. create Gemini chat and sent the full message list
#     model = ChatGoogleGenerativeAI(
#         model=settings.GEMINI_MODEL,
#         google_api_key=settings.GEMINI_API_KEY
#     )

#     # 6. create a agent
#     # create_agent combine models, tools, system prompts
#     agent = create_agent(
#         model=model,
#         tools=TOOLS,
#         system_prompt=SYSTEM_PROMPT
#     )
    
#     # invoke is run the loop
#     result = agent.invoke({
#         "messages": [*history, HumanMessage(content=message)]
#     })
#     final_message = result["messages"][-1]    # get last response/message
#     text = (final_message.text or "").strip()
#     if not text: raise ValueError("Empty response from model")

#     return text

# # 8.1 LangChain Basics (chains)
# def generate_response(message: str, previous_message: list | None = None) -> str:

#     # 1. if key is missing, return error
#     if not settings.GEMINI_API_KEY: raise ValueError("GEMINI_API_KEY is missing")

#     # 2. treat empty history as an empty list to avoid errors
#     previous_message = previous_message or []

#     # 3. convert history into LangChain message
#     # instead manually add model/user message before, we can just use AIMessage/HumanMessage to add directly
#     history = []
#     for msg in previous_message:
#         role = msg["role"]
#         content = msg["content"]
#         if role == "assistant": history.append(AIMessage(content=content))
#         else: history.append(HumanMessage(content=content))

#     # 4. prompt: system instruction/prompts + history + user current question
#     prompt = ChatPromptTemplate([
#         ("system", SYSTEM_PROMPT),
#         MessagesPlaceholder("history"),
#         ("human", "{message}")
#     ])

#     # 5. create Gemini chat and sent the full message list
#     model = ChatGoogleGenerativeAI(
#         model=settings.GEMINI_MODEL,
#         google_api_key=settings.GEMINI_API_KEY
#     )
    
#     # 6. chain: prompt -> model -> plain text
#     chain = prompt | model | StrOutputParser()
#     text = chain.invoke({
#         "history": history,
#         "message": message
#     }).strip()
#     if not text: raise ValueError("Empty response from model")

#     return text

# # 8.1 LangChain Basics (models and prompts)
# def generate_response(message: str, previous_message: list | None = None) -> str:

#     # 1. if key is missing, return error
#     if not settings.GEMINI_API_KEY: raise ValueError("GEMINI_API_KEY is missing")

#     # 2. treat empty history as an empty list to avoid errors
#     previous_message = previous_message or []

#     # 3. build langchain message
#     # instead manually add model/user message before, we can just use AIMessage/HumanMessage to add directly
#     messages = [SystemMessage(content=SYSTEM_PROMPT)]
#     for msg in previous_message:
#         role = msg["role"]
#         content = msg["content"]
#         if role == "assistant": messages.append(AIMessage(content=content))
#         else: messages.append(HumanMessage(content=content))

#     # 4. add current user question
#     messages.append(HumanMessage(content=message))

#     # 5. create Gemini chat and sent the full message list
#     model = ChatGoogleGenerativeAI(
#         model=settings.GEMINI_MODEL,
#         google_api_key=settings.GEMINI_API_KEY
#     )
#     response = model.invoke(messages)

#     # 6. return the assistant text
#     text = (response.text or "").strip()
#     if not text: raise ValueError("Empty response from model")

#     return text