"""CodePipeline resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class CodePipelineHandler(ResourceHandler):
    """Handler for CodePipeline pipelines."""

    @property
    def service_name(self) -> str:
        return "codepipeline"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all CodePipeline pipelines."""
        codepipeline = self.session.client("codepipeline")
        resources = []

        try:
            paginator = codepipeline.get_paginator("list_pipelines")
            for page in paginator.paginate():
                for pipeline in page.get("pipelines", []):
                    resources.append({
                        "id": pipeline["name"],
                        "name": pipeline["name"],
                        "type": "pipeline",
                    })

        except ClientError as e:
            self.logger.error(f"Error listing CodePipeline pipelines: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a CodePipeline pipeline."""
        codepipeline = self.session.client("codepipeline")
        pipeline_name = resource.get("name")

        try:
            codepipeline.delete_pipeline(name=pipeline_name)
            return True
        except ClientError as e:
            self.logger.error(
                f"Error deleting CodePipeline pipeline {pipeline_name}: {str(e)}"
            )
            return False
