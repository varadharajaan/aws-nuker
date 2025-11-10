"""Handler for FRAUDDETECTOR resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class FrauddetectorHandler(ResourceHandler):
    """Handler for FRAUDDETECTOR resources."""

    @property
    def service_name(self) -> str:
        return "frauddetector"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all FRAUDDETECTOR resources."""
        client = self.session.client("frauddetector")
        resources = []

        try:
            response = client.get_detectors()
            for item in response.get("detectors", []):
                resources.append({
                    "id": item.get("detectorId", ""),
                    "name": item.get("detectorId", ""),
                    "type": "detector",
                })
        except ClientError as e:
            self.logger.error(f"Error listing FRAUDDETECTOR resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a FRAUDDETECTOR resource."""
        client = self.session.client("frauddetector")
        resource_id = resource.get("id")

        try:
            client.delete_detector(detectorId=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting FRAUDDETECTOR resource {resource_id}: {str(e)}")
            return False
