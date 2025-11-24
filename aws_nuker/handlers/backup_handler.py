"""AWS Backup resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class BackupHandler(ResourceHandler):
    """Handler for AWS Backup resources."""

    @property
    def service_name(self) -> str:
        return "backup"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all AWS Backup resources."""
        backup = self.session.client("backup")
        resources = []

        try:
            # List backup vaults (skip default vault)
            paginator = backup.get_paginator("list_backup_vaults")
            for page in paginator.paginate():
                for vault in page.get("BackupVaultList", []):
                    vault_name = vault["BackupVaultName"]
                    if vault_name != "Default":
                        resources.append({
                            "id": vault["BackupVaultArn"],
                            "name": vault_name,
                            "type": "backup_vault",
                        })

        except ClientError as e:
            self.logger.error(f"Error listing Backup vaults: {str(e)}")

        try:
            # List backup plans
            paginator = backup.get_paginator("list_backup_plans")
            for page in paginator.paginate():
                for plan in page.get("BackupPlansList", []):
                    resources.append({
                        "id": plan["BackupPlanId"],
                        "name": plan.get("BackupPlanName", plan["BackupPlanId"]),
                        "type": "backup_plan",
                    })

        except ClientError as e:
            self.logger.error(f"Error listing Backup plans: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete an AWS Backup resource."""
        backup = self.session.client("backup")
        resource_type = resource.get("type")
        resource_name = resource.get("name")
        resource_id = resource.get("id")

        try:
            if resource_type == "backup_vault":
                # Delete all recovery points in the vault first
                try:
                    paginator = backup.get_paginator("list_recovery_points_by_backup_vault")
                    for page in paginator.paginate(BackupVaultName=resource_name):
                        for recovery_point in page.get("RecoveryPoints", []):
                            try:
                                backup.delete_recovery_point(
                                    BackupVaultName=resource_name,
                                    RecoveryPointArn=recovery_point["RecoveryPointArn"]
                                )
                            except ClientError as e:
                                # Log but continue if individual recovery point can't be deleted
                                error_code = e.response.get("Error", {}).get("Code", "")
                                if error_code not in ["ResourceNotFoundException"]:
                                    self.logger.warning(
                                        f"Could not delete recovery point {recovery_point['RecoveryPointArn']}: {str(e)}"
                                    )
                except ClientError as e:
                    self.logger.warning(
                        f"Error listing recovery points for vault {resource_name}: {str(e)}"
                    )

                # Delete the vault
                backup.delete_backup_vault(BackupVaultName=resource_name)
                return True

            elif resource_type == "backup_plan":
                backup.delete_backup_plan(BackupPlanId=resource_id)
                return True

            return False

        except ClientError as e:
            self.logger.error(
                f"Error deleting Backup {resource_type} {resource_name}: {str(e)}"
            )
            return False
