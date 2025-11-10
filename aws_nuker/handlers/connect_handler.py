"""Handler for CONNECT resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class ConnectHandler(ResourceHandler):
    """Handler for CONNECT resources."""

    @property
    def service_name(self) -> str:
        return "connect"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all CONNECT resources."""
        client = self.session.client("connect")
        resources = []

        try:
            paginator = client.get_paginator("list_instances")
            for page in paginator.paginate():
                for item in page.get("InstanceSummaryList", []):
                    resources.append({
                        "id": item.get("Id", ""),
                        "name": item.get("InstanceAlias", ""),
                        "type": "instance",
                    })
        except ClientError as e:
            self.logger.error(f"Error listing CONNECT resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a CONNECT resource."""
        client = self.session.client("connect")
        resource_id = resource.get("id")

        try:
            client.delete_instance(Id=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting CONNECT resource {resource_id}: {str(e)}")
            return False
