def fetch_maintenance_history(equipment_id: str) -> dict:
    mock_records = {
        "EQ-1001": [
            {
                "issue": "Hydraulic pressure warning",
                "status": "OPEN",
                "priority": "HIGH",
            },
            {
                "issue": "Oil filter replacement",
                "status": "RESOLVED",
                "priority": "LOW",
            },
        ],
        "EQ-1002": [
            {
                "issue": "Scheduled inspection",
                "status": "RESOLVED",
                "priority": "LOW",
            },
        ],
    }

    return {
        "equipment_id": equipment_id,
        "records": mock_records.get(equipment_id, []),
    }