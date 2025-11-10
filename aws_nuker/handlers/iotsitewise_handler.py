"""Handler for IOTSITEWISE resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class IotsitewiseHandler(ResourceHandler):
    """Handler for IOTSITEWISE resources."""

    @property
    def service_name(self) -> str:
        return "iotsitewise"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all IOTSITEWISE resources."""
        client = self.session.client("iotsitewise")
        resources = []

        try:
            paginator = client.get_paginator("list_assets")
            for page in paginator.paginate():
                for item in page.get("assetSummaries", []):
                    resources.append({
                        "id": item.get("id", ""),
                        "name": item.get("name", ""),
                        "type": "asset",
                    })
        except ClientError as e:
            self.logger.error(f"Error listing IOTSITEWISE resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a IOTSITEWISE resource."""
        client = self.session.client("iotsitewise")
        resource_id = resource.get("id")

        try:
            client.delete_asset(assetId=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting IOTSITEWISE resource {resource_id}: {str(e)}")
            return False
