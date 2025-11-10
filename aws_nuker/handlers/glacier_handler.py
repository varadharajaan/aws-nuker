"""Handler for GLACIER resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class GlacierHandler(ResourceHandler):
    """Handler for GLACIER resources."""

    @property
    def service_name(self) -> str:
        return "glacier"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all GLACIER resources."""
        client = self.session.client("glacier")
        resources = []

        try:
            paginator = client.get_paginator("list_vaults")
            for page in paginator.paginate():
                for item in page.get("VaultList", []):
                    resources.append({
                        "id": item.get("VaultName", ""),
                        "name": item.get("VaultName", ""),
                        "type": "vault",
                    })
        except ClientError as e:
            self.logger.error(f"Error listing GLACIER resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a GLACIER resource."""
        client = self.session.client("glacier")
        resource_id = resource.get("id")

        try:
            client.delete_vault(vaultName=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting GLACIER resource {resource_id}: {str(e)}")
            return False
