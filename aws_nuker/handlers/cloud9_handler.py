"""Cloud9 resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class Cloud9Handler(ResourceHandler):
    """Handler for AWS Cloud9 resources."""

    @property
    def service_name(self) -> str:
        return "cloud9"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all Cloud9 environments."""
        cloud9 = self.session.client("cloud9")
        resources = []

        try:
            # List environments
            response = cloud9.list_environments()
            env_ids = response.get("environmentIds", [])
            
            if env_ids:
                # Get environment details
                envs_response = cloud9.describe_environments(environmentIds=env_ids)
                for env in envs_response.get("environments", []):
                    resources.append({
                        "id": env["id"],
                        "name": env.get("name", env["id"]),
                        "type": "environment",
                        "arn": env["arn"],
                    })

        except ClientError as e:
            self.logger.error(f"Error listing Cloud9 environments: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a Cloud9 environment."""
        cloud9 = self.session.client("cloud9")
        env_id = resource.get("id")

        try:
            cloud9.delete_environment(environmentId=env_id)
            return True
        except ClientError as e:
            self.logger.error(
                f"Error deleting Cloud9 environment {env_id}: {str(e)}"
            )
            return False
