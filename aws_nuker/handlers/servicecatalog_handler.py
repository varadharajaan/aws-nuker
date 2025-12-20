"""Service Catalog resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class ServiceCatalogHandler(ResourceHandler):
    """Handler for AWS Service Catalog resources."""

    @property
    def service_name(self) -> str:
        return "servicecatalog"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all Service Catalog resources."""
        servicecatalog = self.session.client("servicecatalog")
        resources = []

        try:
            # List portfolios
            response = servicecatalog.list_portfolios()
            for portfolio in response.get("PortfolioDetails", []):
                resources.append({
                    "id": portfolio["Id"],
                    "name": portfolio.get("DisplayName", portfolio["Id"]),
                    "type": "portfolio",
                })

        except ClientError as e:
            self.logger.error(f"Error listing Service Catalog portfolios: {str(e)}")

        try:
            # List products
            response = servicecatalog.search_products_as_admin()
            for product in response.get("ProductViewDetails", []):
                product_view = product.get("ProductViewSummary", {})
                resources.append({
                    "id": product_view["ProductId"],
                    "name": product_view.get("Name", product_view["ProductId"]),
                    "type": "product",
                })

        except ClientError as e:
            self.logger.error(f"Error listing Service Catalog products: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a Service Catalog resource."""
        servicecatalog = self.session.client("servicecatalog")
        resource_type = resource.get("type")
        resource_id = resource.get("id")

        try:
            if resource_type == "product":
                servicecatalog.delete_product(Id=resource_id)
                return True

            elif resource_type == "portfolio":
                servicecatalog.delete_portfolio(Id=resource_id)
                return True

            return False

        except ClientError as e:
            self.logger.error(
                f"Error deleting Service Catalog {resource_type} {resource_id}: {str(e)}"
            )
            return False
