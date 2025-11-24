"""MQ (Amazon MQ) resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class MQHandler(ResourceHandler):
    """Handler for Amazon MQ brokers."""

    @property
    def service_name(self) -> str:
        return "mq"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all Amazon MQ brokers."""
        mq = self.session.client("mq")
        resources = []

        try:
            # List brokers
            paginator = mq.get_paginator("list_brokers")
            for page in paginator.paginate():
                for broker in page.get("BrokerSummaries", []):
                    resources.append({
                        "id": broker["BrokerId"],
                        "name": broker.get("BrokerName", broker["BrokerId"]),
                        "type": "broker",
                        "state": broker.get("BrokerState", ""),
                    })

        except ClientError as e:
            self.logger.error(f"Error listing Amazon MQ brokers: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete an Amazon MQ broker."""
        mq = self.session.client("mq")
        broker_id = resource.get("id")

        try:
            mq.delete_broker(BrokerId=broker_id)
            return True
        except ClientError as e:
            self.logger.error(
                f"Error deleting Amazon MQ broker {broker_id}: {str(e)}"
            )
            return False
