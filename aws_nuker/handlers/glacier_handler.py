"""Glacier resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class GlacierHandler(ResourceHandler):
    """Handler for Amazon S3 Glacier resources."""

    @property
    def service_name(self) -> str:
        return "glacier"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all Glacier vaults."""
        glacier = self.session.client("glacier")
        resources = []

        try:
            # List vaults
            paginator = glacier.get_paginator("list_vaults")
            for page in paginator.paginate():
                for vault in page.get("VaultList", []):
                    resources.append({
                        "id": vault["VaultARN"],
                        "name": vault["VaultName"],
                        "type": "vault",
                    })

        except ClientError as e:
            self.logger.error(f"Error listing Glacier vaults: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a Glacier vault."""
        glacier = self.session.client("glacier")
        vault_name = resource.get("name")

        try:
            glacier.delete_vault(vaultName=vault_name)
            return True
        except ClientError as e:
            self.logger.error(
                f"Error deleting Glacier vault {vault_name}: {str(e)}"
            )
            return False
