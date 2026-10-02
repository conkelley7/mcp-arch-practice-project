import json
import logging

from fastmcp import Client
from jsonschema import validate

from llm_client import ask_llm
from mcp_servers.maintenance_server import mcp


logger = logging.getLogger(__name__)

# Demo policy: the agent may execute only this read-only tool.
ALLOWED_TOOLS = {"get_maintenance_history"}


async def run_agent(message: str) -> str:
    conversation = [
        {"role": "user", "content": message}
    ]

    # Real MCP connection using an in-memory transport.
    async with Client(mcp) as client:
        discovered_tools = await client.list_tools()

        tools = [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.inputSchema,
            }
            for tool in discovered_tools
            if tool.name in ALLOWED_TOOLS
        ]

        tools_by_name = {tool["name"]: tool for tool in tools}

        # Bound the loop so repeated tool requests cannot run forever.
        for _ in range(5):
            result = await ask_llm(
                conversation=conversation,
                tools=tools,
            )

            if not result["tool_calls"]:
                return result["text"]

            # Preserve the assistant's tool request in the conversation.
            conversation.append({
                "role": "assistant",
                "content": result["text"],
                "tool_calls": result["tool_calls"],
            })

            for call in result["tool_calls"]:
                if call["name"] not in tools_by_name:
                    raise ValueError("Tool is unavailable or disallowed.")

                # Validate arguments against the schema discovered via MCP.
                validate(
                    instance=call["arguments"],
                    schema=tools_by_name[call["name"]]["parameters"],
                )

                logger.info(
                    "Executing tool=%s arguments=%s",
                    call["name"],
                    call["arguments"],
                )

                tool_result = await client.call_tool(
                    name=call["name"],
                    arguments=call["arguments"],
                    timeout=10,
                )

                conversation.append({
                    "role": "tool",
                    "tool_call_id": call["id"],
                    "content": json.dumps(
                        tool_result.structured_content
                    ),
                })

    return "Unable to complete the request within the step limit."