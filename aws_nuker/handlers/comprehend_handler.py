"""Handler for COMPREHEND resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class ComprehendHandler(ResourceHandler):
    """Handler for COMPREHEND resources."""

    @property
    def service_name(self) -> str:
        return "comprehend"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all COMPREHEND resources."""
        client = self.session.client("comprehend")
        resources = []

        try:
            paginator = client.get_paginator("list_document_classifiers")
            for page in paginator.paginate():
                for item in page.get("DocumentClassifierPropertiesList", []):
                    resources.append({
                        "id": item.get("DocumentClassifierArn", ""),
                        "name": item.get("DocumentClassifierArn", ""),
                        "type": "classifier",
                    })
        except ClientError as e:
            self.logger.error(f"Error listing COMPREHEND resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a COMPREHEND resource."""
        client = self.session.client("comprehend")
        resource_id = resource.get("id")

        try:
            client.delete_document_classifier(DocumentClassifierArn=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting COMPREHEND resource {resource_id}: {str(e)}")
            return False
