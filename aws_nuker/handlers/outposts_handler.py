"""Handler for OUTPOSTS resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class OutpostsHandler(ResourceHandler):
    """Handler for OUTPOSTS resources."""

    @property
    def service_name(self) -> str:
        return "outposts"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all OUTPOSTS resources."""
        client = self.session.client("outposts")
        resources = []

        try:
            response = client.list_outposts()
            for item in response.get("Outposts", []):
                resources.append({
                    "id": item.get("OutpostId", ""),
                    "name": item.get("OutpostId", ""),
                    "type": "outpost",
                })
        except ClientError as e:
            self.logger.error(f"Error listing OUTPOSTS resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a OUTPOSTS resource."""
        client = self.session.client("outposts")
        resource_id = resource.get("id")

        try:
            client.delete_outpost(OutpostId=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting OUTPOSTS resource {resource_id}: {str(e)}")
            return False
