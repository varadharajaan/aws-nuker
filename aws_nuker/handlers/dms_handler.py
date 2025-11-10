"""Handler for DMS resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class DmsHandler(ResourceHandler):
    """Handler for DMS resources."""

    @property
    def service_name(self) -> str:
        return "dms"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all DMS resources."""
        client = self.session.client("dms")
        resources = []

        try:
            paginator = client.get_paginator("describe_replication_instances")
            for page in paginator.paginate():
                for item in page.get("ReplicationInstances", []):
                    resources.append({
                        "id": item.get("ReplicationInstanceArn", ""),
                        "name": item.get("ReplicationInstanceIdentifier", ""),
                        "type": "instance",
                    })
        except ClientError as e:
            self.logger.error(f"Error listing DMS resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a DMS resource."""
        client = self.session.client("dms")
        resource_id = resource.get("id")

        try:
            client.delete_replication_instance(ReplicationInstanceArn=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting DMS resource {resource_id}: {str(e)}")
            return False
