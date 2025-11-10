"""Handler for WAFV2 resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class Wafv2Handler(ResourceHandler):
    """Handler for WAFV2 resources."""

    @property
    def service_name(self) -> str:
        return "wafv2"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all WAFV2 resources."""
        client = self.session.client("wafv2")
        resources = []

        try:
            response = client.list_web_acls()
            for item in response.get("WebACLs", []):
                resources.append({
                    "id": item.get("Id", ""),
                    "name": item.get("Name", ""),
                    "type": "webacl",
                })
        except ClientError as e:
            self.logger.error(f"Error listing WAFV2 resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a WAFV2 resource."""
        client = self.session.client("wafv2")
        resource_id = resource.get("id")

        try:
            client.delete_web_acl(Id=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting WAFV2 resource {resource_id}: {str(e)}")
            return False
