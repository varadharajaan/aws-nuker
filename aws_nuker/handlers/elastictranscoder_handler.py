"""Elastic Transcoder resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class ElasticTranscoderHandler(ResourceHandler):
    """Handler for Amazon Elastic Transcoder resources."""

    @property
    def service_name(self) -> str:
        return "elastictranscoder"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all Elastic Transcoder resources."""
        elastictranscoder = self.session.client("elastictranscoder")
        resources = []

        try:
            # List pipelines
            paginator = elastictranscoder.get_paginator("list_pipelines")
            for page in paginator.paginate():
                for pipeline in page.get("Pipelines", []):
                    resources.append({
                        "id": pipeline["Id"],
                        "name": pipeline.get("Name", pipeline["Id"]),
                        "type": "pipeline",
                        "status": pipeline.get("Status", ""),
                    })

        except ClientError as e:
            self.logger.error(f"Error listing Elastic Transcoder pipelines: {str(e)}")

        try:
            # List presets (skip system presets)
            paginator = elastictranscoder.get_paginator("list_presets")
            for page in paginator.paginate():
                for preset in page.get("Presets", []):
                    # Skip system presets (they start with specific patterns)
                    if preset.get("Type") != "System":
                        resources.append({
                            "id": preset["Id"],
                            "name": preset.get("Name", preset["Id"]),
                            "type": "preset",
                        })

        except ClientError as e:
            self.logger.error(f"Error listing Elastic Transcoder presets: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete an Elastic Transcoder resource."""
        elastictranscoder = self.session.client("elastictranscoder")
        resource_type = resource.get("type")
        resource_id = resource.get("id")

        try:
            if resource_type == "pipeline":
                elastictranscoder.delete_pipeline(Id=resource_id)
                return True

            elif resource_type == "preset":
                elastictranscoder.delete_preset(Id=resource_id)
                return True

            return False

        except ClientError as e:
            self.logger.error(
                f"Error deleting Elastic Transcoder {resource_type} {resource_id}: {str(e)}"
            )
            return False
