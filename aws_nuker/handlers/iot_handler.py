"""IoT Core resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class IoTHandler(ResourceHandler):
    """Handler for AWS IoT Core resources."""

    @property
    def service_name(self) -> str:
        return "iot"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all IoT Core resources."""
        iot = self.session.client("iot")
        resources = []

        try:
            # List things
            paginator = iot.get_paginator("list_things")
            for page in paginator.paginate():
                for thing in page.get("things", []):
                    resources.append({
                        "id": thing["thingArn"],
                        "name": thing["thingName"],
                        "type": "thing",
                    })

        except ClientError as e:
            self.logger.error(f"Error listing IoT things: {str(e)}")

        try:
            # List thing groups
            paginator = iot.get_paginator("list_thing_groups")
            for page in paginator.paginate():
                for group in page.get("thingGroups", []):
                    resources.append({
                        "id": group["groupArn"],
                        "name": group["groupName"],
                        "type": "thing_group",
                    })

        except ClientError as e:
            self.logger.error(f"Error listing IoT thing groups: {str(e)}")

        try:
            # List policies
            paginator = iot.get_paginator("list_policies")
            for page in paginator.paginate():
                for policy in page.get("policies", []):
                    resources.append({
                        "id": policy["policyArn"],
                        "name": policy["policyName"],
                        "type": "policy",
                    })

        except ClientError as e:
            self.logger.error(f"Error listing IoT policies: {str(e)}")

        try:
            # List topic rules
            paginator = iot.get_paginator("list_topic_rules")
            for page in paginator.paginate():
                for rule in page.get("rules", []):
                    resources.append({
                        "id": rule["ruleArn"],
                        "name": rule["ruleName"],
                        "type": "topic_rule",
                    })

        except ClientError as e:
            self.logger.error(f"Error listing IoT topic rules: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete an IoT Core resource."""
        iot = self.session.client("iot")
        resource_type = resource.get("type")
        resource_name = resource.get("name")

        try:
            if resource_type == "thing":
                # Detach principals first
                try:
                    principals = iot.list_thing_principals(thingName=resource_name)
                    for principal in principals.get("principals", []):
                        iot.detach_thing_principal(
                            thingName=resource_name,
                            principal=principal
                        )
                except ClientError:
                    pass

                iot.delete_thing(thingName=resource_name)
                return True

            elif resource_type == "thing_group":
                iot.delete_thing_group(thingGroupName=resource_name)
                return True

            elif resource_type == "policy":
                # Detach all targets first
                try:
                    targets = iot.list_targets_for_policy(policyName=resource_name)
                    for target in targets.get("targets", []):
                        iot.detach_policy(policyName=resource_name, target=target)
                except ClientError:
                    pass

                # Delete all versions except default
                try:
                    versions = iot.list_policy_versions(policyName=resource_name)
                    for version in versions.get("policyVersions", []):
                        if not version.get("isDefaultVersion"):
                            iot.delete_policy_version(
                                policyName=resource_name,
                                policyVersionId=version["versionId"]
                            )
                except ClientError:
                    pass

                iot.delete_policy(policyName=resource_name)
                return True

            elif resource_type == "topic_rule":
                iot.delete_topic_rule(ruleName=resource_name)
                return True

            return False

        except ClientError as e:
            self.logger.error(
                f"Error deleting IoT {resource_type} {resource_name}: {str(e)}"
            )
            return False
