"""Handler for SERVERLESSREPO resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class ServerlessrepoHandler(ResourceHandler):
    """Handler for SERVERLESSREPO resources."""

    @property
    def service_name(self) -> str:
        return "serverlessrepo"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all SERVERLESSREPO resources."""
        client = self.session.client("serverlessrepo")
        resources = []

        try:
            paginator = client.get_paginator("list_applications")
            for page in paginator.paginate():
                for item in page.get("Applications", []):
                    resources.append({
                        "id": item.get("ApplicationId", ""),
                        "name": item.get("Name", ""),
                        "type": "application",
                    })
        except ClientError as e:
            self.logger.error(f"Error listing SERVERLESSREPO resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a SERVERLESSREPO resource."""
        client = self.session.client("serverlessrepo")
        resource_id = resource.get("id")

        try:
            client.delete_application(ApplicationId=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting SERVERLESSREPO resource {resource_id}: {str(e)}")
            return False
