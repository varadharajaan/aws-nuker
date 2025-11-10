"""Handler for APPRUNNER resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class ApprunnerHandler(ResourceHandler):
    """Handler for APPRUNNER resources."""

    @property
    def service_name(self) -> str:
        return "apprunner"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all APPRUNNER resources."""
        client = self.session.client("apprunner")
        resources = []

        try:
            response = client.list_services()
            for item in response.get("ServiceSummaryList", []):
                resources.append({
                    "id": item.get("ServiceArn", ""),
                    "name": item.get("ServiceName", ""),
                    "type": "service",
                })
        except ClientError as e:
            self.logger.error(f"Error listing APPRUNNER resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a APPRUNNER resource."""
        client = self.session.client("apprunner")
        resource_id = resource.get("id")

        try:
            client.delete_service(ServiceArn=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting APPRUNNER resource {resource_id}: {str(e)}")
            return False
