"""Handler for XRAY resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class XrayHandler(ResourceHandler):
    """Handler for XRAY resources."""

    @property
    def service_name(self) -> str:
        return "xray"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all XRAY resources."""
        client = self.session.client("xray")
        resources = []

        try:
            paginator = client.get_paginator("get_groups")
            for page in paginator.paginate():
                for item in page.get("Groups", []):
                    resources.append({
                        "id": item.get("GroupName", ""),
                        "name": item.get("GroupName", ""),
                        "type": "group",
                    })
        except ClientError as e:
            self.logger.error(f"Error listing XRAY resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a XRAY resource."""
        client = self.session.client("xray")
        resource_id = resource.get("id")

        try:
            client.delete_group(GroupName=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting XRAY resource {resource_id}: {str(e)}")
            return False
