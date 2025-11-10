"""Handler for MQ resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class MqHandler(ResourceHandler):
    """Handler for MQ resources."""

    @property
    def service_name(self) -> str:
        return "mq"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all MQ resources."""
        client = self.session.client("mq")
        resources = []

        try:
            response = client.list_brokers()
            for item in response.get("BrokerSummaries", []):
                resources.append({
                    "id": item.get("BrokerId", ""),
                    "name": item.get("BrokerName", ""),
                    "type": "broker",
                })
        except ClientError as e:
            self.logger.error(f"Error listing MQ resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a MQ resource."""
        client = self.session.client("mq")
        resource_id = resource.get("id")

        try:
            client.delete_broker(BrokerId=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting MQ resource {resource_id}: {str(e)}")
            return False
