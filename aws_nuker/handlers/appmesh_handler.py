"""Handler for APPMESH resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class AppmeshHandler(ResourceHandler):
    """Handler for APPMESH resources."""

    @property
    def service_name(self) -> str:
        return "appmesh"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all APPMESH resources."""
        client = self.session.client("appmesh")
        resources = []

        try:
            paginator = client.get_paginator("list_meshes")
            for page in paginator.paginate():
                for item in page.get("meshes", []):
                    resources.append({
                        "id": item.get("meshName", ""),
                        "name": item.get("meshName", ""),
                        "type": "mesh",
                    })
        except ClientError as e:
            self.logger.error(f"Error listing APPMESH resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a APPMESH resource."""
        client = self.session.client("appmesh")
        resource_id = resource.get("id")

        try:
            client.delete_mesh(meshName=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting APPMESH resource {resource_id}: {str(e)}")
            return False
