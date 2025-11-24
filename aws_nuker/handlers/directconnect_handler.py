"""Direct Connect resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class DirectConnectHandler(ResourceHandler):
    """Handler for Direct Connect connections and virtual interfaces."""

    @property
    def service_name(self) -> str:
        return "directconnect"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all Direct Connect resources."""
        dx = self.session.client("directconnect")
        resources = []

        try:
            # List connections
            response = dx.describe_connections()
            for connection in response.get("connections", []):
                resources.append({
                    "id": connection["connectionId"],
                    "name": connection.get("connectionName", connection["connectionId"]),
                    "type": "connection",
                    "state": connection.get("connectionState", ""),
                })

        except ClientError as e:
            self.logger.error(f"Error listing Direct Connect connections: {str(e)}")

        try:
            # List virtual interfaces
            response = dx.describe_virtual_interfaces()
            for vif in response.get("virtualInterfaces", []):
                resources.append({
                    "id": vif["virtualInterfaceId"],
                    "name": vif.get("virtualInterfaceName", vif["virtualInterfaceId"]),
                    "type": "virtual_interface",
                    "state": vif.get("virtualInterfaceState", ""),
                })

        except ClientError as e:
            self.logger.error(f"Error listing Direct Connect virtual interfaces: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a Direct Connect resource."""
        dx = self.session.client("directconnect")
        resource_type = resource.get("type")
        resource_id = resource.get("id")

        try:
            if resource_type == "virtual_interface":
                dx.delete_virtual_interface(virtualInterfaceId=resource_id)
                return True

            elif resource_type == "connection":
                dx.delete_connection(connectionId=resource_id)
                return True

            return False

        except ClientError as e:
            self.logger.error(
                f"Error deleting Direct Connect {resource_type} {resource_id}: {str(e)}"
            )
            return False
