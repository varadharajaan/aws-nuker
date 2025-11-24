"""Step Functions resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class StepFunctionsHandler(ResourceHandler):
    """Handler for Step Functions state machines."""

    @property
    def service_name(self) -> str:
        return "stepfunctions"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all Step Functions state machines."""
        sfn = self.session.client("stepfunctions")
        resources = []

        try:
            paginator = sfn.get_paginator("list_state_machines")
            for page in paginator.paginate():
                for state_machine in page.get("stateMachines", []):
                    resources.append({
                        "id": state_machine["stateMachineArn"],
                        "name": state_machine["name"],
                        "type": "state_machine",
                        "status": state_machine.get("status", ""),
                    })

        except ClientError as e:
            self.logger.error(f"Error listing Step Functions state machines: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a Step Functions state machine."""
        sfn = self.session.client("stepfunctions")
        state_machine_arn = resource.get("id")

        try:
            sfn.delete_state_machine(stateMachineArn=state_machine_arn)
            return True
        except ClientError as e:
            self.logger.error(
                f"Error deleting Step Functions state machine {state_machine_arn}: {str(e)}"
            )
            return False
