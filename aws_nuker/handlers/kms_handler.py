"""KMS resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class KMSHandler(ResourceHandler):
    """Handler for KMS (Key Management Service) customer-managed keys."""

    @property
    def service_name(self) -> str:
        return "kms"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all customer-managed KMS keys."""
        kms = self.session.client("kms")
        resources = []

        try:
            paginator = kms.get_paginator("list_keys")
            for page in paginator.paginate():
                for key in page.get("Keys", []):
                    key_id = key["KeyId"]

                    # Get key metadata to check if it's customer-managed
                    try:
                        key_metadata = kms.describe_key(KeyId=key_id)
                        key_info = key_metadata["KeyMetadata"]

                        # Only include customer-managed keys (not AWS-managed)
                        if key_info.get("KeyManager") == "CUSTOMER":
                            resources.append({
                                "id": key_id,
                                "name": key_info.get("Description", key_id),
                                "type": "customer_key",
                                "state": key_info.get("KeyState", ""),
                            })
                    except ClientError:
                        # Skip keys we can't describe
                        pass

        except ClientError as e:
            self.logger.error(f"Error listing KMS keys: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Schedule deletion of a KMS key."""
        kms = self.session.client("kms")
        key_id = resource.get("id")

        try:
            # Schedule key deletion (minimum waiting period is 7 days)
            kms.schedule_key_deletion(
                KeyId=key_id,
                PendingWindowInDays=7  # Minimum allowed
            )
            return True
        except ClientError as e:
            self.logger.error(
                f"Error scheduling deletion for KMS key {key_id}: {str(e)}"
            )
            return False
