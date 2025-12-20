"""Firehose resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class FirehoseHandler(ResourceHandler):
    """Handler for Kinesis Data Firehose delivery streams."""

    @property
    def service_name(self) -> str:
        return "firehose"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all Firehose delivery streams."""
        firehose = self.session.client("firehose")
        resources = []

        try:
            # List delivery streams
            response = firehose.list_delivery_streams(Limit=100)
            stream_names = response.get("DeliveryStreamNames", [])

            # Get details for each stream
            for stream_name in stream_names:
                try:
                    response = firehose.describe_delivery_stream(
                        DeliveryStreamName=stream_name
                    )
                    stream = response.get("DeliveryStreamDescription", {})
                    resources.append({
                        "id": stream.get("DeliveryStreamARN", stream_name),
                        "name": stream_name,
                        "type": "delivery_stream",
                        "status": stream.get("DeliveryStreamStatus", ""),
                    })
                except ClientError:
                    # If we can't describe, add it anyway
                    resources.append({
                        "id": stream_name,
                        "name": stream_name,
                        "type": "delivery_stream",
                    })

        except ClientError as e:
            self.logger.error(f"Error listing Firehose delivery streams: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a Firehose delivery stream."""
        firehose = self.session.client("firehose")
        stream_name = resource.get("name")

        try:
            firehose.delete_delivery_stream(
                DeliveryStreamName=stream_name,
                AllowForceDelete=self.force
            )
            return True
        except ClientError as e:
            self.logger.error(
                f"Error deleting Firehose delivery stream {stream_name}: {str(e)}"
            )
            return False
