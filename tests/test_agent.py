import asyncio

import pytest
from jsonschema.exceptions import ValidationError

import agent


def set_tool_call(monkeypatch, name, arguments):
    async def fake_ask_llm(*, conversation, tools):
        return {
            "text": None,
            "tool_calls": [
                {
                    "id": "test-call",
                    "name": name,
                    "arguments": arguments,
                }
            ],
        }

    monkeypatch.setattr(agent, "ask_llm", fake_ask_llm)


def test_agent_rejects_disallowed_tool(monkeypatch):
    set_tool_call(
        monkeypatch,
        name="delete_equipment",
        arguments={"equipment_id": "EQ-1001"},
    )

    with pytest.raises(ValueError, match="unavailable or disallowed"):
        asyncio.run(agent.run_agent("Look up EQ-1001"))


def test_agent_rejects_invalid_tool_arguments(monkeypatch):
    set_tool_call(
        monkeypatch,
        name="get_equipment_details",
        arguments={},
    )

    with pytest.raises(ValidationError):
        asyncio.run(agent.run_agent("Look up EQ-1001"))