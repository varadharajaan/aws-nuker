"""Handler for TRANSLATE resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class TranslateHandler(ResourceHandler):
    """Handler for TRANSLATE resources."""

    @property
    def service_name(self) -> str:
        return "translate"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all TRANSLATE resources."""
        client = self.session.client("translate")
        resources = []

        try:
            response = client.list_terminologies()
            for item in response.get("TerminologyPropertiesList", []):
                resources.append({
                    "id": item.get("Name", ""),
                    "name": item.get("Name", ""),
                    "type": "terminology",
                })
        except ClientError as e:
            self.logger.error(f"Error listing TRANSLATE resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a TRANSLATE resource."""
        client = self.session.client("translate")
        resource_id = resource.get("id")

        try:
            client.delete_terminology(Name=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting TRANSLATE resource {resource_id}: {str(e)}")
            return False
