"""Timestream resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class TimestreamHandler(ResourceHandler):
    """Handler for Amazon Timestream resources."""

    @property
    def service_name(self) -> str:
        return "timestream"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all Timestream resources."""
        # Timestream has two services: timestream-write and timestream-query
        timestream_write = self.session.client("timestream-write")
        resources = []

        try:
            # List databases
            paginator = timestream_write.get_paginator("list_databases")
            for page in paginator.paginate():
                for database in page.get("Databases", []):
                    db_name = database["DatabaseName"]
                    resources.append({
                        "id": database["Arn"],
                        "name": db_name,
                        "type": "database",
                    })

                    # List tables in this database
                    try:
                        table_paginator = timestream_write.get_paginator("list_tables")
                        for table_page in table_paginator.paginate(DatabaseName=db_name):
                            for table in table_page.get("Tables", []):
                                resources.append({
                                    "id": table["Arn"],
                                    "name": table["TableName"],
                                    "type": "table",
                                    "database_name": db_name,
                                })
                    except ClientError:
                        pass

        except ClientError as e:
            self.logger.error(f"Error listing Timestream databases: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a Timestream resource."""
        timestream_write = self.session.client("timestream-write")
        resource_type = resource.get("type")
        resource_name = resource.get("name")

        try:
            if resource_type == "table":
                db_name = resource.get("database_name")
                timestream_write.delete_table(
                    DatabaseName=db_name,
                    TableName=resource_name
                )
                return True

            elif resource_type == "database":
                timestream_write.delete_database(DatabaseName=resource_name)
                return True

            return False

        except ClientError as e:
            self.logger.error(
                f"Error deleting Timestream {resource_type} {resource_name}: {str(e)}"
            )
            return False
