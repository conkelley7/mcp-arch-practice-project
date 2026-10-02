from fastmcp import FastMCP

from services.maintenance import fetch_maintenance_history


mcp = FastMCP("maintenance-service")


@mcp.tool()
def get_maintenance_history(equipment_id: str) -> dict:
    """Retrieve maintenance records, including issue status and priority."""
    return fetch_maintenance_history(equipment_id)


if __name__ == "__main__":
    mcp.run()