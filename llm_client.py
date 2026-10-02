import json
import re
from uuid import uuid4


async def ask_llm(conversation: list[dict], tools: list[dict]) -> dict:
    # After tool execution, combine all results into a final answer.
    if conversation[-1]["role"] == "tool":
        summaries = []

        for message in conversation:
            if message["role"] != "tool":
                continue

            data = json.loads(message["content"])
            equipment_id = data["equipment_id"]

            if message["name"] == "get_equipment_details":
                if not data["found"]:
                    summaries.append(
                        f"No equipment details found for {equipment_id}."
                    )
                    continue

                details = data["details"]
                summaries.append(
                    f"{equipment_id}: {details['model']}, "
                    f"{details['operating_hours']} operating hours, "
                    f"status: {details['status']}."
                )

            elif message["name"] == "get_maintenance_history":
                records = data["records"]

                if not records:
                    summaries.append(
                        f"No maintenance records found for {equipment_id}."
                    )
                    continue

                history = "; ".join(
                    f"{record['issue']} "
                    f"(status: {record['status']}, "
                    f"priority: {record['priority']})"
                    for record in records
                )

                urgent_count = sum(
                    record["status"] == "OPEN"
                    and record["priority"] == "HIGH"
                    for record in records
                )

                summaries.append(
                    f"Maintenance history for {equipment_id}: {history}. "
                    f"Open high-priority issues: {urgent_count}."
                )

        return {
            "text": " ".join(summaries),
            "tool_calls": [],
        }

    # First pass: simulate interpreting the user's request.
    message = conversation[-1]["content"]
    text = message.lower()

    equipment_match = re.search(
        r"\bEQ-\d+\b",
        message,
        re.IGNORECASE,
    )

    if not equipment_match:
        return {
            "text": "Please include an equipment ID, such as EQ-1001.",
            "tool_calls": [],
        }

    equipment_id = equipment_match.group(0).upper()

    wants_overview = any(
        phrase in text
        for phrase in ("tell me about", "overview", "everything", "both")
    )

    wants_equipment = wants_overview or any(
        keyword in text
        for keyword in ("equipment", "model", "hours", "details", "status")
    )

    wants_maintenance = wants_overview or any(
        keyword in text
        for keyword in ("maintenance", "urgent", "issues", "repairs")
    )

    requested_tools = []

    if wants_equipment:
        requested_tools.append("get_equipment_details")

    if wants_maintenance:
        requested_tools.append("get_maintenance_history")

    if not requested_tools:
        return {
            "text": "Ask for equipment details, maintenance history, "
                    "or an overview.",
            "tool_calls": [],
        }

    available_names = {tool["name"] for tool in tools}

    if any(name not in available_names for name in requested_tools):
        return {
            "text": "A required lookup tool is unavailable.",
            "tool_calls": [],
        }

    return {
        "text": None,
        "tool_calls": [
            {
                "id": str(uuid4()),
                "name": name,
                "arguments": {"equipment_id": equipment_id},
            }
            for name in requested_tools
        ],
    }