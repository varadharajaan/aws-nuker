"""IoT SiteWise resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class IoTSiteWiseHandler(ResourceHandler):
    """Handler for AWS IoT SiteWise resources."""

    @property
    def service_name(self) -> str:
        return "iotsitewise"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all IoT SiteWise resources."""
        iotsitewise = self.session.client("iotsitewise")
        resources = []

        try:
            # List asset models
            paginator = iotsitewise.get_paginator("list_asset_models")
            for page in paginator.paginate():
                for model in page.get("assetModelSummaries", []):
                    resources.append({
                        "id": model["id"],
                        "name": model["name"],
                        "type": "asset_model",
                    })

        except ClientError as e:
            self.logger.error(f"Error listing IoT SiteWise asset models: {str(e)}")

        try:
            # List assets
            paginator = iotsitewise.get_paginator("list_assets")
            for page in paginator.paginate():
                for asset in page.get("assetSummaries", []):
                    resources.append({
                        "id": asset["id"],
                        "name": asset["name"],
                        "type": "asset",
                    })

        except ClientError as e:
            self.logger.error(f"Error listing IoT SiteWise assets: {str(e)}")

        try:
            # List gateways
            paginator = iotsitewise.get_paginator("list_gateways")
            for page in paginator.paginate():
                for gateway in page.get("gatewaySummaries", []):
                    resources.append({
                        "id": gateway["gatewayId"],
                        "name": gateway["gatewayName"],
                        "type": "gateway",
                    })

        except ClientError as e:
            self.logger.error(f"Error listing IoT SiteWise gateways: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete an IoT SiteWise resource."""
        iotsitewise = self.session.client("iotsitewise")
        resource_type = resource.get("type")
        resource_id = resource.get("id")

        try:
            if resource_type == "asset":
                iotsitewise.delete_asset(assetId=resource_id)
                return True

            elif resource_type == "asset_model":
                iotsitewise.delete_asset_model(assetModelId=resource_id)
                return True

            elif resource_type == "gateway":
                iotsitewise.delete_gateway(gatewayId=resource_id)
                return True

            return False

        except ClientError as e:
            self.logger.error(
                f"Error deleting IoT SiteWise {resource_type} {resource_id}: {str(e)}"
            )
            return False
