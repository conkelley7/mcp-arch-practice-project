import json
import re
from uuid import uuid4


async def ask_llm(conversation: list[dict], tools: list[dict]) -> dict:
    """Mock LLM: request a maintenance tool, then summarize its result."""

    last_message = conversation[-1]

    # Second pass: the agent has supplied the tool result.
    if last_message["role"] == "tool":
        data = json.loads(last_message["content"])

        records = data.get("records", [])
        if not records:
            return {
                "text": f"No maintenance records found for {data['equipment_id']}.",
                "tool_calls": [],
            }

        summary = "; ".join(
            f"{record['issue']} "
            f"(status: {record['status']}, priority: {record['priority']})"
            for record in records
        )

        return {
            "text": f"Maintenance history for {data['equipment_id']}: {summary}.",
            "tool_calls": [],
        }

    # First pass: simulate interpreting the user's request.
    message = last_message["content"]
    equipment_match = re.search(r"\bEQ-\d+\b", message, re.IGNORECASE)

    if "maintenance" not in message.lower():
        return {
            "text": "I can look up maintenance history. Try: "
                    "'Show maintenance history for EQ-1001'.",
            "tool_calls": [],
        }

    if not equipment_match:
        return {
            "text": "Please include an equipment ID, such as EQ-1001.",
            "tool_calls": [],
        }

    tool_name = "get_maintenance_history"
    available_names = {tool["name"] for tool in tools}

    if tool_name not in available_names:
        return {
            "text": "The maintenance lookup tool is unavailable.",
            "tool_calls": [],
        }

    return {
        "text": None,
        "tool_calls": [
            {
                "id": str(uuid4()),
                "name": tool_name,
                "arguments": {
                    "equipment_id": equipment_match.group(0).upper()
                },
            }
        ],
    }