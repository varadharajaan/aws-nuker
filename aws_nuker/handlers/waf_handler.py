"""WAF Classic resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class WAFHandler(ResourceHandler):
    """Handler for WAF Classic resources."""

    @property
    def service_name(self) -> str:
        return "waf"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all WAF Classic resources."""
        waf = self.session.client("waf")
        resources = []

        try:
            # List Web ACLs
            response = waf.list_web_acls(Limit=100)
            for acl in response.get("WebACLs", []):
                resources.append({
                    "id": acl["WebACLId"],
                    "name": acl["Name"],
                    "type": "web_acl",
                })

        except ClientError as e:
            self.logger.error(f"Error listing WAF Web ACLs: {str(e)}")

        try:
            # List Rule Groups
            response = waf.list_rule_groups(Limit=100)
            for rg in response.get("RuleGroups", []):
                resources.append({
                    "id": rg["RuleGroupId"],
                    "name": rg["Name"],
                    "type": "rule_group",
                })

        except ClientError as e:
            self.logger.error(f"Error listing WAF Rule Groups: {str(e)}")

        try:
            # List Rules
            response = waf.list_rules(Limit=100)
            for rule in response.get("Rules", []):
                resources.append({
                    "id": rule["RuleId"],
                    "name": rule["Name"],
                    "type": "rule",
                })

        except ClientError as e:
            self.logger.error(f"Error listing WAF Rules: {str(e)}")

        return resources

    def _get_change_token(self, waf) -> str:
        """Get WAF change token."""
        try:
            response = waf.get_change_token()
            return response["ChangeToken"]
        except ClientError as e:
            self.logger.error(f"Error getting WAF change token: {str(e)}")
            return ""

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a WAF Classic resource."""
        waf = self.session.client("waf")
        resource_type = resource.get("type")
        resource_id = resource.get("id")

        change_token = self._get_change_token(waf)
        if not change_token:
            return False

        try:
            if resource_type == "web_acl":
                waf.delete_web_acl(
                    WebACLId=resource_id,
                    ChangeToken=change_token
                )
                return True

            elif resource_type == "rule_group":
                waf.delete_rule_group(
                    RuleGroupId=resource_id,
                    ChangeToken=change_token
                )
                return True

            elif resource_type == "rule":
                waf.delete_rule(
                    RuleId=resource_id,
                    ChangeToken=change_token
                )
                return True

            return False

        except ClientError as e:
            self.logger.error(
                f"Error deleting WAF {resource_type} {resource_id}: {str(e)}"
            )
            return False
