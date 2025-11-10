"""Handler for KENDRA resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class KendraHandler(ResourceHandler):
    """Handler for KENDRA resources."""

    @property
    def service_name(self) -> str:
        return "kendra"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all KENDRA resources."""
        client = self.session.client("kendra")
        resources = []

        try:
            paginator = client.get_paginator("list_indices")
            for page in paginator.paginate():
                for item in page.get("IndexConfigurationSummaryItems", []):
                    resources.append({
                        "id": item.get("Id", ""),
                        "name": item.get("Name", ""),
                        "type": "index",
                    })
        except ClientError as e:
            self.logger.error(f"Error listing KENDRA resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a KENDRA resource."""
        client = self.session.client("kendra")
        resource_id = resource.get("id")

        try:
            client.delete_index(Id=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting KENDRA resource {resource_id}: {str(e)}")
            return False
