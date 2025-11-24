"""AppFlow resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class AppFlowHandler(ResourceHandler):
    """Handler for AppFlow flows."""

    @property
    def service_name(self) -> str:
        return "appflow"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all AppFlow flows."""
        appflow = self.session.client("appflow")
        resources = []

        try:
            # List flows
            paginator = appflow.get_paginator("list_flows")
            for page in paginator.paginate():
                for flow in page.get("flows", []):
                    resources.append({
                        "id": flow["flowArn"],
                        "name": flow["flowName"],
                        "type": "flow",
                        "status": flow.get("flowStatus", ""),
                    })

        except ClientError as e:
            self.logger.error(f"Error listing AppFlow flows: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete an AppFlow flow."""
        appflow = self.session.client("appflow")
        flow_name = resource.get("name")

        try:
            appflow.delete_flow(flowName=flow_name, forceDelete=self.force)
            return True
        except ClientError as e:
            self.logger.error(
                f"Error deleting AppFlow flow {flow_name}: {str(e)}"
            )
            return False
