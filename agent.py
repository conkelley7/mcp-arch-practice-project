
from llm_client import ask_llm

async def run_agent(message: str) -> str:

    conversation = [
        {"role": "user", "content": message}
    ]

    # Discover available MCP tools
    tools = await discover_mcp_tools()

    for _ in range(5):

        # Ask the LLM what to do next
        result = await ask_llm(
            conversation=conversation,
            tools=tools
        )

        if result.has_tool_calls:

            for call in result.tool_calls:

                # Validate permission and arguments
                validate_tool_call(call)

                # Execute using MCP client
                tool_result = await execute_mcp_tool(
                    name=call.name,
                    arguments=call.arguments
                )

                # Return result to the LLM
                conversation.append(
                    make_tool_result_message(
                        call.id,
                        tool_result
                    )
                )

        else:
            return result.text

    return "Unable to complete request."
