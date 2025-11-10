"""Handler for EFS resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class EfsHandler(ResourceHandler):
    """Handler for EFS resources."""

    @property
    def service_name(self) -> str:
        return "efs"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all EFS resources."""
        client = self.session.client("efs")
        resources = []

        try:
            paginator = client.get_paginator("describe_file_systems")
            for page in paginator.paginate():
                for item in page.get("FileSystems", []):
                    resources.append({
                        "id": item.get("FileSystemId", ""),
                        "name": item.get("Name", ""),
                        "type": "file_system",
                    })
        except ClientError as e:
            self.logger.error(f"Error listing EFS resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a EFS resource."""
        client = self.session.client("efs")
        resource_id = resource.get("id")

        try:
            client.delete_file_system(FileSystemId=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting EFS resource {resource_id}: {str(e)}")
            return False
