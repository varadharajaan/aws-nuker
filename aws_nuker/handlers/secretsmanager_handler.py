"""Secrets Manager resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class SecretsManagerHandler(ResourceHandler):
    """Handler for AWS Secrets Manager secrets."""

    @property
    def service_name(self) -> str:
        return "secretsmanager"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all Secrets Manager secrets."""
        sm = self.session.client("secretsmanager")
        resources = []

        try:
            paginator = sm.get_paginator("list_secrets")
            for page in paginator.paginate():
                for secret in page.get("SecretList", []):
                    # Skip secrets that are already scheduled for deletion
                    if "DeletedDate" not in secret:
                        resources.append({
                            "id": secret["ARN"],
                            "name": secret["Name"],
                            "type": "secret",
                        })

        except ClientError as e:
            self.logger.error(f"Error listing Secrets Manager secrets: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a Secrets Manager secret."""
        sm = self.session.client("secretsmanager")
        secret_id = resource.get("id")

        try:
            # Delete secret with no recovery window if force is enabled
            recovery_days = 7 if not self.force else 0

            if recovery_days == 0:
                sm.delete_secret(
                    SecretId=secret_id,
                    ForceDeleteWithoutRecovery=True
                )
            else:
                sm.delete_secret(
                    SecretId=secret_id,
                    RecoveryWindowInDays=recovery_days
                )
            return True
        except ClientError as e:
            self.logger.error(
                f"Error deleting secret {secret_id}: {str(e)}"
            )
            return False
