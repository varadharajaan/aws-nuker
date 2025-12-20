"""Keyspaces resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class KeyspacesHandler(ResourceHandler):
    """Handler for Amazon Keyspaces (Apache Cassandra) resources."""

    @property
    def service_name(self) -> str:
        return "keyspaces"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all Keyspaces resources."""
        keyspaces = self.session.client("keyspaces")
        resources = []

        try:
            # List keyspaces
            paginator = keyspaces.get_paginator("list_keyspaces")
            for page in paginator.paginate():
                for keyspace in page.get("keyspaces", []):
                    keyspace_name = keyspace["keyspaceName"]
                    # Skip system keyspaces
                    if keyspace_name not in ["system", "system_schema", "system_schema_mcs"]:
                        resources.append({
                            "id": keyspace["resourceArn"],
                            "name": keyspace_name,
                            "type": "keyspace",
                        })

                        # List tables in this keyspace
                        try:
                            table_paginator = keyspaces.get_paginator("list_tables")
                            for table_page in table_paginator.paginate(keyspaceName=keyspace_name):
                                for table in table_page.get("tables", []):
                                    resources.append({
                                        "id": table["resourceArn"],
                                        "name": table["tableName"],
                                        "type": "table",
                                        "keyspace_name": keyspace_name,
                                    })
                        except ClientError:
                            pass

        except ClientError as e:
            self.logger.error(f"Error listing Keyspaces: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a Keyspaces resource."""
        keyspaces = self.session.client("keyspaces")
        resource_type = resource.get("type")
        resource_name = resource.get("name")

        try:
            if resource_type == "table":
                keyspace_name = resource.get("keyspace_name")
                keyspaces.delete_table(
                    keyspaceName=keyspace_name,
                    tableName=resource_name
                )
                return True

            elif resource_type == "keyspace":
                keyspaces.delete_keyspace(keyspaceName=resource_name)
                return True

            return False

        except ClientError as e:
            self.logger.error(
                f"Error deleting Keyspaces {resource_type} {resource_name}: {str(e)}"
            )
            return False
