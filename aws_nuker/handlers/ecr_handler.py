"""ECR resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class ECRHandler(ResourceHandler):
    """Handler for Elastic Container Registry repositories."""

    @property
    def service_name(self) -> str:
        return "ecr"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all ECR repositories."""
        ecr = self.session.client("ecr")
        resources = []

        try:
            paginator = ecr.get_paginator("describe_repositories")
            for page in paginator.paginate():
                for repo in page.get("repositories", []):
                    resources.append({
                        "id": repo["repositoryArn"],
                        "name": repo["repositoryName"],
                        "type": "repository",
                    })

        except ClientError as e:
            self.logger.error(f"Error listing ECR repositories: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete an ECR repository."""
        ecr = self.session.client("ecr")
        repo_name = resource.get("name")

        try:
            # Delete repository with force to remove all images
            ecr.delete_repository(
                repositoryName=repo_name,
                force=True  # Delete even if it contains images
            )
            return True
        except ClientError as e:
            self.logger.error(
                f"Error deleting ECR repository {repo_name}: {str(e)}"
            )
            return False
