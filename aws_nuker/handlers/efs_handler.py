"""EFS (Elastic File System) resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class EFSHandler(ResourceHandler):
    """Handler for EFS file systems and mount targets."""

    @property
    def service_name(self) -> str:
        return "efs"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all EFS resources."""
        efs = self.session.client("efs")
        resources = []

        try:
            # List file systems
            paginator = efs.get_paginator("describe_file_systems")
            for page in paginator.paginate():
                for fs in page.get("FileSystems", []):
                    fs_id = fs["FileSystemId"]
                    
                    resources.append({
                        "id": fs_id,
                        "name": fs.get("Name", fs_id),
                        "type": "file_system",
                        "lifecycle_state": fs.get("LifeCycleState", ""),
                    })
                    
                    # List mount targets for this file system
                    try:
                        mt_paginator = efs.get_paginator("describe_mount_targets")
                        for mt_page in mt_paginator.paginate(FileSystemId=fs_id):
                            for mt in mt_page.get("MountTargets", []):
                                resources.append({
                                    "id": mt["MountTargetId"],
                                    "name": mt["MountTargetId"],
                                    "type": "mount_target",
                                    "file_system_id": fs_id,
                                })
                    except ClientError:
                        pass

        except ClientError as e:
            self.logger.error(f"Error listing EFS resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete an EFS resource."""
        efs = self.session.client("efs")
        resource_type = resource.get("type")
        resource_id = resource.get("id")

        try:
            if resource_type == "mount_target":
                # Delete mount target first (dependency for file system)
                efs.delete_mount_target(MountTargetId=resource_id)
                return True

            elif resource_type == "file_system":
                # Delete file system
                efs.delete_file_system(FileSystemId=resource_id)
                return True

            return False

        except ClientError as e:
            self.logger.error(
                f"Error deleting EFS {resource_type} {resource_id}: {str(e)}"
            )
            return False
