"""STS resource handler."""

from typing import List, Dict, Any

from ..base_handler import ResourceHandler


class STSHandler(ResourceHandler):
    """Handler for AWS Security Token Service resources."""

    @property
    def service_name(self) -> str:
        return "sts"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List STS resources."""
        # STS doesn't have persistent resources to clean up
        # It only provides temporary credentials
        return []

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete STS resources."""
        # STS temporary credentials expire automatically - nothing to delete
        # Return True since there's no actual deletion needed
        return True
