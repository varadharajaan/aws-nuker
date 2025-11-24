"""CodeBuild resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class CodeBuildHandler(ResourceHandler):
    """Handler for CodeBuild projects."""

    @property
    def service_name(self) -> str:
        return "codebuild"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all CodeBuild projects."""
        codebuild = self.session.client("codebuild")
        resources = []

        try:
            paginator = codebuild.get_paginator("list_projects")
            for page in paginator.paginate():
                project_names = page.get("projects", [])
                
                # Get project details in batches
                if project_names:
                    # Batch get projects (max 100 at a time)
                    for i in range(0, len(project_names), 100):
                        batch = project_names[i:i + 100]
                        try:
                            response = codebuild.batch_get_projects(names=batch)
                            for project in response.get("projects", []):
                                resources.append({
                                    "id": project["arn"],
                                    "name": project["name"],
                                    "type": "project",
                                })
                        except ClientError:
                            # If batch get fails, add projects with names only
                            for name in batch:
                                resources.append({
                                    "id": name,
                                    "name": name,
                                    "type": "project",
                                })

        except ClientError as e:
            self.logger.error(f"Error listing CodeBuild projects: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a CodeBuild project."""
        codebuild = self.session.client("codebuild")
        project_name = resource.get("name")

        try:
            codebuild.delete_project(name=project_name)
            return True
        except ClientError as e:
            self.logger.error(
                f"Error deleting CodeBuild project {project_name}: {str(e)}"
            )
            return False
