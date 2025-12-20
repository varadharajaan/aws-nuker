"""OpsWorks resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class OpsWorksHandler(ResourceHandler):
    """Handler for AWS OpsWorks resources."""

    @property
    def service_name(self) -> str:
        return "opsworks"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all OpsWorks stacks."""
        opsworks = self.session.client("opsworks")
        resources = []

        try:
            # List stacks
            response = opsworks.describe_stacks()
            for stack in response.get("Stacks", []):
                resources.append({
                    "id": stack["StackId"],
                    "name": stack.get("Name", stack["StackId"]),
                    "type": "stack",
                })

        except ClientError as e:
            self.logger.error(f"Error listing OpsWorks stacks: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete an OpsWorks stack."""
        opsworks = self.session.client("opsworks")
        stack_id = resource.get("id")

        try:
            opsworks.delete_stack(StackId=stack_id)
            return True
        except ClientError as e:
            self.logger.error(
                f"Error deleting OpsWorks stack {stack_id}: {str(e)}"
            )
            return False
