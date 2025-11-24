"""SES (Simple Email Service) resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class SESHandler(ResourceHandler):
    """Handler for SES identities and configuration sets."""

    @property
    def service_name(self) -> str:
        return "ses"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all SES resources."""
        ses = self.session.client("ses")
        resources = []

        try:
            # List email identities
            response = ses.list_identities()
            for identity in response.get("Identities", []):
                resources.append({
                    "id": identity,
                    "name": identity,
                    "type": "identity",
                })

        except ClientError as e:
            self.logger.error(f"Error listing SES identities: {str(e)}")

        try:
            # List configuration sets
            response = ses.list_configuration_sets()
            for config_set in response.get("ConfigurationSets", []):
                name = config_set.get("Name", "")
                resources.append({
                    "id": name,
                    "name": name,
                    "type": "configuration_set",
                })

        except ClientError as e:
            self.logger.error(f"Error listing SES configuration sets: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete an SES resource."""
        ses = self.session.client("ses")
        resource_type = resource.get("type")
        resource_name = resource.get("name")

        try:
            if resource_type == "identity":
                ses.delete_identity(Identity=resource_name)
                return True

            elif resource_type == "configuration_set":
                ses.delete_configuration_set(ConfigurationSetName=resource_name)
                return True

            return False

        except ClientError as e:
            self.logger.error(
                f"Error deleting SES {resource_type} {resource_name}: {str(e)}"
            )
            return False
