"""Handler for STEPFUNCTIONS resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class StepfunctionsHandler(ResourceHandler):
    """Handler for STEPFUNCTIONS resources."""

    @property
    def service_name(self) -> str:
        return "stepfunctions"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all STEPFUNCTIONS resources."""
        client = self.session.client("stepfunctions")
        resources = []

        try:
            paginator = client.get_paginator("list_state_machines")
            for page in paginator.paginate():
                for item in page.get("stateMachines", []):
                    resources.append({
                        "id": item.get("stateMachineArn", ""),
                        "name": item.get("name", ""),
                        "type": "state_machine",
                    })
        except ClientError as e:
            self.logger.error(f"Error listing STEPFUNCTIONS resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a STEPFUNCTIONS resource."""
        client = self.session.client("stepfunctions")
        resource_id = resource.get("id")

        try:
            client.delete_state_machine(stateMachineArn=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting STEPFUNCTIONS resource {resource_id}: {str(e)}")
            return False
