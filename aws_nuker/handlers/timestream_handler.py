"""Handler for TIMESTREAM resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class TimestreamHandler(ResourceHandler):
    """Handler for TIMESTREAM resources."""

    @property
    def service_name(self) -> str:
        return "timestream"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all TIMESTREAM resources."""
        client = self.session.client("timestream-write")
        resources = []

        try:
            paginator = client.get_paginator("list_databases")
            for page in paginator.paginate():
                for item in page.get("Databases", []):
                    resources.append({
                        "id": item.get("DatabaseName", ""),
                        "name": item.get("DatabaseName", ""),
                        "type": "database",
                    })
        except ClientError as e:
            self.logger.error(f"Error listing TIMESTREAM resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a TIMESTREAM resource."""
        client = self.session.client("timestream-write")
        resource_id = resource.get("id")

        try:
            client.delete_database(DatabaseName=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting TIMESTREAM resource {resource_id}: {str(e)}")
            return False
