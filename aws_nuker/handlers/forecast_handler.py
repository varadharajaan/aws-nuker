"""Handler for FORECAST resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class ForecastHandler(ResourceHandler):
    """Handler for FORECAST resources."""

    @property
    def service_name(self) -> str:
        return "forecast"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all FORECAST resources."""
        client = self.session.client("forecast")
        resources = []

        try:
            paginator = client.get_paginator("list_forecasts")
            for page in paginator.paginate():
                for item in page.get("Forecasts", []):
                    resources.append({
                        "id": item.get("ForecastArn", ""),
                        "name": item.get("ForecastName", ""),
                        "type": "forecast",
                    })
        except ClientError as e:
            self.logger.error(f"Error listing FORECAST resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a FORECAST resource."""
        client = self.session.client("forecast")
        resource_id = resource.get("id")

        try:
            client.delete_forecast(ForecastArn=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting FORECAST resource {resource_id}: {str(e)}")
            return False
