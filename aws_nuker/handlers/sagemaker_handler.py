"""Handler for SAGEMAKER resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class SagemakerHandler(ResourceHandler):
    """Handler for SAGEMAKER resources."""

    @property
    def service_name(self) -> str:
        return "sagemaker"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all SAGEMAKER resources."""
        client = self.session.client("sagemaker")
        resources = []

        try:
            paginator = client.get_paginator("list_models")
            for page in paginator.paginate():
                for item in page.get("Models", []):
                    resources.append({
                        "id": item.get("ModelName", ""),
                        "name": item.get("ModelName", ""),
                        "type": "model",
                    })
        except ClientError as e:
            self.logger.error(f"Error listing SAGEMAKER resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a SAGEMAKER resource."""
        client = self.session.client("sagemaker")
        resource_id = resource.get("id")

        try:
            client.delete_model(ModelName=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting SAGEMAKER resource {resource_id}: {str(e)}")
            return False
