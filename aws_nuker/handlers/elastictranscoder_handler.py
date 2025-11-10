"""Handler for ELASTICTRANSCODER resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class ElastictranscoderHandler(ResourceHandler):
    """Handler for ELASTICTRANSCODER resources."""

    @property
    def service_name(self) -> str:
        return "elastictranscoder"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all ELASTICTRANSCODER resources."""
        client = self.session.client("elastictranscoder")
        resources = []

        try:
            paginator = client.get_paginator("list_pipelines")
            for page in paginator.paginate():
                for item in page.get("Pipelines", []):
                    resources.append({
                        "id": item.get("Id", ""),
                        "name": item.get("Name", ""),
                        "type": "pipeline",
                    })
        except ClientError as e:
            self.logger.error(f"Error listing ELASTICTRANSCODER resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a ELASTICTRANSCODER resource."""
        client = self.session.client("elastictranscoder")
        resource_id = resource.get("id")

        try:
            client.delete_pipeline(Id=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting ELASTICTRANSCODER resource {resource_id}: {str(e)}")
            return False
