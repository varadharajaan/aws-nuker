"""Handler for CODEARTIFACT resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class CodeartifactHandler(ResourceHandler):
    """Handler for CODEARTIFACT resources."""

    @property
    def service_name(self) -> str:
        return "codeartifact"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all CODEARTIFACT resources."""
        client = self.session.client("codeartifact")
        resources = []

        try:
            paginator = client.get_paginator("list_domains")
            for page in paginator.paginate():
                for item in page.get("domains", []):
                    resources.append({
                        "id": item.get("name", ""),
                        "name": item.get("name", ""),
                        "type": "domain",
                    })
        except ClientError as e:
            self.logger.error(f"Error listing CODEARTIFACT resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a CODEARTIFACT resource."""
        client = self.session.client("codeartifact")
        resource_id = resource.get("id")

        try:
            client.delete_domain(domain=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting CODEARTIFACT resource {resource_id}: {str(e)}")
            return False
