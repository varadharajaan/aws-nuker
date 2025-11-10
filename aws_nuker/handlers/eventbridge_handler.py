"""Handler for EVENTBRIDGE resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class EventbridgeHandler(ResourceHandler):
    """Handler for EVENTBRIDGE resources."""

    @property
    def service_name(self) -> str:
        return "eventbridge"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all EVENTBRIDGE resources."""
        client = self.session.client("events")
        resources = []

        try:
            response = client.list_event_buses()
            for item in response.get("EventBuses", []):
                resources.append({
                    "id": item.get("Name", ""),
                    "name": item.get("Name", ""),
                    "type": "event_bus",
                })
        except ClientError as e:
            self.logger.error(f"Error listing EVENTBRIDGE resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a EVENTBRIDGE resource."""
        client = self.session.client("events")
        resource_id = resource.get("id")

        try:
            client.delete_event_bus(Name=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting EVENTBRIDGE resource {resource_id}: {str(e)}")
            return False
