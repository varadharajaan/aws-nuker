"""Handler for SWF resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class SwfHandler(ResourceHandler):
    """Handler for SWF resources."""

    @property
    def service_name(self) -> str:
        return "swf"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all SWF resources."""
        client = self.session.client("swf")
        resources = []

        try:
            response = client.list_domains()
            for item in response.get("domainInfos", []):
                resources.append({
                    "id": item.get("name", ""),
                    "name": item.get("name", ""),
                    "type": "domain",
                })
        except ClientError as e:
            self.logger.error(f"Error listing SWF resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a SWF resource."""
        client = self.session.client("swf")
        resource_id = resource.get("id")

        try:
            client.deprecate_domain(name=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting SWF resource {resource_id}: {str(e)}")
            return False
