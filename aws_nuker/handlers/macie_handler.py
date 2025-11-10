"""Handler for MACIE resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class MacieHandler(ResourceHandler):
    """Handler for MACIE resources."""

    @property
    def service_name(self) -> str:
        return "macie"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all MACIE resources."""
        client = self.session.client("macie2")
        resources = []

        try:
            paginator = client.get_paginator("list_classification_jobs")
            for page in paginator.paginate():
                for item in page.get("items", []):
                    resources.append({
                        "id": item.get("id", ""),
                        "name": item.get("name", ""),
                        "type": "job",
                    })
        except ClientError as e:
            self.logger.error(f"Error listing MACIE resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a MACIE resource."""
        client = self.session.client("macie2")
        resource_id = resource.get("id")

        try:
            client.delete_custom_data_identifier(id=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting MACIE resource {resource_id}: {str(e)}")
            return False
