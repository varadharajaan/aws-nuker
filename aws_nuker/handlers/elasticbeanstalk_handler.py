"""Elastic Beanstalk resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class ElasticBeanstalkHandler(ResourceHandler):
    """Handler for Elastic Beanstalk applications and environments."""

    @property
    def service_name(self) -> str:
        return "elasticbeanstalk"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all Elastic Beanstalk resources."""
        eb = self.session.client("elasticbeanstalk")
        resources = []

        try:
            # List environments
            response = eb.describe_environments()
            for env in response.get("Environments", []):
                # Skip terminated environments
                if env.get("Status") != "Terminated":
                    resources.append({
                        "id": env["EnvironmentId"],
                        "name": env["EnvironmentName"],
                        "type": "environment",
                        "application": env.get("ApplicationName", ""),
                        "status": env.get("Status", ""),
                    })

        except ClientError as e:
            self.logger.error(f"Error listing Elastic Beanstalk environments: {str(e)}")

        try:
            # List applications
            response = eb.describe_applications()
            for app in response.get("Applications", []):
                resources.append({
                    "id": app["ApplicationArn"],
                    "name": app["ApplicationName"],
                    "type": "application",
                })

        except ClientError as e:
            self.logger.error(f"Error listing Elastic Beanstalk applications: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete an Elastic Beanstalk resource."""
        eb = self.session.client("elasticbeanstalk")
        resource_type = resource.get("type")
        resource_name = resource.get("name")

        try:
            if resource_type == "environment":
                # Terminate environment
                eb.terminate_environment(EnvironmentName=resource_name)
                return True

            elif resource_type == "application":
                # Delete application (this also deletes all versions)
                eb.delete_application(
                    ApplicationName=resource_name,
                    TerminateEnvByForce=self.force
                )
                return True

            return False

        except ClientError as e:
            self.logger.error(
                f"Error deleting Elastic Beanstalk {resource_type} {resource_name}: {str(e)}"
            )
            return False
