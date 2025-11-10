"""Handler for CLOUDMAP resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class CloudmapHandler(ResourceHandler):
    """Handler for CLOUDMAP resources."""

    @property
    def service_name(self) -> str:
        return "cloudmap"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all CLOUDMAP resources."""
        client = self.session.client("servicediscovery")
        resources = []

        try:
            paginator = client.get_paginator("list_namespaces")
            for page in paginator.paginate():
                for item in page.get("Namespaces", []):
                    resources.append({
                        "id": item.get("Id", ""),
                        "name": item.get("Name", ""),
                        "type": "namespace",
                    })
        except ClientError as e:
            self.logger.error(f"Error listing CLOUDMAP resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a CLOUDMAP resource."""
        client = self.session.client("servicediscovery")
        resource_id = resource.get("id")

        try:
            client.delete_namespace(Id=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting CLOUDMAP resource {resource_id}: {str(e)}")
            return False
