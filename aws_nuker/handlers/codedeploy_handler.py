"""Handler for CODEDEPLOY resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class CodedeployHandler(ResourceHandler):
    """Handler for CODEDEPLOY resources."""

    @property
    def service_name(self) -> str:
        return "codedeploy"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all CODEDEPLOY resources."""
        client = self.session.client("codedeploy")
        resources = []

        try:
            response = client.list_applications()
            for app_name in response.get("applications", []):
                resources.append({
                    "id": app_name,
                    "name": app_name,
                    "type": "application",
                })
        except ClientError as e:
            self.logger.error(f"Error listing CODEDEPLOY resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a CODEDEPLOY resource."""
        client = self.session.client("codedeploy")
        resource_id = resource.get("id")

        try:
            client.delete_application(applicationName=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting CODEDEPLOY resource {resource_id}: {str(e)}")
            return False
