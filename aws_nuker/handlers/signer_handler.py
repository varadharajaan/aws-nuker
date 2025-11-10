"""Handler for SIGNER resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class SignerHandler(ResourceHandler):
    """Handler for SIGNER resources."""

    @property
    def service_name(self) -> str:
        return "signer"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all SIGNER resources."""
        client = self.session.client("signer")
        resources = []

        try:
            paginator = client.get_paginator("list_signing_profiles")
            for page in paginator.paginate():
                for item in page.get("profiles", []):
                    resources.append({
                        "id": item.get("profileName", ""),
                        "name": item.get("profileName", ""),
                        "type": "profile",
                    })
        except ClientError as e:
            self.logger.error(f"Error listing SIGNER resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a SIGNER resource."""
        client = self.session.client("signer")
        resource_id = resource.get("id")

        try:
            client.cancel_signing_profile(profileName=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting SIGNER resource {resource_id}: {str(e)}")
            return False
