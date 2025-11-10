"""Handler for COGNITO resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class CognitoHandler(ResourceHandler):
    """Handler for COGNITO resources."""

    @property
    def service_name(self) -> str:
        return "cognito"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all COGNITO resources."""
        client = self.session.client("cognito-idp")
        resources = []

        try:
            paginator = client.get_paginator("list_user_pools")
            for page in paginator.paginate():
                for item in page.get("UserPools", []):
                    resources.append({
                        "id": item.get("Id", ""),
                        "name": item.get("Name", ""),
                        "type": "user_pool",
                    })
        except ClientError as e:
            self.logger.error(f"Error listing COGNITO resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a COGNITO resource."""
        client = self.session.client("cognito-idp")
        resource_id = resource.get("id")

        try:
            client.delete_user_pool(UserPoolId=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting COGNITO resource {resource_id}: {str(e)}")
            return False
