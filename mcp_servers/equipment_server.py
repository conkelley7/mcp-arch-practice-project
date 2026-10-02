from fastmcp import FastMCP

from services.equipment import fetch_equipment_details


mcp = FastMCP("equipment-service")


@mcp.tool()
def get_equipment_details(equipment_id: str) -> dict:
    """Retrieve an equipment item's model, operating hours, and status."""
    return fetch_equipment_details(equipment_id)


if __name__ == "__main__":
    mcp.run()