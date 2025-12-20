"""API Gateway resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class APIGatewayHandler(ResourceHandler):
    """Handler for API Gateway resources."""

    @property
    def service_name(self) -> str:
        return "apigateway"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all API Gateway APIs."""
        apigw = self.session.client("apigateway")
        apigwv2 = self.session.client("apigatewayv2")
        resources = []

        try:
            # List REST APIs (v1)
            rest_apis = apigw.get_rest_apis()
            for api in rest_apis.get("items", []):
                resources.append({
                    "id": api["id"],
                    "name": api.get("name", ""),
                    "type": "rest_api",
                })

            # List HTTP/WebSocket APIs (v2)
            http_apis = apigwv2.get_apis()
            for api in http_apis.get("Items", []):
                resources.append({
                    "id": api["ApiId"],
                    "name": api.get("Name", ""),
                    "type": "http_api",
                    "protocol": api.get("ProtocolType", ""),
                })

        except ClientError as e:
            self.logger.error(f"Error listing API Gateway resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete an API Gateway resource."""
        resource_type = resource.get("type")
        resource_id = resource.get("id")

        try:
            if resource_type == "rest_api":
                apigw = self.session.client("apigateway")
                apigw.delete_rest_api(restApiId=resource_id)
                return True

            elif resource_type == "http_api":
                apigwv2 = self.session.client("apigatewayv2")
                apigwv2.delete_api(ApiId=resource_id)
                return True

            return False

        except ClientError as e:
            self.logger.error(
                f"Error deleting API Gateway {resource_type} {resource_id}: {str(e)}"
            )
            return False
