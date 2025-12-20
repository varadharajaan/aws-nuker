"""Chime resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class ChimeHandler(ResourceHandler):
    """Handler for Amazon Chime resources."""

    @property
    def service_name(self) -> str:
        return "chime"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all Chime resources."""
        chime = self.session.client("chime")
        resources = []

        try:
            # List voice connectors
            response = chime.list_voice_connectors()
            for vc in response.get("VoiceConnectors", []):
                resources.append({
                    "id": vc["VoiceConnectorId"],
                    "name": vc.get("Name", vc["VoiceConnectorId"]),
                    "type": "voice_connector",
                })

        except ClientError as e:
            self.logger.error(f"Error listing Chime voice connectors: {str(e)}")

        try:
            # List SIP media applications
            response = chime.list_sip_media_applications()
            for app in response.get("SipMediaApplications", []):
                resources.append({
                    "id": app["SipMediaApplicationId"],
                    "name": app.get("Name", app["SipMediaApplicationId"]),
                    "type": "sip_media_application",
                })

        except ClientError as e:
            self.logger.error(f"Error listing Chime SIP media applications: {str(e)}")

        try:
            # List SIP rules
            response = chime.list_sip_rules()
            for rule in response.get("SipRules", []):
                resources.append({
                    "id": rule["SipRuleId"],
                    "name": rule.get("Name", rule["SipRuleId"]),
                    "type": "sip_rule",
                })

        except ClientError as e:
            self.logger.error(f"Error listing Chime SIP rules: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a Chime resource."""
        chime = self.session.client("chime")
        resource_type = resource.get("type")
        resource_id = resource.get("id")

        try:
            if resource_type == "voice_connector":
                chime.delete_voice_connector(VoiceConnectorId=resource_id)
                return True

            elif resource_type == "sip_media_application":
                chime.delete_sip_media_application(SipMediaApplicationId=resource_id)
                return True

            elif resource_type == "sip_rule":
                chime.delete_sip_rule(SipRuleId=resource_id)
                return True

            return False

        except ClientError as e:
            self.logger.error(
                f"Error deleting Chime {resource_type} {resource_id}: {str(e)}"
            )
            return False
