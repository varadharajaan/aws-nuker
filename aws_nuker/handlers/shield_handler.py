"""Shield resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class ShieldHandler(ResourceHandler):
    """Handler for AWS Shield resources."""

    @property
    def service_name(self) -> str:
        return "shield"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all Shield protections."""
        # Shield is a global service
        shield = self.session.client("shield", region_name="us-east-1")
        resources = []

        try:
            # List protections
            paginator = shield.get_paginator("list_protections")
            for page in paginator.paginate():
                for protection in page.get("Protections", []):
                    resources.append({
                        "id": protection["Id"],
                        "name": protection.get("Name", protection["Id"]),
                        "type": "protection",
                    })

        except ClientError as e:
            self.logger.error(f"Error listing Shield protections: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a Shield protection."""
        shield = self.session.client("shield", region_name="us-east-1")
        protection_id = resource.get("id")

        try:
            shield.delete_protection(ProtectionId=protection_id)
            return True
        except ClientError as e:
            self.logger.error(
                f"Error deleting Shield protection {protection_id}: {str(e)}"
            )
            return False
