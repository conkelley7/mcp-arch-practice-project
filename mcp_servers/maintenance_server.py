
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("maintenance-service")


@mcp.tool()
def get_maintenance_history(equipment_id: str) -> dict:
    """
    Retrieve maintenance history for a given equipment ID.
    """

    """
    Mocks an external API call / response

    In real system, would look something like:

    async def fetch_maintenance(equipment_id: str):
    response = await internal_client.get(
        f"/maintenance/{equipment_id}"
    )

    response.raise_for_status()
    return response.json()
    """
    return {
        "equipment_id": equipment_id,
        "records": [
            {
                "issue": "Hydraulic pressure warning",
                "status": "OPEN",
                "priority": "HIGH"
            },
            {
                "issue": "Oil filter replacement",
                "status": "RESOLVED",
                "priority": "LOW"
            }
        ]
    }


if __name__ == "__main__":
    mcp.run()
