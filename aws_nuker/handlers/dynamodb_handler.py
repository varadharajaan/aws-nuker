"""DynamoDB resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class DynamoDBHandler(ResourceHandler):
    """Handler for DynamoDB tables."""

    @property
    def service_name(self) -> str:
        return "dynamodb"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all DynamoDB tables."""
        dynamodb = self.session.client("dynamodb")
        resources = []

        try:
            paginator = dynamodb.get_paginator("list_tables")
            for page in paginator.paginate():
                for table_name in page.get("TableNames", []):
                    resources.append({
                        "id": table_name,
                        "name": table_name,
                        "type": "table",
                    })

        except ClientError as e:
            self.logger.error(f"Error listing DynamoDB tables: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a DynamoDB table."""
        dynamodb = self.session.client("dynamodb")
        table_name = resource.get("name")

        try:
            dynamodb.delete_table(TableName=table_name)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting DynamoDB table {table_name}: {str(e)}")
            return False
