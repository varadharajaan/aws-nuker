"""Serverless Application Repository resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class ServerlessRepoHandler(ResourceHandler):
    """Handler for AWS Serverless Application Repository resources."""

    @property
    def service_name(self) -> str:
        return "serverlessrepo"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all Serverless Application Repository applications."""
        serverlessrepo = self.session.client("serverlessrepo")
        resources = []

        try:
            # List applications
            paginator = serverlessrepo.get_paginator("list_applications")
            for page in paginator.paginate():
                for app in page.get("Applications", []):
                    # Only list applications owned by the current account
                    resources.append({
                        "id": app["ApplicationId"],
                        "name": app.get("Name", app["ApplicationId"]),
                        "type": "application",
                    })

        except ClientError as e:
            self.logger.error(f"Error listing Serverless Repository applications: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a Serverless Repository application."""
        serverlessrepo = self.session.client("serverlessrepo")
        app_id = resource.get("id")

        try:
            serverlessrepo.delete_application(ApplicationId=app_id)
            return True
        except ClientError as e:
            self.logger.error(
                f"Error deleting Serverless Repository application {app_id}: {str(e)}"
            )
            return False
