"""Kinesis resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class KinesisHandler(ResourceHandler):
    """Handler for Kinesis streams."""

    @property
    def service_name(self) -> str:
        return "kinesis"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all Kinesis streams."""
        kinesis = self.session.client("kinesis")
        resources = []

        try:
            paginator = kinesis.get_paginator("list_streams")
            for page in paginator.paginate():
                for stream_name in page.get("StreamNames", []):
                    resources.append({
                        "id": stream_name,
                        "name": stream_name,
                        "type": "stream",
                    })

        except ClientError as e:
            self.logger.error(f"Error listing Kinesis streams: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a Kinesis stream."""
        kinesis = self.session.client("kinesis")
        stream_name = resource.get("name")

        try:
            kinesis.delete_stream(
                StreamName=stream_name,
                EnforceConsumerDeletion=True  # Force delete consumers
            )
            return True
        except ClientError as e:
            self.logger.error(
                f"Error deleting Kinesis stream {stream_name}: {str(e)}"
            )
            return False
