"""Handler for WORKSPACES resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class WorkspacesHandler(ResourceHandler):
    """Handler for WORKSPACES resources."""

    @property
    def service_name(self) -> str:
        return "workspaces"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all WORKSPACES resources."""
        client = self.session.client("workspaces")
        resources = []

        try:
            response = client.describe_workspaces()
            for item in response.get("Workspaces", []):
                resources.append({
                    "id": item.get("WorkspaceId", ""),
                    "name": item.get("WorkspaceId", ""),
                    "type": "workspace",
                })
        except ClientError as e:
            self.logger.error(f"Error listing WORKSPACES resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a WORKSPACES resource."""
        client = self.session.client("workspaces")
        resource_id = resource.get("id")

        try:
            client.terminate_workspaces(WorkspaceId=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting WORKSPACES resource {resource_id}: {str(e)}")
            return False
