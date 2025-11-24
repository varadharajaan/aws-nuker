"""WorkSpaces resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class WorkSpacesHandler(ResourceHandler):
    """Handler for WorkSpaces."""

    @property
    def service_name(self) -> str:
        return "workspaces"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all WorkSpaces."""
        workspaces = self.session.client("workspaces")
        resources = []

        try:
            # List WorkSpaces
            paginator = workspaces.get_paginator("describe_workspaces")
            for page in paginator.paginate():
                for workspace in page.get("Workspaces", []):
                    resources.append({
                        "id": workspace["WorkspaceId"],
                        "name": workspace.get("UserName", workspace["WorkspaceId"]),
                        "type": "workspace",
                        "state": workspace.get("State", ""),
                    })

        except ClientError as e:
            self.logger.error(f"Error listing WorkSpaces: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Terminate a WorkSpace."""
        workspaces = self.session.client("workspaces")
        workspace_id = resource.get("id")

        try:
            workspaces.terminate_workspaces(
                TerminateWorkspaceRequests=[{"WorkspaceId": workspace_id}]
            )
            return True
        except ClientError as e:
            self.logger.error(
                f"Error terminating WorkSpace {workspace_id}: {str(e)}"
            )
            return False
