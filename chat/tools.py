from datetime import datetime
from zoneinfo import ZoneInfo

# 6.1 Define Tools
def get_current_time() -> str:
    now = datetime.now(ZoneInfo("America/Los_Angeles"))
    return now.strftime("%Y-%m-%d %H:%M:%S %Z")

