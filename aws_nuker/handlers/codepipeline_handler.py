"""Handler for CODEPIPELINE resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class CodepipelineHandler(ResourceHandler):
    """Handler for CODEPIPELINE resources."""

    @property
    def service_name(self) -> str:
        return "codepipeline"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all CODEPIPELINE resources."""
        client = self.session.client("codepipeline")
        resources = []

        try:
            paginator = client.get_paginator("list_pipelines")
            for page in paginator.paginate():
                for item in page.get("pipelines", []):
                    resources.append({
                        "id": item.get("name", ""),
                        "name": item.get("name", ""),
                        "type": "pipeline",
                    })
        except ClientError as e:
            self.logger.error(f"Error listing CODEPIPELINE resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a CODEPIPELINE resource."""
        client = self.session.client("codepipeline")
        resource_id = resource.get("id")

        try:
            client.delete_pipeline(name=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting CODEPIPELINE resource {resource_id}: {str(e)}")
            return False
