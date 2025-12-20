"""Cognito resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class CognitoHandler(ResourceHandler):
    """Handler for Cognito user pools and identity pools."""

    @property
    def service_name(self) -> str:
        return "cognito"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all Cognito resources."""
        cognito_idp = self.session.client("cognito-idp")
        cognito_identity = self.session.client("cognito-identity")
        resources = []

        try:
            # List user pools
            paginator = cognito_idp.get_paginator("list_user_pools")
            for page in paginator.paginate(MaxResults=60):
                for pool in page.get("UserPools", []):
                    resources.append({
                        "id": pool["Id"],
                        "name": pool.get("Name", pool["Id"]),
                        "type": "user_pool",
                    })

        except ClientError as e:
            self.logger.error(f"Error listing Cognito user pools: {str(e)}")

        try:
            # List identity pools
            paginator = cognito_identity.get_paginator("list_identity_pools")
            for page in paginator.paginate(MaxResults=60):
                for pool in page.get("IdentityPools", []):
                    resources.append({
                        "id": pool["IdentityPoolId"],
                        "name": pool.get("IdentityPoolName", pool["IdentityPoolId"]),
                        "type": "identity_pool",
                    })

        except ClientError as e:
            self.logger.error(f"Error listing Cognito identity pools: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a Cognito resource."""
        resource_type = resource.get("type")
        resource_id = resource.get("id")

        try:
            if resource_type == "user_pool":
                cognito_idp = self.session.client("cognito-idp")
                cognito_idp.delete_user_pool(UserPoolId=resource_id)
                return True

            elif resource_type == "identity_pool":
                cognito_identity = self.session.client("cognito-identity")
                cognito_identity.delete_identity_pool(IdentityPoolId=resource_id)
                return True

            return False

        except ClientError as e:
            self.logger.error(
                f"Error deleting Cognito {resource_type} {resource_id}: {str(e)}"
            )
            return False
