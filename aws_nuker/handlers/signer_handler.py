"""Signer resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class SignerHandler(ResourceHandler):
    """Handler for AWS Signer resources."""

    @property
    def service_name(self) -> str:
        return "signer"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all Signer signing profiles."""
        signer = self.session.client("signer")
        resources = []

        try:
            # List signing profiles
            paginator = signer.get_paginator("list_signing_profiles")
            for page in paginator.paginate():
                for profile in page.get("profiles", []):
                    resources.append({
                        "id": profile["profileName"],
                        "name": profile["profileName"],
                        "type": "signing_profile",
                        "status": profile.get("status", ""),
                    })

        except ClientError as e:
            self.logger.error(f"Error listing Signer profiles: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a Signer signing profile."""
        signer = self.session.client("signer")
        profile_name = resource.get("name")

        try:
            signer.cancel_signing_profile(profileName=profile_name)
            return True
        except ClientError as e:
            self.logger.error(
                f"Error canceling Signer profile {profile_name}: {str(e)}"
            )
            return False
