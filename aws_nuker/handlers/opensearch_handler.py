"""Handler for OPENSEARCH resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class OpensearchHandler(ResourceHandler):
    """Handler for OPENSEARCH resources."""

    @property
    def service_name(self) -> str:
        return "opensearch"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all OPENSEARCH resources."""
        client = self.session.client("opensearch")
        resources = []

        try:
            response = client.list_domain_names()
            for item in response.get("DomainNames", []):
                resources.append({
                    "id": item.get("DomainName", ""),
                    "name": item.get("DomainName", ""),
                    "type": "domain",
                })
        except ClientError as e:
            self.logger.error(f"Error listing OPENSEARCH resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a OPENSEARCH resource."""
        client = self.session.client("opensearch")
        resource_id = resource.get("id")

        try:
            client.delete_domain(DomainName=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting OPENSEARCH resource {resource_id}: {str(e)}")
            return False
