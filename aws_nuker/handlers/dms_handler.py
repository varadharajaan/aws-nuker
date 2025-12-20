"""DMS (Database Migration Service) resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class DMSHandler(ResourceHandler):
    """Handler for DMS replication instances and endpoints."""

    @property
    def service_name(self) -> str:
        return "dms"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all DMS resources."""
        dms = self.session.client("dms")
        resources = []

        try:
            # List replication instances
            paginator = dms.get_paginator("describe_replication_instances")
            for page in paginator.paginate():
                for instance in page.get("ReplicationInstances", []):
                    resources.append({
                        "id": instance["ReplicationInstanceArn"],
                        "name": instance["ReplicationInstanceIdentifier"],
                        "type": "replication_instance",
                        "status": instance.get("ReplicationInstanceStatus", ""),
                    })

        except ClientError as e:
            self.logger.error(f"Error listing DMS replication instances: {str(e)}")

        try:
            # List endpoints
            paginator = dms.get_paginator("describe_endpoints")
            for page in paginator.paginate():
                for endpoint in page.get("Endpoints", []):
                    resources.append({
                        "id": endpoint["EndpointArn"],
                        "name": endpoint["EndpointIdentifier"],
                        "type": "endpoint",
                        "endpoint_type": endpoint.get("EndpointType", ""),
                    })

        except ClientError as e:
            self.logger.error(f"Error listing DMS endpoints: {str(e)}")

        try:
            # List replication tasks
            paginator = dms.get_paginator("describe_replication_tasks")
            for page in paginator.paginate():
                for task in page.get("ReplicationTasks", []):
                    resources.append({
                        "id": task["ReplicationTaskArn"],
                        "name": task["ReplicationTaskIdentifier"],
                        "type": "replication_task",
                        "status": task.get("Status", ""),
                    })

        except ClientError as e:
            self.logger.error(f"Error listing DMS replication tasks: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a DMS resource."""
        dms = self.session.client("dms")
        resource_type = resource.get("type")
        resource_arn = resource.get("id")

        try:
            if resource_type == "replication_task":
                dms.delete_replication_task(ReplicationTaskArn=resource_arn)
                return True

            elif resource_type == "endpoint":
                dms.delete_endpoint(EndpointArn=resource_arn)
                return True

            elif resource_type == "replication_instance":
                dms.delete_replication_instance(ReplicationInstanceArn=resource_arn)
                return True

            return False

        except ClientError as e:
            self.logger.error(
                f"Error deleting DMS {resource_type} {resource_arn}: {str(e)}"
            )
            return False
