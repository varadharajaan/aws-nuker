"""Global Accelerator resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class GlobalAcceleratorHandler(ResourceHandler):
    """Handler for AWS Global Accelerator resources."""

    @property
    def service_name(self) -> str:
        return "globalaccelerator"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all Global Accelerator accelerators."""
        # Global Accelerator is a global service, use us-west-2
        globalaccelerator = self.session.client("globalaccelerator", region_name="us-west-2")
        resources = []

        try:
            # List accelerators
            paginator = globalaccelerator.get_paginator("list_accelerators")
            for page in paginator.paginate():
                for accelerator in page.get("Accelerators", []):
                    resources.append({
                        "id": accelerator["AcceleratorArn"],
                        "name": accelerator.get("Name", accelerator["AcceleratorArn"].split("/")[-1]),
                        "type": "accelerator",
                    })

        except ClientError as e:
            self.logger.error(f"Error listing Global Accelerator accelerators: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a Global Accelerator accelerator."""
        globalaccelerator = self.session.client("globalaccelerator", region_name="us-west-2")
        accelerator_arn = resource.get("id")

        try:
            # First, disable the accelerator
            globalaccelerator.update_accelerator(
                AcceleratorArn=accelerator_arn,
                Enabled=False
            )
            # Then delete it
            globalaccelerator.delete_accelerator(AcceleratorArn=accelerator_arn)
            return True
        except ClientError as e:
            self.logger.error(
                f"Error deleting Global Accelerator {accelerator_arn}: {str(e)}"
            )
            return False
