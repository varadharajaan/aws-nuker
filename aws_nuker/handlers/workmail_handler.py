"""Handler for WORKMAIL resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class WorkmailHandler(ResourceHandler):
    """Handler for WORKMAIL resources."""

    @property
    def service_name(self) -> str:
        return "workmail"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all WORKMAIL resources."""
        client = self.session.client("workmail")
        resources = []

        try:
            response = client.list_organizations()
            for item in response.get("OrganizationSummaries", []):
                resources.append({
                    "id": item.get("OrganizationId", ""),
                    "name": item.get("Alias", ""),
                    "type": "organization",
                })
        except ClientError as e:
            self.logger.error(f"Error listing WORKMAIL resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a WORKMAIL resource."""
        client = self.session.client("workmail")
        resource_id = resource.get("id")

        try:
            client.delete_organization(OrganizationId=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting WORKMAIL resource {resource_id}: {str(e)}")
            return False
