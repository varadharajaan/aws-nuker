"""Handler for ELASTICBEANSTALK resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class ElasticbeanstalkHandler(ResourceHandler):
    """Handler for ELASTICBEANSTALK resources."""

    @property
    def service_name(self) -> str:
        return "elasticbeanstalk"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all ELASTICBEANSTALK resources."""
        client = self.session.client("elasticbeanstalk")
        resources = []

        try:
            response = client.describe_applications()
            for item in response.get("Applications", []):
                resources.append({
                    "id": item.get("ApplicationName", ""),
                    "name": item.get("ApplicationName", ""),
                    "type": "application",
                })
        except ClientError as e:
            self.logger.error(f"Error listing ELASTICBEANSTALK resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a ELASTICBEANSTALK resource."""
        client = self.session.client("elasticbeanstalk")
        resource_id = resource.get("id")

        try:
            client.delete_application(ApplicationName=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting ELASTICBEANSTALK resource {resource_id}: {str(e)}")
            return False
