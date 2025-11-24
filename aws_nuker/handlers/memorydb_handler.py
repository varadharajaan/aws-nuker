"""MemoryDB resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class MemoryDBHandler(ResourceHandler):
    """Handler for Amazon MemoryDB for Redis resources."""

    @property
    def service_name(self) -> str:
        return "memorydb"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all MemoryDB resources."""
        memorydb = self.session.client("memorydb")
        resources = []

        try:
            # List clusters
            paginator = memorydb.get_paginator("describe_clusters")
            for page in paginator.paginate():
                for cluster in page.get("Clusters", []):
                    resources.append({
                        "id": cluster["ARN"],
                        "name": cluster["Name"],
                        "type": "cluster",
                        "status": cluster.get("Status", ""),
                    })

        except ClientError as e:
            self.logger.error(f"Error listing MemoryDB clusters: {str(e)}")

        try:
            # List parameter groups (skip default)
            paginator = memorydb.get_paginator("describe_parameter_groups")
            for page in paginator.paginate():
                for pg in page.get("ParameterGroups", []):
                    if not pg["Name"].startswith("default."):
                        resources.append({
                            "id": pg["ARN"],
                            "name": pg["Name"],
                            "type": "parameter_group",
                        })

        except ClientError as e:
            self.logger.error(f"Error listing MemoryDB parameter groups: {str(e)}")

        try:
            # List subnet groups (skip default)
            paginator = memorydb.get_paginator("describe_subnet_groups")
            for page in paginator.paginate():
                for sg in page.get("SubnetGroups", []):
                    if sg["Name"] != "default":
                        resources.append({
                            "id": sg["ARN"],
                            "name": sg["Name"],
                            "type": "subnet_group",
                        })

        except ClientError as e:
            self.logger.error(f"Error listing MemoryDB subnet groups: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a MemoryDB resource."""
        memorydb = self.session.client("memorydb")
        resource_type = resource.get("type")
        resource_name = resource.get("name")

        try:
            if resource_type == "cluster":
                memorydb.delete_cluster(ClusterName=resource_name)
                return True

            elif resource_type == "parameter_group":
                memorydb.delete_parameter_group(ParameterGroupName=resource_name)
                return True

            elif resource_type == "subnet_group":
                memorydb.delete_subnet_group(SubnetGroupName=resource_name)
                return True

            return False

        except ClientError as e:
            self.logger.error(
                f"Error deleting MemoryDB {resource_type} {resource_name}: {str(e)}"
            )
            return False
