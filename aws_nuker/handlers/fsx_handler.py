"""FSx resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class FSxHandler(ResourceHandler):
    """Handler for FSx file systems."""

    @property
    def service_name(self) -> str:
        return "fsx"

    def _get_tag_name(self, tags: List[Dict[str, str]]) -> str:
        """Extract name from tags list."""
        if not tags:
            return ""
        for tag in tags:
            if tag.get("Key") == "Name":
                return tag.get("Value", "")
        return ""

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all FSx file systems."""
        fsx = self.session.client("fsx")
        resources = []

        try:
            # List file systems
            paginator = fsx.get_paginator("describe_file_systems")
            for page in paginator.paginate():
                for fs in page.get("FileSystems", []):
                    fs_id = fs["FileSystemId"]
                    name = self._get_tag_name(fs.get("Tags", [])) or fs_id
                    resources.append({
                        "id": fs_id,
                        "name": name,
                        "type": "file_system",
                        "fs_type": fs.get("FileSystemType", ""),
                        "lifecycle": fs.get("Lifecycle", ""),
                    })

        except ClientError as e:
            self.logger.error(f"Error listing FSx file systems: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete an FSx file system."""
        fsx = self.session.client("fsx")
        fs_id = resource.get("id")

        try:
            fsx.delete_file_system(FileSystemId=fs_id)
            return True
        except ClientError as e:
            self.logger.error(
                f"Error deleting FSx file system {fs_id}: {str(e)}"
            )
            return False
