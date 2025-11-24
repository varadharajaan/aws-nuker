"""AppStream resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class AppStreamHandler(ResourceHandler):
    """Handler for Amazon AppStream 2.0 resources."""

    @property
    def service_name(self) -> str:
        return "appstream"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all AppStream resources."""
        appstream = self.session.client("appstream")
        resources = []

        try:
            # List fleets
            response = appstream.describe_fleets()
            for fleet in response.get("Fleets", []):
                resources.append({
                    "id": fleet["Arn"],
                    "name": fleet["Name"],
                    "type": "fleet",
                    "state": fleet.get("State", ""),
                })

        except ClientError as e:
            self.logger.error(f"Error listing AppStream fleets: {str(e)}")

        try:
            # List stacks
            response = appstream.describe_stacks()
            for stack in response.get("Stacks", []):
                resources.append({
                    "id": stack["Arn"],
                    "name": stack["Name"],
                    "type": "stack",
                })

        except ClientError as e:
            self.logger.error(f"Error listing AppStream stacks: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete an AppStream resource."""
        appstream = self.session.client("appstream")
        resource_type = resource.get("type")
        resource_name = resource.get("name")

        try:
            if resource_type == "fleet":
                # Stop fleet first
                appstream.stop_fleet(Name=resource_name)
                appstream.delete_fleet(Name=resource_name)
                return True

            elif resource_type == "stack":
                appstream.delete_stack(Name=resource_name)
                return True

            return False

        except ClientError as e:
            self.logger.error(
                f"Error deleting AppStream {resource_type} {resource_name}: {str(e)}"
            )
            return False
