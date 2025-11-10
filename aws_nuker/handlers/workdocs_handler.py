"""Handler for WORKDOCS resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class WorkdocsHandler(ResourceHandler):
    """Handler for WORKDOCS resources."""

    @property
    def service_name(self) -> str:
        return "workdocs"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all WORKDOCS resources."""
        client = self.session.client("workdocs")
        resources = []

        try:
            response = client.describe_users()
            for item in response.get("Users", []):
                resources.append({
                    "id": item.get("Id", ""),
                    "name": item.get("Username", ""),
                    "type": "user",
                })
        except ClientError as e:
            self.logger.error(f"Error listing WORKDOCS resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a WORKDOCS resource."""
        client = self.session.client("workdocs")
        resource_id = resource.get("id")

        try:
            client.delete_user(UserId=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting WORKDOCS resource {resource_id}: {str(e)}")
            return False
