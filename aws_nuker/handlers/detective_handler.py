"""Handler for DETECTIVE resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class DetectiveHandler(ResourceHandler):
    """Handler for DETECTIVE resources."""

    @property
    def service_name(self) -> str:
        return "detective"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all DETECTIVE resources."""
        client = self.session.client("detective")
        resources = []

        try:
            paginator = client.get_paginator("list_graphs")
            for page in paginator.paginate():
                for item in page.get("GraphList", []):
                    resources.append({
                        "id": item.get("Arn", ""),
                        "name": item.get("Arn", ""),
                        "type": "graph",
                    })
        except ClientError as e:
            self.logger.error(f"Error listing DETECTIVE resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a DETECTIVE resource."""
        client = self.session.client("detective")
        resource_id = resource.get("id")

        try:
            client.delete_graph(GraphArn=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting DETECTIVE resource {resource_id}: {str(e)}")
            return False
