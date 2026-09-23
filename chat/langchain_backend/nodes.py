from django.conf import settings
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages

from chat.langchain_backend.rag import get_retriever
from chat.langchain_backend.tools import TOOLS

# 9.1 Graph Basics (state)
class GraphState(TypedDict, total=False):
    question: str
    context: str
    messages: Annotated[list, add_messages]
    tool_results: list

# 9.1 Graph Basics (nodes)
# 9.3 Graph Basics (state)
# update all function header from (state: dict) to (state: GraphState)

# search chroma and return relevant chunk text
def retrieve_node(state: GraphState) -> dict:
    docs = get_retriever().invoke(state["question"])
    context = "\n\n".join(
    f"Source: {doc.metadata.get('source', 'unknown')}\n{doc.page_content}"
    for doc in docs
    ) or "No relevant context found."

    return {"context": context}

# ask gemini for next answer or tool call
def model_node(state: GraphState) -> dict:
    model = ChatGoogleGenerativeAI(
        model=settings.GEMINI_MODEL,
        google_api_key=settings.GEMINI_API_KEY,
    )
    response = model.bind_tools(TOOLS).invoke(state["messages"])
    return {"messages": [response]}

# run every tool requested by latest model response (vs create_agent in langchain)
def tool_node(state: GraphState) -> dict:
    tool_calls = state["messages"][-1].tool_calls
    tool_map = {tool.name: tool for tool in TOOLS}
    
    results = []
    for call in tool_calls:
        tool = tool_map[call["name"]]
        result = tool.invoke(call["args"])
        results.append({
            "name": call["name"],
            "result": result
        })

    return {"tool_results": results}
