"""Handler for IOTEVENTS resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class IoteventsHandler(ResourceHandler):
    """Handler for IOTEVENTS resources."""

    @property
    def service_name(self) -> str:
        return "iotevents"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all IOTEVENTS resources."""
        client = self.session.client("iotevents")
        resources = []

        try:
            paginator = client.get_paginator("list_detector_models")
            for page in paginator.paginate():
                for item in page.get("detectorModelSummaries", []):
                    resources.append({
                        "id": item.get("detectorModelName", ""),
                        "name": item.get("detectorModelName", ""),
                        "type": "model",
                    })
        except ClientError as e:
            self.logger.error(f"Error listing IOTEVENTS resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a IOTEVENTS resource."""
        client = self.session.client("iotevents")
        resource_id = resource.get("id")

        try:
            client.delete_detector_model(detectorModelName=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting IOTEVENTS resource {resource_id}: {str(e)}")
            return False
