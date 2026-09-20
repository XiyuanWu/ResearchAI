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

TOOLS = [types.Tool(function_declarations=[GET_CURRENT_TIME_DECL])]