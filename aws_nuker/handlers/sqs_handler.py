"""SQS resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class SQSHandler(ResourceHandler):
    """Handler for SQS queues."""

    @property
    def service_name(self) -> str:
        return "sqs"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all SQS queues."""
        sqs = self.session.client("sqs")
        resources = []

        try:
            paginator = sqs.get_paginator("list_queues")
            for page in paginator.paginate():
                for queue_url in page.get("QueueUrls", []):
                    queue_name = queue_url.split("/")[-1]
                    resources.append({
                        "id": queue_url,
                        "name": queue_name,
                        "type": "queue",
                    })

        except ClientError as e:
            self.logger.error(f"Error listing SQS queues: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete an SQS queue."""
        sqs = self.session.client("sqs")
        queue_url = resource.get("id")

        try:
            sqs.delete_queue(QueueUrl=queue_url)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting SQS queue {queue_url}: {str(e)}")
            return False
