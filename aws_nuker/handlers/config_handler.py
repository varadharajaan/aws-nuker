"""AWS Config resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class ConfigHandler(ResourceHandler):
    """Handler for AWS Config resources."""

    @property
    def service_name(self) -> str:
        return "config"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all AWS Config resources."""
        config = self.session.client("config")
        resources = []

        try:
            # List configuration recorders
            recorders = config.describe_configuration_recorders()
            for recorder in recorders.get("ConfigurationRecorders", []):
                resources.append({
                    "id": recorder["name"],
                    "name": recorder["name"],
                    "type": "configuration_recorder",
                })

        except ClientError as e:
            self.logger.error(f"Error listing Config recorders: {str(e)}")

        try:
            # List delivery channels
            channels = config.describe_delivery_channels()
            for channel in channels.get("DeliveryChannels", []):
                resources.append({
                    "id": channel["name"],
                    "name": channel["name"],
                    "type": "delivery_channel",
                })

        except ClientError as e:
            self.logger.error(f"Error listing Config delivery channels: {str(e)}")

        try:
            # List configuration aggregators
            aggregators = config.describe_configuration_aggregators()
            for aggregator in aggregators.get("ConfigurationAggregators", []):
                resources.append({
                    "id": aggregator["ConfigurationAggregatorName"],
                    "name": aggregator["ConfigurationAggregatorName"],
                    "type": "configuration_aggregator",
                })

        except ClientError as e:
            self.logger.error(f"Error listing Config aggregators: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete an AWS Config resource."""
        config = self.session.client("config")
        resource_type = resource.get("type")
        resource_name = resource.get("name")

        try:
            if resource_type == "configuration_recorder":
                config.delete_configuration_recorder(
                    ConfigurationRecorderName=resource_name
                )
                return True

            elif resource_type == "delivery_channel":
                config.delete_delivery_channel(DeliveryChannelName=resource_name)
                return True

            elif resource_type == "configuration_aggregator":
                config.delete_configuration_aggregator(
                    ConfigurationAggregatorName=resource_name
                )
                return True

            return False

        except ClientError as e:
            self.logger.error(
                f"Error deleting Config {resource_type} {resource_name}: {str(e)}"
            )
            return False
