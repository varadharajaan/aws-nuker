"""Handler for SECURITYHUB resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class SecurityhubHandler(ResourceHandler):
    """Handler for SECURITYHUB resources."""

    @property
    def service_name(self) -> str:
        return "securityhub"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all SECURITYHUB resources."""
        client = self.session.client("securityhub")
        resources = []

        try:
            paginator = client.get_paginator("get_findings")
            for page in paginator.paginate():
                for item in page.get("Findings", []):
                    resources.append({
                        "id": item.get("Id", ""),
                        "name": item.get("Id", ""),
                        "type": "finding",
                    })
        except ClientError as e:
            self.logger.error(f"Error listing SECURITYHUB resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a SECURITYHUB resource."""
        client = self.session.client("securityhub")
        resource_id = resource.get("id")

        try:
            client.batch_update_findings(Id=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting SECURITYHUB resource {resource_id}: {str(e)}")
            return False
