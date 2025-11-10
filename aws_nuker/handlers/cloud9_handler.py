"""Handler for CLOUD9 resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class Cloud9Handler(ResourceHandler):
    """Handler for CLOUD9 resources."""

    @property
    def service_name(self) -> str:
        return "cloud9"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all CLOUD9 resources."""
        client = self.session.client("cloud9")
        resources = []

        try:
            response = client.list_environments()
            for item in response.get("environmentIds", []):
                resources.append({
                    "id": item.get("", ""),
                    "name": item.get("", ""),
                    "type": "environment",
                })
        except ClientError as e:
            self.logger.error(f"Error listing CLOUD9 resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a CLOUD9 resource."""
        client = self.session.client("cloud9")
        resource_id = resource.get("id")

        try:
            client.delete_environment(environmentId=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting CLOUD9 resource {resource_id}: {str(e)}")
            return False
