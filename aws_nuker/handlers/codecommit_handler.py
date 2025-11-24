"""CodeCommit resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class CodeCommitHandler(ResourceHandler):
    """Handler for CodeCommit repositories."""

    @property
    def service_name(self) -> str:
        return "codecommit"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all CodeCommit repositories."""
        codecommit = self.session.client("codecommit")
        resources = []

        try:
            paginator = codecommit.get_paginator("list_repositories")
            for page in paginator.paginate():
                for repo in page.get("repositories", []):
                    resources.append({
                        "id": repo["repositoryId"],
                        "name": repo["repositoryName"],
                        "type": "repository",
                    })

        except ClientError as e:
            self.logger.error(f"Error listing CodeCommit repositories: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a CodeCommit repository."""
        codecommit = self.session.client("codecommit")
        repo_name = resource.get("name")

        try:
            codecommit.delete_repository(repositoryName=repo_name)
            return True
        except ClientError as e:
            self.logger.error(
                f"Error deleting CodeCommit repository {repo_name}: {str(e)}"
            )
            return False
