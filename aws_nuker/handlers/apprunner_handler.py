"""App Runner resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class AppRunnerHandler(ResourceHandler):
    """Handler for AWS App Runner resources."""

    @property
    def service_name(self) -> str:
        return "apprunner"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all App Runner services."""
        apprunner = self.session.client("apprunner")
        resources = []

        try:
            # List services
            paginator = apprunner.get_paginator("list_services")
            for page in paginator.paginate():
                for service in page.get("ServiceSummaryList", []):
                    resources.append({
                        "id": service["ServiceArn"],
                        "name": service.get("ServiceName", service["ServiceArn"].split("/")[-1]),
                        "type": "service",
                        "status": service.get("Status", ""),
                    })

        except ClientError as e:
            self.logger.error(f"Error listing App Runner services: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete an App Runner service."""
        apprunner = self.session.client("apprunner")
        service_arn = resource.get("id")

        try:
            apprunner.delete_service(ServiceArn=service_arn)
            return True
        except ClientError as e:
            self.logger.error(
                f"Error deleting App Runner service {service_arn}: {str(e)}"
            )
            return False
