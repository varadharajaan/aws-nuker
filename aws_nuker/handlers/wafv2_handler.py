"""WAFv2 resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class WAFv2Handler(ResourceHandler):
    """Handler for WAFv2 web ACLs and rule groups."""

    @property
    def service_name(self) -> str:
        return "wafv2"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all WAFv2 resources."""
        # WAFv2 has different scopes: REGIONAL and CLOUDFRONT
        # CLOUDFRONT resources must be managed in us-east-1
        resources = []

        # List REGIONAL resources
        resources.extend(self._list_wafv2_resources("REGIONAL"))
        
        # Only list CLOUDFRONT resources if we're in us-east-1
        if self.region == "us-east-1":
            resources.extend(self._list_wafv2_resources("CLOUDFRONT"))

        return resources

    def _list_wafv2_resources(self, scope: str) -> List[Dict[str, Any]]:
        """List WAFv2 resources for a specific scope."""
        wafv2 = self.session.client("wafv2")
        resources = []

        try:
            # List Web ACLs
            response = wafv2.list_web_acls(Scope=scope)
            for acl in response.get("WebACLs", []):
                resources.append({
                    "id": acl["Id"],
                    "name": acl["Name"],
                    "type": "web_acl",
                    "scope": scope,
                    "lock_token": acl.get("LockToken", ""),
                })

        except ClientError as e:
            self.logger.error(f"Error listing WAFv2 Web ACLs ({scope}): {str(e)}")

        try:
            # List Rule Groups
            response = wafv2.list_rule_groups(Scope=scope)
            for rg in response.get("RuleGroups", []):
                resources.append({
                    "id": rg["Id"],
                    "name": rg["Name"],
                    "type": "rule_group",
                    "scope": scope,
                    "lock_token": rg.get("LockToken", ""),
                })

        except ClientError as e:
            self.logger.error(f"Error listing WAFv2 Rule Groups ({scope}): {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a WAFv2 resource."""
        wafv2 = self.session.client("wafv2")
        resource_type = resource.get("type")
        resource_name = resource.get("name")
        resource_id = resource.get("id")
        scope = resource.get("scope", "REGIONAL")
        lock_token = resource.get("lock_token", "")

        try:
            if resource_type == "web_acl":
                wafv2.delete_web_acl(
                    Name=resource_name,
                    Scope=scope,
                    Id=resource_id,
                    LockToken=lock_token
                )
                return True

            elif resource_type == "rule_group":
                wafv2.delete_rule_group(
                    Name=resource_name,
                    Scope=scope,
                    Id=resource_id,
                    LockToken=lock_token
                )
                return True

            return False

        except ClientError as e:
            self.logger.error(
                f"Error deleting WAFv2 {resource_type} {resource_name}: {str(e)}"
            )
            return False
