"""Handler for APPFLOW resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class AppflowHandler(ResourceHandler):
    """Handler for APPFLOW resources."""

    @property
    def service_name(self) -> str:
        return "appflow"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all APPFLOW resources."""
        client = self.session.client("appflow")
        resources = []

        try:
            response = client.list_flows()
            for item in response.get("flows", []):
                resources.append({
                    "id": item.get("flowName", ""),
                    "name": item.get("flowName", ""),
                    "type": "flow",
                })
        except ClientError as e:
            self.logger.error(f"Error listing APPFLOW resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a APPFLOW resource."""
        client = self.session.client("appflow")
        resource_id = resource.get("id")

        try:
            client.delete_flow(flowName=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting APPFLOW resource {resource_id}: {str(e)}")
            return False
