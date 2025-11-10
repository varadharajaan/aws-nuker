"""Handler for LAKEFORMATION resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class LakeformationHandler(ResourceHandler):
    """Handler for LAKEFORMATION resources."""

    @property
    def service_name(self) -> str:
        return "lakeformation"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all LAKEFORMATION resources."""
        client = self.session.client("lakeformation")
        resources = []

        try:
            paginator = client.get_paginator("list_resources")
            for page in paginator.paginate():
                for item in page.get("ResourceInfoList", []):
                    resources.append({
                        "id": item.get("ResourceArn", ""),
                        "name": item.get("ResourceArn", ""),
                        "type": "resource",
                    })
        except ClientError as e:
            self.logger.error(f"Error listing LAKEFORMATION resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a LAKEFORMATION resource."""
        client = self.session.client("lakeformation")
        resource_id = resource.get("id")

        try:
            client.deregister_resource(ResourceArn=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting LAKEFORMATION resource {resource_id}: {str(e)}")
            return False
