"""Handler for STORAGEGATEWAY resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class StoragegatewayHandler(ResourceHandler):
    """Handler for STORAGEGATEWAY resources."""

    @property
    def service_name(self) -> str:
        return "storagegateway"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all STORAGEGATEWAY resources."""
        client = self.session.client("storagegateway")
        resources = []

        try:
            paginator = client.get_paginator("list_gateways")
            for page in paginator.paginate():
                for item in page.get("Gateways", []):
                    resources.append({
                        "id": item.get("GatewayARN", ""),
                        "name": item.get("GatewayName", ""),
                        "type": "gateway",
                    })
        except ClientError as e:
            self.logger.error(f"Error listing STORAGEGATEWAY resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a STORAGEGATEWAY resource."""
        client = self.session.client("storagegateway")
        resource_id = resource.get("id")

        try:
            client.delete_gateway(GatewayARN=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting STORAGEGATEWAY resource {resource_id}: {str(e)}")
            return False
