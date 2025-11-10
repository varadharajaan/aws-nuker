"""Handler for INSPECTOR resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class InspectorHandler(ResourceHandler):
    """Handler for INSPECTOR resources."""

    @property
    def service_name(self) -> str:
        return "inspector"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all INSPECTOR resources."""
        client = self.session.client("inspector2")
        resources = []

        try:
            paginator = client.get_paginator("list_findings")
            for page in paginator.paginate():
                for item in page.get("findings", []):
                    resources.append({
                        "id": item.get("findingArn", ""),
                        "name": item.get("findingArn", ""),
                        "type": "finding",
                    })
        except ClientError as e:
            self.logger.error(f"Error listing INSPECTOR resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a INSPECTOR resource."""
        client = self.session.client("inspector2")
        resource_id = resource.get("id")

        try:
            client.batch_update_findings(findingArns=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting INSPECTOR resource {resource_id}: {str(e)}")
            return False
