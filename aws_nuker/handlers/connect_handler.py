"""Connect resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class ConnectHandler(ResourceHandler):
    """Handler for Amazon Connect resources."""

    @property
    def service_name(self) -> str:
        return "connect"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all Connect instances."""
        connect = self.session.client("connect")
        resources = []

        try:
            # List instances
            paginator = connect.get_paginator("list_instances")
            for page in paginator.paginate():
                for instance in page.get("InstanceSummaryList", []):
                    resources.append({
                        "id": instance["Id"],
                        "name": instance.get("InstanceAlias", instance["Id"]),
                        "type": "instance",
                        "arn": instance["Arn"],
                    })

        except ClientError as e:
            self.logger.error(f"Error listing Connect instances: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a Connect instance."""
        connect = self.session.client("connect")
        instance_id = resource.get("id")

        try:
            connect.delete_instance(InstanceId=instance_id)
            return True
        except ClientError as e:
            self.logger.error(
                f"Error deleting Connect instance {instance_id}: {str(e)}"
            )
            return False
