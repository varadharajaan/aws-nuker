"""Lambda resource handler.

Enhanced handler for AWS Lambda resources including:
- Lambda functions
- Lambda layers (all versions)
- Event source mappings
- Code signing configurations
- Function URLs
"""

from typing import List, Dict, Any, Optional
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class LambdaHandler(ResourceHandler):
    """
    Handler for AWS Lambda resources.

    Manages the lifecycle of:
    - Lambda functions and their aliases/versions
    - Lambda layers with version enumeration
    - Event source mappings (separate from functions)
    - Code signing configurations
    - Function URLs
    """

    @property
    def service_name(self) -> str:
        return "lambda"

    def list_resources(self) -> List[Dict[str, Any]]:
        """
        List all Lambda resources.

        Enumerates:
        - Functions with metadata
        - All layer versions
        - Event source mappings
        - Code signing configurations
        - Function URLs
        """
        lambda_client = self.session.client("lambda")
        resources = []

        try:
            # List functions
            resources.extend(self._list_functions(lambda_client))

            # List layers with all versions
            resources.extend(self._list_layers_with_versions(lambda_client))

            # List event source mappings
            resources.extend(self._list_event_source_mappings(lambda_client))

            # List code signing configurations
            resources.extend(self._list_code_signing_configs(lambda_client))

            # List function URLs
            resources.extend(self._list_function_urls(lambda_client))

        except ClientError as e:
            self.logger.error(f"Error listing Lambda resources: {str(e)}")

        return resources

    def _list_functions(self, client) -> List[Dict[str, Any]]:
        """List all Lambda functions with metadata."""
        resources = []
        try:
            paginator = client.get_paginator("list_functions")
            for page in paginator.paginate():
                for function in page.get("Functions", []):
                    resources.append({
                        "id": function["FunctionArn"],
                        "name": function["FunctionName"],
                        "type": "function",
                        "runtime": function.get("Runtime", ""),
                        "memory_size": function.get("MemorySize"),
                        "timeout": function.get("Timeout"),
                        "last_modified": function.get("LastModified"),
                        "code_size": function.get("CodeSize"),
                        "handler": function.get("Handler"),
                    })
        except ClientError as e:
            self.logger.warning(f"Error listing Lambda functions: {str(e)}")
        return resources

    def _list_layers_with_versions(self, client) -> List[Dict[str, Any]]:
        """
        List all Lambda layers with version details.

        Enumerates all versions of each layer for complete cleanup.
        """
        resources = []
        try:
            layers_paginator = client.get_paginator("list_layers")
            for page in layers_paginator.paginate():
                for layer in page.get("Layers", []):
                    layer_name = layer["LayerName"]

                    # Get all versions of this layer
                    try:
                        versions_response = client.list_layer_versions(
                            LayerName=layer_name
                        )
                        layer_versions = versions_response.get("LayerVersions", [])

                        # Add the layer with version count
                        resources.append({
                            "id": layer["LayerArn"],
                            "name": layer_name,
                            "type": "layer",
                            "version_count": len(layer_versions),
                            "latest_version": layer.get("LatestMatchingVersion", {}).get(
                                "Version"
                            ),
                            "compatible_runtimes": layer.get(
                                "LatestMatchingVersion", {}
                            ).get("CompatibleRuntimes", []),
                        })

                        # Also list individual layer versions for granular control
                        for version in layer_versions:
                            resources.append({
                                "id": version["LayerVersionArn"],
                                "name": f"{layer_name}:{version['Version']}",
                                "type": "layer_version",
                                "layer_name": layer_name,
                                "version": version["Version"],
                                "created_date": version.get("CreatedDate"),
                                "compatible_runtimes": version.get("CompatibleRuntimes", []),
                            })

                    except ClientError as e:
                        self.logger.warning(
                            f"Error listing versions for layer {layer_name}: {str(e)}"
                        )
                        # Still add the layer without version details
                        resources.append({
                            "id": layer["LayerArn"],
                            "name": layer_name,
                            "type": "layer",
                        })

        except ClientError as e:
            self.logger.warning(f"Error listing Lambda layers: {str(e)}")

        return resources

    def _list_event_source_mappings(self, client) -> List[Dict[str, Any]]:
        """
        List all event source mappings.

        Event source mappings connect Lambda functions to event sources
        like Kinesis streams, DynamoDB streams, SQS queues, etc.
        """
        resources = []
        try:
            paginator = client.get_paginator("list_event_source_mappings")
            for page in paginator.paginate():
                for mapping in page.get("EventSourceMappings", []):
                    event_source_arn = mapping.get("EventSourceArn", "")

                    # Determine the event source type
                    source_type = self._get_event_source_type(event_source_arn)

                    resources.append({
                        "id": mapping["UUID"],
                        "name": mapping.get("FunctionArn", "").split(":")[-1] or mapping["UUID"],
                        "type": "event_source_mapping",
                        "function_arn": mapping.get("FunctionArn"),
                        "event_source_arn": event_source_arn,
                        "source_type": source_type,
                        "state": mapping.get("State"),
                        "batch_size": mapping.get("BatchSize"),
                        "last_modified": mapping.get("LastModified"),
                    })

        except ClientError as e:
            self.logger.warning(f"Error listing event source mappings: {str(e)}")

        return resources

    def _get_event_source_type(self, arn: str) -> str:
        """Determine the event source type from the ARN."""
        if not arn:
            return "unknown"
        if ":kinesis:" in arn:
            return "kinesis"
        if ":dynamodb:" in arn:
            return "dynamodb"
        if ":sqs:" in arn:
            return "sqs"
        if ":kafka:" in arn or ":kafka-cluster:" in arn:
            return "kafka"
        if ":mq:" in arn:
            return "mq"
        return "other"

    def _list_code_signing_configs(self, client) -> List[Dict[str, Any]]:
        """List all code signing configurations."""
        resources = []
        try:
            paginator = client.get_paginator("list_code_signing_configs")
            for page in paginator.paginate():
                for config in page.get("CodeSigningConfigs", []):
                    resources.append({
                        "id": config["CodeSigningConfigId"],
                        "name": config.get("Description", config["CodeSigningConfigId"]),
                        "type": "code_signing_config",
                        "arn": config["CodeSigningConfigArn"],
                        "last_modified": config.get("LastModified"),
                    })
        except ClientError as e:
            # This might fail if the feature isn't used/available
            self.logger.debug(f"Error listing code signing configs: {str(e)}")
        return resources

    def _list_function_urls(self, client) -> List[Dict[str, Any]]:
        """List all function URLs."""
        resources = []
        try:
            # First get all functions
            paginator = client.get_paginator("list_functions")
            for page in paginator.paginate():
                for function in page.get("Functions", []):
                    function_name = function["FunctionName"]
                    try:
                        # Check if function has a URL configuration
                        url_config = client.get_function_url_config(
                            FunctionName=function_name
                        )
                        resources.append({
                            "id": f"{function_name}-url",
                            "name": f"{function_name} URL",
                            "type": "function_url",
                            "function_name": function_name,
                            "function_arn": url_config.get("FunctionArn"),
                            "function_url": url_config.get("FunctionUrl"),
                            "auth_type": url_config.get("AuthType"),
                            "creation_time": url_config.get("CreationTime"),
                        })
                    except ClientError as e:
                        error_code = e.response.get("Error", {}).get("Code", "")
                        if error_code != "ResourceNotFoundException":
                            self.logger.debug(
                                f"Error getting function URL for {function_name}: {str(e)}"
                            )
        except ClientError as e:
            self.logger.debug(f"Error listing function URLs: {str(e)}")
        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a Lambda resource."""
        lambda_client = self.session.client("lambda")
        resource_type = resource.get("type")
        resource_id = resource.get("id")
        resource_name = resource.get("name")

        try:
            if resource_type == "function":
                return self._delete_function(lambda_client, resource_name)

            elif resource_type == "layer":
                return self._delete_layer(lambda_client, resource_name)

            elif resource_type == "layer_version":
                return self._delete_layer_version(
                    lambda_client,
                    resource.get("layer_name"),
                    resource.get("version"),
                )

            elif resource_type == "event_source_mapping":
                return self._delete_event_source_mapping(lambda_client, resource_id)

            elif resource_type == "code_signing_config":
                return self._delete_code_signing_config(lambda_client, resource_id)

            elif resource_type == "function_url":
                return self._delete_function_url(
                    lambda_client, resource.get("function_name")
                )

            return False

        except ClientError as e:
            self.logger.error(
                f"Error deleting Lambda {resource_type} {resource_name}: {str(e)}"
            )
            return False

    def _delete_function(self, client, function_name: str) -> bool:
        """Delete a Lambda function."""
        client.delete_function(FunctionName=function_name)
        return True

    def _delete_layer(self, client, layer_name: str) -> bool:
        """Delete all versions of a Lambda layer."""
        versions_response = client.list_layer_versions(LayerName=layer_name)
        for version in versions_response.get("LayerVersions", []):
            client.delete_layer_version(
                LayerName=layer_name,
                VersionNumber=version["Version"],
            )
        return True

    def _delete_layer_version(
        self, client, layer_name: str, version: int
    ) -> bool:
        """Delete a specific layer version."""
        client.delete_layer_version(
            LayerName=layer_name,
            VersionNumber=version,
        )
        return True

    def _delete_event_source_mapping(self, client, uuid: str) -> bool:
        """Delete an event source mapping."""
        client.delete_event_source_mapping(UUID=uuid)
        return True

    def _delete_code_signing_config(self, client, config_id: str) -> bool:
        """Delete a code signing configuration."""
        client.delete_code_signing_config(CodeSigningConfigArn=config_id)
        return True

    def _delete_function_url(self, client, function_name: str) -> bool:
        """Delete a function URL configuration."""
        client.delete_function_url_config(FunctionName=function_name)
        return True
