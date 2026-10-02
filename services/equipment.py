def fetch_equipment_details(equipment_id: str) -> dict:
    mock_equipment = {
        "EQ-1001": {
            "model": "Bobcat S650",
            "operating_hours": 1250,
            "status": "NEEDS_ATTENTION",
        },
        "EQ-1002": {
            "model": "Bobcat E35",
            "operating_hours": 680,
            "status": "ACTIVE",
        },
    }

    equipment = mock_equipment.get(equipment_id)

    return {
        "equipment_id": equipment_id,
        "found": equipment is not None,
        "details": equipment,
    }