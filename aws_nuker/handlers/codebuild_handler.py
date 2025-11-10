"""Handler for CODEBUILD resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class CodebuildHandler(ResourceHandler):
    """Handler for CODEBUILD resources."""

    @property
    def service_name(self) -> str:
        return "codebuild"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all CODEBUILD resources."""
        client = self.session.client("codebuild")
        resources = []

        try:
            response = client.list_projects()
            for project_name in response.get("projects", []):
                resources.append({
                    "id": project_name,
                    "name": project_name,
                    "type": "project",
                })
        except ClientError as e:
            self.logger.error(f"Error listing CODEBUILD resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a CODEBUILD resource."""
        client = self.session.client("codebuild")
        resource_id = resource.get("id")

        try:
            client.delete_project(name=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting CODEBUILD resource {resource_id}: {str(e)}")
            return False
