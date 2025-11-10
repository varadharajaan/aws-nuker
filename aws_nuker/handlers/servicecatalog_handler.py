"""Handler for SERVICECATALOG resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class ServicecatalogHandler(ResourceHandler):
    """Handler for SERVICECATALOG resources."""

    @property
    def service_name(self) -> str:
        return "servicecatalog"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all SERVICECATALOG resources."""
        client = self.session.client("servicecatalog")
        resources = []

        try:
            response = client.list_portfolios()
            for item in response.get("PortfolioDetails", []):
                resources.append({
                    "id": item.get("Id", ""),
                    "name": item.get("DisplayName", ""),
                    "type": "portfolio",
                })
        except ClientError as e:
            self.logger.error(f"Error listing SERVICECATALOG resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a SERVICECATALOG resource."""
        client = self.session.client("servicecatalog")
        resource_id = resource.get("id")

        try:
            client.delete_portfolio(Id=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting SERVICECATALOG resource {resource_id}: {str(e)}")
            return False
