"""Firewall Manager resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class FMSHandler(ResourceHandler):
    """Handler for AWS Firewall Manager resources."""

    @property
    def service_name(self) -> str:
        return "fms"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all Firewall Manager policies."""
        fms = self.session.client("fms")
        resources = []

        try:
            # List policies
            paginator = fms.get_paginator("list_policies")
            for page in paginator.paginate():
                for policy in page.get("PolicyList", []):
                    resources.append({
                        "id": policy["PolicyArn"],
                        "name": policy.get("PolicyName", policy["PolicyId"]),
                        "type": "policy",
                        "policy_id": policy["PolicyId"],
                    })

        except ClientError as e:
            self.logger.error(f"Error listing Firewall Manager policies: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a Firewall Manager policy."""
        fms = self.session.client("fms")
        policy_id = resource.get("policy_id")

        try:
            fms.delete_policy(PolicyId=policy_id, DeleteAllPolicyResources=True)
            return True
        except ClientError as e:
            self.logger.error(
                f"Error deleting Firewall Manager policy {policy_id}: {str(e)}"
            )
            return False
