"""CodeDeploy resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class CodeDeployHandler(ResourceHandler):
    """Handler for CodeDeploy applications and deployment groups."""

    @property
    def service_name(self) -> str:
        return "codedeploy"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all CodeDeploy resources."""
        codedeploy = self.session.client("codedeploy")
        resources = []

        try:
            # List applications
            paginator = codedeploy.get_paginator("list_applications")
            for page in paginator.paginate():
                for app_name in page.get("applications", []):
                    resources.append({
                        "id": app_name,
                        "name": app_name,
                        "type": "application",
                    })

                    # List deployment groups for this application
                    try:
                        dg_paginator = codedeploy.get_paginator("list_deployment_groups")
                        for dg_page in dg_paginator.paginate(applicationName=app_name):
                            for dg_name in dg_page.get("deploymentGroups", []):
                                resources.append({
                                    "id": dg_name,
                                    "name": dg_name,
                                    "type": "deployment_group",
                                    "application_name": app_name,
                                })
                    except ClientError:
                        pass

        except ClientError as e:
            self.logger.error(f"Error listing CodeDeploy applications: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a CodeDeploy resource."""
        codedeploy = self.session.client("codedeploy")
        resource_type = resource.get("type")
        resource_name = resource.get("name")

        try:
            if resource_type == "deployment_group":
                app_name = resource.get("application_name")
                codedeploy.delete_deployment_group(
                    applicationName=app_name,
                    deploymentGroupName=resource_name
                )
                return True

            elif resource_type == "application":
                codedeploy.delete_application(applicationName=resource_name)
                return True

            return False

        except ClientError as e:
            self.logger.error(
                f"Error deleting CodeDeploy {resource_type} {resource_name}: {str(e)}"
            )
            return False
