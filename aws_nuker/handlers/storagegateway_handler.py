"""Storage Gateway resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class StorageGatewayHandler(ResourceHandler):
    """Handler for AWS Storage Gateway resources."""

    @property
    def service_name(self) -> str:
        return "storagegateway"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all Storage Gateway gateways."""
        storagegateway = self.session.client("storagegateway")
        resources = []

        try:
            # List gateways
            paginator = storagegateway.get_paginator("list_gateways")
            for page in paginator.paginate():
                for gateway in page.get("Gateways", []):
                    resources.append({
                        "id": gateway["GatewayARN"],
                        "name": gateway.get("GatewayName", gateway["GatewayId"]),
                        "type": "gateway",
                        "gateway_arn": gateway["GatewayARN"],
                    })

        except ClientError as e:
            self.logger.error(f"Error listing Storage Gateway gateways: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a Storage Gateway."""
        storagegateway = self.session.client("storagegateway")
        gateway_arn = resource.get("gateway_arn")

        try:
            storagegateway.delete_gateway(GatewayARN=gateway_arn)
            return True
        except ClientError as e:
            self.logger.error(
                f"Error deleting Storage Gateway {gateway_arn}: {str(e)}"
            )
            return False
