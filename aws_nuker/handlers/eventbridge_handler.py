"""EventBridge resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class EventBridgeHandler(ResourceHandler):
    """Handler for EventBridge rules and event buses."""

    @property
    def service_name(self) -> str:
        return "eventbridge"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all EventBridge resources."""
        events = self.session.client("events")
        resources = []

        try:
            # List event buses
            paginator = events.get_paginator("list_event_buses")
            for page in paginator.paginate():
                for bus in page.get("EventBuses", []):
                    # Skip default event bus
                    if bus["Name"] != "default":
                        resources.append({
                            "id": bus["Arn"],
                            "name": bus["Name"],
                            "type": "event_bus",
                        })

        except ClientError as e:
            self.logger.error(f"Error listing EventBridge event buses: {str(e)}")

        try:
            # List rules on default bus
            rule_paginator = events.get_paginator("list_rules")
            for page in rule_paginator.paginate():
                for rule in page.get("Rules", []):
                    resources.append({
                        "id": rule["Arn"],
                        "name": rule["Name"],
                        "type": "rule",
                        "event_bus": rule.get("EventBusName", "default"),
                    })

        except ClientError as e:
            self.logger.error(f"Error listing EventBridge rules: {str(e)}")

        return resources

    def is_default_resource(self, resource: Dict[str, Any]) -> bool:
        """Check if resource is a default resource."""
        # Skip rules on default event bus that might be AWS managed
        if resource.get("type") == "rule":
            event_bus = resource.get("event_bus", "default")
            if event_bus == "default":
                # Could add logic to skip AWS-managed rules
                return False
        return False

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete an EventBridge resource."""
        events = self.session.client("events")
        resource_type = resource.get("type")
        resource_name = resource.get("name")

        try:
            if resource_type == "rule":
                # Remove targets first
                event_bus = resource.get("event_bus", "default")
                try:
                    targets = events.list_targets_by_rule(
                        Rule=resource_name,
                        EventBusName=event_bus
                    )
                    target_ids = [t["Id"] for t in targets.get("Targets", [])]
                    if target_ids:
                        events.remove_targets(
                            Rule=resource_name,
                            EventBusName=event_bus,
                            Ids=target_ids
                        )
                except ClientError:
                    pass
                
                # Delete rule
                events.delete_rule(Name=resource_name, EventBusName=event_bus)
                return True

            elif resource_type == "event_bus":
                events.delete_event_bus(Name=resource_name)
                return True

            return False

        except ClientError as e:
            self.logger.error(
                f"Error deleting EventBridge {resource_type} {resource_name}: {str(e)}"
            )
            return False
