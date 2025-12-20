"""Security Hub resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class SecurityHubHandler(ResourceHandler):
    """Handler for AWS Security Hub resources."""

    @property
    def service_name(self) -> str:
        return "securityhub"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all Security Hub resources."""
        securityhub = self.session.client("securityhub")
        resources = []

        try:
            # Check if Security Hub is enabled
            response = securityhub.describe_hub()
            if response.get("HubArn"):
                resources.append({
                    "id": response["HubArn"],
                    "name": "Security Hub",
                    "type": "hub",
                })

        except ClientError as e:
            if e.response.get("Error", {}).get("Code") != "InvalidAccessException":
                self.logger.error(f"Error describing Security Hub: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete Security Hub (disable it)."""
        securityhub = self.session.client("securityhub")

        try:
            securityhub.disable_security_hub()
            return True
        except ClientError as e:
            self.logger.error(
                f"Error disabling Security Hub: {str(e)}"
            )
            return False
