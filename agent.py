import json
import logging

from fastmcp import Client
from jsonschema import validate

from llm_client import ask_llm
from mcp_servers.equipment_server import mcp as equipment_mcp
from mcp_servers.maintenance_server import mcp as maintenance_mcp


logger = logging.getLogger(__name__)

ALLOWED_TOOLS = {
    "get_maintenance_history",
    "get_equipment_details",
}


async def run_agent(message: str) -> str:
    conversation = [
        {"role": "user", "content": message}
    ]

    async with (
        Client(maintenance_mcp) as maintenance_client,
        Client(equipment_mcp) as equipment_client,
    ):
        tools = []
        clients_by_tool = {}

        # Discover tools and remember which server owns each one.
        for client in (maintenance_client, equipment_client):
            discovered_tools = await client.list_tools()

            for tool in discovered_tools:
                if tool.name not in ALLOWED_TOOLS:
                    continue

                tools.append({
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema,
                })
                clients_by_tool[tool.name] = client

        tools_by_name = {
            tool["name"]: tool for tool in tools
        }

        for _ in range(5):
            result = await ask_llm(
                conversation=conversation,
                tools=tools,
            )

            if not result["tool_calls"]:
                return result["text"]

            conversation.append({
                "role": "assistant",
                "content": result["text"],
                "tool_calls": result["tool_calls"],
            })

            for call in result["tool_calls"]:
                tool_name = call["name"]

                if tool_name not in tools_by_name:
                    raise ValueError("Tool is unavailable or disallowed.")

                validate(
                    instance=call["arguments"],
                    schema=tools_by_name[tool_name]["parameters"],
                )

                logger.info(
                    "Executing tool=%s arguments=%s",
                    tool_name,
                    call["arguments"],
                )

                # Route this call to the client for the correct server.
                client = clients_by_tool[tool_name]

                tool_result = await client.call_tool(
                    name=tool_name,
                    arguments=call["arguments"],
                    timeout=10,
                )

                if tool_result.is_error:
                    raise RuntimeError(f"Tool failed: {tool_name}")

                conversation.append({
                    "role": "tool",
                    "name": tool_name,
                    "tool_call_id": call["id"],
                    "content": json.dumps(
                        tool_result.structured_content
                    ),
                })

    return "Unable to complete the request within the step limit."