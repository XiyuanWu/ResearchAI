from datetime import datetime
from typing import Literal
from zoneinfo import ZoneInfo
from langchain_core.tools import tool

# 8.2 Tools and Agents (langChain tools)
# we use @tool so we don't need write FunctionDeclaration manually
@tool
def get_current_time() -> str:
    now = datetime.now(ZoneInfo("America/Los_Angeles"))
    return now.strftime("%Y-%m-%d %H:%M:%S %Z")

@tool
def calculate(a: float, b: float, operation: str) -> float:
    if operation == "add":
        return a + b
    if operation == "subtract":
        return a - b
    if operation == "multiply":
        return a * b
    if operation == "divide":
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b
    raise ValueError(f"Unsupported operation: {operation}")

TOOLS = [get_current_time, calculate]