"""Handler for CODECOMMIT resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class CodecommitHandler(ResourceHandler):
    """Handler for CODECOMMIT resources."""

    @property
    def service_name(self) -> str:
        return "codecommit"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all CODECOMMIT resources."""
        client = self.session.client("codecommit")
        resources = []

        try:
            paginator = client.get_paginator("list_repositories")
            for page in paginator.paginate():
                for item in page.get("repositories", []):
                    resources.append({
                        "id": item.get("repositoryName", ""),
                        "name": item.get("repositoryName", ""),
                        "type": "repository",
                    })
        except ClientError as e:
            self.logger.error(f"Error listing CODECOMMIT resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a CODECOMMIT resource."""
        client = self.session.client("codecommit")
        resource_id = resource.get("id")

        try:
            client.delete_repository(repositoryName=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting CODECOMMIT resource {resource_id}: {str(e)}")
            return False
