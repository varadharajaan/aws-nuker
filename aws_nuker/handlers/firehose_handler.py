"""Handler for FIREHOSE resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class FirehoseHandler(ResourceHandler):
    """Handler for FIREHOSE resources."""

    @property
    def service_name(self) -> str:
        return "firehose"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all FIREHOSE resources."""
        client = self.session.client("firehose")
        resources = []

        try:
            response = client.list_delivery_streams()
            for item in response.get("DeliveryStreamNames", []):
                resources.append({
                    "id": item.get("", ""),
                    "name": item.get("", ""),
                    "type": "stream",
                })
        except ClientError as e:
            self.logger.error(f"Error listing FIREHOSE resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a FIREHOSE resource."""
        client = self.session.client("firehose")
        resource_id = resource.get("id")

        try:
            client.delete_delivery_stream(DeliveryStreamName=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting FIREHOSE resource {resource_id}: {str(e)}")
            return False
