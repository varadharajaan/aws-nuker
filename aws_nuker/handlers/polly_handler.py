"""Handler for POLLY resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class PollyHandler(ResourceHandler):
    """Handler for POLLY resources."""

    @property
    def service_name(self) -> str:
        return "polly"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all POLLY resources."""
        client = self.session.client("polly")
        resources = []

        try:
            response = client.list_lexicons()
            for item in response.get("Lexicons", []):
                resources.append({
                    "id": item.get("Name", ""),
                    "name": item.get("Name", ""),
                    "type": "lexicon",
                })
        except ClientError as e:
            self.logger.error(f"Error listing POLLY resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a POLLY resource."""
        client = self.session.client("polly")
        resource_id = resource.get("id")

        try:
            client.delete_lexicon(Name=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting POLLY resource {resource_id}: {str(e)}")
            return False
