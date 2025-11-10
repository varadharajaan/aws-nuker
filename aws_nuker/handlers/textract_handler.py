"""Handler for TEXTRACT resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class TextractHandler(ResourceHandler):
    """Handler for TEXTRACT resources."""

    @property
    def service_name(self) -> str:
        return "textract"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all TEXTRACT resources."""
        client = self.session.client("textract")
        resources = []

        try:
            paginator = client.get_paginator("list_adapters")
            for page in paginator.paginate():
                for item in page.get("Adapters", []):
                    resources.append({
                        "id": item.get("AdapterId", ""),
                        "name": item.get("AdapterName", ""),
                        "type": "adapter",
                    })
        except ClientError as e:
            self.logger.error(f"Error listing TEXTRACT resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a TEXTRACT resource."""
        client = self.session.client("textract")
        resource_id = resource.get("id")

        try:
            client.delete_adapter(AdapterId=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting TEXTRACT resource {resource_id}: {str(e)}")
            return False
