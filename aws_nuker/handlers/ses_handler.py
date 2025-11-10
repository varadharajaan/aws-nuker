"""Handler for SES resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class SesHandler(ResourceHandler):
    """Handler for SES resources."""

    @property
    def service_name(self) -> str:
        return "ses"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all SES resources."""
        client = self.session.client("sesv2")
        resources = []

        try:
            response = client.list_email_identities()
            for item in response.get("EmailIdentities", []):
                resources.append({
                    "id": item.get("IdentityName", ""),
                    "name": item.get("IdentityName", ""),
                    "type": "identity",
                })
        except ClientError as e:
            self.logger.error(f"Error listing SES resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a SES resource."""
        client = self.session.client("sesv2")
        resource_id = resource.get("id")

        try:
            client.delete_email_identity(EmailIdentity=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting SES resource {resource_id}: {str(e)}")
            return False
