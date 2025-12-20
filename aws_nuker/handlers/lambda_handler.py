"""Lambda resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class LambdaHandler(ResourceHandler):
    """Handler for AWS Lambda functions and layers."""

    @property
    def service_name(self) -> str:
        return "lambda"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all Lambda functions and layers."""
        lambda_client = self.session.client("lambda")
        resources = []

        try:
            # List functions
            paginator = lambda_client.get_paginator("list_functions")
            for page in paginator.paginate():
                for function in page.get("Functions", []):
                    resources.append({
                        "id": function["FunctionArn"],
                        "name": function["FunctionName"],
                        "type": "function",
                        "runtime": function.get("Runtime", ""),
                    })

            # List layers
            layers_paginator = lambda_client.get_paginator("list_layers")
            for page in layers_paginator.paginate():
                for layer in page.get("Layers", []):
                    resources.append({
                        "id": layer["LayerArn"],
                        "name": layer["LayerName"],
                        "type": "layer",
                    })

        except ClientError as e:
            self.logger.error(f"Error listing Lambda resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a Lambda resource."""
        lambda_client = self.session.client("lambda")
        resource_type = resource.get("type")
        resource_name = resource.get("name")

        try:
            if resource_type == "function":
                # Delete Lambda function
                lambda_client.delete_function(FunctionName=resource_name)
                return True

            elif resource_type == "layer":
                # Delete all versions of the layer
                layer_name = resource_name
                versions_response = lambda_client.list_layer_versions(
                    LayerName=layer_name
                )
                for version in versions_response.get("LayerVersions", []):
                    lambda_client.delete_layer_version(
                        LayerName=layer_name,
                        VersionNumber=version["Version"],
                    )
                return True

            return False

        except ClientError as e:
            self.logger.error(
                f"Error deleting Lambda {resource_type} {resource_name}: {str(e)}"
            )
            return False
