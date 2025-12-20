"""Textract resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class TextractHandler(ResourceHandler):
    """Handler for Amazon Textract resources."""

    @property
    def service_name(self) -> str:
        return "textract"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all Textract resources."""
        # Note: Textract doesn't have persistent resources like collections
        # It's a stateless API service. Resources are jobs that complete.
        # We'll list adapters (custom models) if any exist
        textract = self.session.client("textract")
        resources = []

        try:
            # List adapters (custom models for document analysis)
            paginator = textract.get_paginator("list_adapters")
            for page in paginator.paginate():
                for adapter in page.get("Adapters", []):
                    resources.append({
                        "id": adapter["AdapterId"],
                        "name": adapter.get("AdapterName", adapter["AdapterId"]),
                        "type": "adapter",
                    })

        except ClientError as e:
            # Adapters might not be available in all regions
            if e.response.get("Error", {}).get("Code") != "InvalidParameterException":
                self.logger.error(f"Error listing Textract adapters: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a Textract resource."""
        textract = self.session.client("textract")
        resource_type = resource.get("type")
        resource_id = resource.get("id")

        try:
            if resource_type == "adapter":
                textract.delete_adapter(AdapterId=resource_id)
                return True

            return False

        except ClientError as e:
            self.logger.error(
                f"Error deleting Textract {resource_type} {resource_id}: {str(e)}"
            )
            return False
