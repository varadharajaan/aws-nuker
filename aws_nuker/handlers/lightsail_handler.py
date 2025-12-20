"""Lightsail resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class LightsailHandler(ResourceHandler):
    """Handler for Lightsail instances and databases."""

    @property
    def service_name(self) -> str:
        return "lightsail"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all Lightsail resources."""
        lightsail = self.session.client("lightsail")
        resources = []

        try:
            # List instances
            paginator = lightsail.get_paginator("get_instances")
            for page in paginator.paginate():
                for instance in page.get("instances", []):
                    resources.append({
                        "id": instance["arn"],
                        "name": instance["name"],
                        "type": "instance",
                        "state": instance.get("state", {}).get("name", ""),
                    })

        except ClientError as e:
            self.logger.error(f"Error listing Lightsail instances: {str(e)}")

        try:
            # List databases
            paginator = lightsail.get_paginator("get_relational_databases")
            for page in paginator.paginate():
                for db in page.get("relationalDatabases", []):
                    resources.append({
                        "id": db["arn"],
                        "name": db["name"],
                        "type": "database",
                        "state": db.get("state", ""),
                    })

        except ClientError as e:
            self.logger.error(f"Error listing Lightsail databases: {str(e)}")

        try:
            # List load balancers
            response = lightsail.get_load_balancers()
            for lb in response.get("loadBalancers", []):
                resources.append({
                    "id": lb["arn"],
                    "name": lb["name"],
                    "type": "load_balancer",
                    "state": lb.get("state", ""),
                })

        except ClientError as e:
            self.logger.error(f"Error listing Lightsail load balancers: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a Lightsail resource."""
        lightsail = self.session.client("lightsail")
        resource_type = resource.get("type")
        resource_name = resource.get("name")

        try:
            if resource_type == "instance":
                lightsail.delete_instance(instanceName=resource_name)
                return True

            elif resource_type == "database":
                lightsail.delete_relational_database(
                    relationalDatabaseName=resource_name,
                    skipFinalSnapshot=True
                )
                return True

            elif resource_type == "load_balancer":
                lightsail.delete_load_balancer(loadBalancerName=resource_name)
                return True

            return False

        except ClientError as e:
            self.logger.error(
                f"Error deleting Lightsail {resource_type} {resource_name}: {str(e)}"
            )
            return False
