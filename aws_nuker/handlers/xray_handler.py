"""XRay resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class XRayHandler(ResourceHandler):
    """Handler for AWS X-Ray sampling rules and groups."""

    @property
    def service_name(self) -> str:
        return "xray"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all X-Ray resources."""
        xray = self.session.client("xray")
        resources = []

        try:
            # List sampling rules (skip default rule)
            paginator = xray.get_paginator("get_sampling_rules")
            for page in paginator.paginate():
                for rule in page.get("SamplingRuleRecords", []):
                    rule_name = rule.get("SamplingRule", {}).get("RuleName", "")
                    if rule_name and rule_name != "Default":
                        resources.append({
                            "id": rule_name,
                            "name": rule_name,
                            "type": "sampling_rule",
                        })

        except ClientError as e:
            self.logger.error(f"Error listing X-Ray sampling rules: {str(e)}")

        try:
            # List groups
            paginator = xray.get_paginator("get_groups")
            for page in paginator.paginate():
                for group in page.get("Groups", []):
                    resources.append({
                        "id": group.get("GroupARN", ""),
                        "name": group.get("GroupName", ""),
                        "type": "group",
                    })

        except ClientError as e:
            self.logger.error(f"Error listing X-Ray groups: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete an X-Ray resource."""
        xray = self.session.client("xray")
        resource_type = resource.get("type")
        resource_name = resource.get("name")

        try:
            if resource_type == "sampling_rule":
                xray.delete_sampling_rule(RuleName=resource_name)
                return True

            elif resource_type == "group":
                xray.delete_group(GroupName=resource_name)
                return True

            return False

        except ClientError as e:
            self.logger.error(
                f"Error deleting X-Ray {resource_type} {resource_name}: {str(e)}"
            )
            return False
