"""CloudFormation resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class CloudFormationHandler(ResourceHandler):
    """Handler for CloudFormation stacks."""

    @property
    def service_name(self) -> str:
        return "cloudformation"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all CloudFormation stacks."""
        cfn = self.session.client("cloudformation")
        resources = []

        try:
            paginator = cfn.get_paginator("list_stacks")
            for page in paginator.paginate():
                for stack in page.get("StackSummaries", []):
                    # Skip deleted stacks
                    if stack["StackStatus"] != "DELETE_COMPLETE":
                        resources.append({
                            "id": stack["StackId"],
                            "name": stack["StackName"],
                            "type": "stack",
                            "status": stack["StackStatus"],
                        })

        except ClientError as e:
            self.logger.error(f"Error listing CloudFormation stacks: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a CloudFormation stack."""
        cfn = self.session.client("cloudformation")
        stack_name = resource.get("name")

        try:
            cfn.delete_stack(StackName=stack_name)
            return True
        except ClientError as e:
            self.logger.error(
                f"Error deleting CloudFormation stack {stack_name}: {str(e)}"
            )
            return False
