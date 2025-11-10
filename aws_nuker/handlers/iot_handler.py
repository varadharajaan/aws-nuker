"""Handler for IOT resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class IotHandler(ResourceHandler):
    """Handler for IOT resources."""

    @property
    def service_name(self) -> str:
        return "iot"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all IOT resources."""
        client = self.session.client("iot")
        resources = []

        try:
            paginator = client.get_paginator("list_things")
            for page in paginator.paginate():
                for item in page.get("things", []):
                    resources.append({
                        "id": item.get("thingName", ""),
                        "name": item.get("thingName", ""),
                        "type": "thing",
                    })
        except ClientError as e:
            self.logger.error(f"Error listing IOT resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a IOT resource."""
        client = self.session.client("iot")
        resource_id = resource.get("id")

        try:
            client.delete_thing(thingName=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting IOT resource {resource_id}: {str(e)}")
            return False
