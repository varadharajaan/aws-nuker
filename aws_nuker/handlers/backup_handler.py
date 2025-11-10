"""Handler for BACKUP resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class BackupHandler(ResourceHandler):
    """Handler for BACKUP resources."""

    @property
    def service_name(self) -> str:
        return "backup"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all BACKUP resources."""
        client = self.session.client("backup")
        resources = []

        try:
            response = client.list_backup_vaults()
            for item in response.get("BackupVaultList", []):
                resources.append({
                    "id": item.get("BackupVaultName", ""),
                    "name": item.get("BackupVaultName", ""),
                    "type": "vault",
                })
        except ClientError as e:
            self.logger.error(f"Error listing BACKUP resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a BACKUP resource."""
        client = self.session.client("backup")
        resource_id = resource.get("id")

        try:
            client.delete_backup_vault(BackupVaultName=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting BACKUP resource {resource_id}: {str(e)}")
            return False
