"""Handler for CLOUDFRONT resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class CloudfrontHandler(ResourceHandler):
    """Handler for CLOUDFRONT resources."""

    @property
    def service_name(self) -> str:
        return "cloudfront"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all CLOUDFRONT resources."""
        client = self.session.client("cloudfront")
        resources = []

        try:
            paginator = client.get_paginator("list_distributions")
            for page in paginator.paginate():
                for item in page.get("DistributionList", []):
                    resources.append({
                        "id": item.get("Id", ""),
                        "name": item.get("Id", ""),
                        "type": "distribution",
                    })
        except ClientError as e:
            self.logger.error(f"Error listing CLOUDFRONT resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a CLOUDFRONT resource."""
        client = self.session.client("cloudfront")
        resource_id = resource.get("id")

        try:
            client.delete_distribution(Id=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting CLOUDFRONT resource {resource_id}: {str(e)}")
            return False
