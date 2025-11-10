"""Handler for ORGANIZATIONS resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class OrganizationsHandler(ResourceHandler):
    """Handler for ORGANIZATIONS resources."""

    @property
    def service_name(self) -> str:
        return "organizations"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all ORGANIZATIONS resources."""
        client = self.session.client("organizations")
        resources = []

        try:
            paginator = client.get_paginator("list_accounts")
            for page in paginator.paginate():
                for item in page.get("Accounts", []):
                    resources.append({
                        "id": item.get("Id", ""),
                        "name": item.get("Name", ""),
                        "type": "account",
                    })
        except ClientError as e:
            self.logger.error(f"Error listing ORGANIZATIONS resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a ORGANIZATIONS resource."""
        client = self.session.client("organizations")
        resource_id = resource.get("id")

        try:
            client.remove_account_from_organization(AccountId=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting ORGANIZATIONS resource {resource_id}: {str(e)}")
            return False
