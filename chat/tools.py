from datetime import datetime
from zoneinfo import ZoneInfo
from google.genai import types

# 6.1 Define Tools
def get_current_time() -> str:
    now = datetime.now(ZoneInfo("America/Los_Angeles"))
    return now.strftime("%Y-%m-%d %H:%M:%S %Z")

# 6.2 Tool Execution (let model decide when to use)
GET_CURRENT_TIME_DECL = types.FunctionDeclaration(
    name="get_current_time",
    description=(
        "Get the current date and time in US Pacific timezone (PST/PDT). "
        "Use this when user asks what time it is now. "
    ),
    parameters={
        "type": "object",
        "properties": {},
        "required": [],
    },
)

# 6.3 Multiple Tools (add multiple tools)
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

CALCULATE_DECL = types.FunctionDeclaration(
    name="calculate",
    description=(
        "Perform an arithmetic calculation. "
        "Use this tool for addition, subtraction, multiplication, or division."
    ),
    parameters={
        "type": "object",
        "properties": {
            "a": {
                "type": "number",
                "description": "The first number.",
            },
            "b": {
                "type": "number",
                "description": "The second number.",
            },
            "operation": {
                "type": "string",
                "enum": ["add", "subtract", "multiply", "divide"],
                "description": "The arithmetic operation to perform.",
            },
        },
        "required": ["a", "b", "operation"],
    },
)

TOOLS = [types.Tool(function_declarations=[GET_CURRENT_TIME_DECL, CALCULATE_DECL])]