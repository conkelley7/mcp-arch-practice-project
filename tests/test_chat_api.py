from fastapi.testclient import TestClient

from main import app

import controllers.chat_controller as chat_controller

client = TestClient(app)

def test_chat_combines_equipment_and_maintenance_results():
    response = client.post(
        "/api/agent/chat",
        json = {
            "message": "What can you tell me about EQ-1001 and does it have any urgent maintenance issues?"
        },
    )

    assert response.status_code == 200

    answer = response.json()["response"]

    assert "Bobcat S650" in answer
    assert "Hydraulic pressure warning" in answer
    assert "Open high-priority issues: 1" in answer


def test_chat_returns_generic_502_when_agent_fails(monkeypatch):
    async def fail_run_agent(message):
        raise RuntimeError("internal failure details")

    monkeypatch.setattr(chat_controller, "run_agent", fail_run_agent)

    response = client.post(
        "/api/agent/chat",
        json={"message": "Look up EQ-1001"},
    )

    assert response.status_code == 502
    assert response.json() == {
        "detail": "The agent could not complete the request."
    }
    assert "internal failure details" not in response.text