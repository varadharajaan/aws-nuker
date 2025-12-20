"""WorkMail resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class WorkMailHandler(ResourceHandler):
    """Handler for Amazon WorkMail resources."""

    @property
    def service_name(self) -> str:
        return "workmail"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all WorkMail organizations."""
        workmail = self.session.client("workmail")
        resources = []

        try:
            # List organizations
            paginator = workmail.get_paginator("list_organizations")
            for page in paginator.paginate():
                for org in page.get("OrganizationSummaries", []):
                    resources.append({
                        "id": org["OrganizationId"],
                        "name": org.get("Alias", org["OrganizationId"]),
                        "type": "organization",
                        "state": org.get("State", ""),
                    })

        except ClientError as e:
            self.logger.error(f"Error listing WorkMail organizations: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a WorkMail organization."""
        workmail = self.session.client("workmail")
        org_id = resource.get("id")

        try:
            workmail.delete_organization(
                OrganizationId=org_id,
                DeleteDirectory=True
            )
            return True
        except ClientError as e:
            self.logger.error(
                f"Error deleting WorkMail organization {org_id}: {str(e)}"
            )
            return False
