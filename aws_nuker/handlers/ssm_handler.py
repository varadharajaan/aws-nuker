"""Handler for SSM resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class SsmHandler(ResourceHandler):
    """Handler for SSM resources."""

    @property
    def service_name(self) -> str:
        return "ssm"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all SSM resources."""
        client = self.session.client("ssm")
        resources = []

        try:
            paginator = client.get_paginator("describe_parameters")
            for page in paginator.paginate():
                for item in page.get("Parameters", []):
                    resources.append({
                        "id": item.get("Name", ""),
                        "name": item.get("Name", ""),
                        "type": "parameter",
                    })
        except ClientError as e:
            self.logger.error(f"Error listing SSM resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a SSM resource."""
        client = self.session.client("ssm")
        resource_id = resource.get("id")

        try:
            client.delete_parameter(Name=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting SSM resource {resource_id}: {str(e)}")
            return False
