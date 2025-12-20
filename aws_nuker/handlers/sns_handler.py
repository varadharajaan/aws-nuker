"""SNS resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class SNSHandler(ResourceHandler):
    """Handler for SNS topics."""

    @property
    def service_name(self) -> str:
        return "sns"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all SNS topics."""
        sns = self.session.client("sns")
        resources = []

        try:
            paginator = sns.get_paginator("list_topics")
            for page in paginator.paginate():
                for topic in page.get("Topics", []):
                    topic_arn = topic["TopicArn"]
                    topic_name = topic_arn.split(":")[-1]
                    resources.append({
                        "id": topic_arn,
                        "name": topic_name,
                        "type": "topic",
                    })

        except ClientError as e:
            self.logger.error(f"Error listing SNS topics: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete an SNS topic."""
        sns = self.session.client("sns")
        topic_arn = resource.get("id")

        try:
            sns.delete_topic(TopicArn=topic_arn)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting SNS topic {topic_arn}: {str(e)}")
            return False
