"""Pinpoint resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class PinpointHandler(ResourceHandler):
    """Handler for Amazon Pinpoint resources."""

    @property
    def service_name(self) -> str:
        return "pinpoint"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all Pinpoint applications."""
        pinpoint = self.session.client("pinpoint")
        resources = []

        try:
            # List applications
            response = pinpoint.get_apps()
            for app in response.get("ApplicationsResponse", {}).get("Item", []):
                resources.append({
                    "id": app["Id"],
                    "name": app.get("Name", app["Id"]),
                    "type": "application",
                    "arn": app["Arn"],
                })

        except ClientError as e:
            self.logger.error(f"Error listing Pinpoint applications: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a Pinpoint application."""
        pinpoint = self.session.client("pinpoint")
        app_id = resource.get("id")

        try:
            pinpoint.delete_app(ApplicationId=app_id)
            return True
        except ClientError as e:
            self.logger.error(
                f"Error deleting Pinpoint application {app_id}: {str(e)}"
            )
            return False
