"""Handler for GLOBALACCELERATOR resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class GlobalacceleratorHandler(ResourceHandler):
    """Handler for GLOBALACCELERATOR resources."""

    @property
    def service_name(self) -> str:
        return "globalaccelerator"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all GLOBALACCELERATOR resources."""
        client = self.session.client("globalaccelerator")
        resources = []

        try:
            paginator = client.get_paginator("list_accelerators")
            for page in paginator.paginate():
                for item in page.get("Accelerators", []):
                    resources.append({
                        "id": item.get("AcceleratorArn", ""),
                        "name": item.get("Name", ""),
                        "type": "accelerator",
                    })
        except ClientError as e:
            self.logger.error(f"Error listing GLOBALACCELERATOR resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a GLOBALACCELERATOR resource."""
        client = self.session.client("globalaccelerator")
        resource_id = resource.get("id")

        try:
            client.delete_accelerator(AcceleratorArn=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting GLOBALACCELERATOR resource {resource_id}: {str(e)}")
            return False
