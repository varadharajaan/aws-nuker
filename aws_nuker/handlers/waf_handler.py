"""Handler for WAF resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class WafHandler(ResourceHandler):
    """Handler for WAF resources."""

    @property
    def service_name(self) -> str:
        return "waf"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all WAF resources."""
        client = self.session.client("waf")
        resources = []

        try:
            response = client.list_web_acls()
            for item in response.get("WebACLs", []):
                resources.append({
                    "id": item.get("WebACLId", ""),
                    "name": item.get("Name", ""),
                    "type": "webacl",
                })
        except ClientError as e:
            self.logger.error(f"Error listing WAF resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a WAF resource."""
        client = self.session.client("waf")
        resource_id = resource.get("id")

        try:
            client.delete_web_acl(WebACLId=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting WAF resource {resource_id}: {str(e)}")
            return False
