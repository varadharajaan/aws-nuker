"""Handler for STS resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class StsHandler(ResourceHandler):
    """Handler for STS resources."""

    @property
    def service_name(self) -> str:
        return "sts"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all STS resources."""
        client = self.session.client("sts")
        resources = []

        # STS doesn't have deletable resources
        return []

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a STS resource."""
        client = self.session.client("sts")
        resource_id = resource.get("id")

        # STS doesn't support deletion
        return False
