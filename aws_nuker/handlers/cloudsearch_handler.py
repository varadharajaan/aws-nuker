"""Handler for CLOUDSEARCH resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class CloudsearchHandler(ResourceHandler):
    """Handler for CLOUDSEARCH resources."""

    @property
    def service_name(self) -> str:
        return "cloudsearch"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all CLOUDSEARCH resources."""
        client = self.session.client("cloudsearch")
        resources = []

        try:
            response = client.describe_domains()
            for item in response.get("DomainStatusList", []):
                resources.append({
                    "id": item.get("DomainName", ""),
                    "name": item.get("DomainName", ""),
                    "type": "domain",
                })
        except ClientError as e:
            self.logger.error(f"Error listing CLOUDSEARCH resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a CLOUDSEARCH resource."""
        client = self.session.client("cloudsearch")
        resource_id = resource.get("id")

        try:
            client.delete_domain(DomainName=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting CLOUDSEARCH resource {resource_id}: {str(e)}")
            return False
