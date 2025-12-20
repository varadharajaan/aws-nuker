"""Tests for Lambda Handler."""

import pytest
from unittest.mock import MagicMock, patch
from botocore.exceptions import ClientError

from aws_nuker.handlers.lambda_handler import LambdaHandler


class TestLambdaHandler:
    """Tests for LambdaHandler class."""

    @pytest.fixture
    def handler(self):
        """Create LambdaHandler with mocked session."""
        with patch('aws_nuker.handlers.lambda_handler.ResourceHandler.__init__'):
            handler = LambdaHandler.__new__(LambdaHandler)
            handler.region = "us-east-1"
            handler.dry_run = False
            handler.force = False
            handler.logger = MagicMock()
            handler.session = MagicMock()
        return handler

    def test_service_name(self, handler):
        """Test service_name property."""
        assert handler.service_name == "lambda"

    def test_list_functions(self, handler):
        """Test listing Lambda functions."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client

        mock_paginator = MagicMock()
        mock_paginator.paginate.return_value = [{
            "Functions": [{
                "FunctionArn": "arn:aws:lambda:us-east-1:123456789012:function:my-function",
                "FunctionName": "my-function",
                "Runtime": "python3.9",
                "MemorySize": 128,
                "Timeout": 30,
                "LastModified": "2023-01-01T00:00:00Z",
                "CodeSize": 1024,
                "Handler": "index.handler"
            }]
        }]
        mock_client.get_paginator.return_value = mock_paginator

        resources = handler._list_functions(mock_client)

        assert len(resources) == 1
        assert resources[0]["name"] == "my-function"
        assert resources[0]["type"] == "function"
        assert resources[0]["runtime"] == "python3.9"

    def test_list_layers_with_versions(self, handler):
        """Test listing Lambda layers with version details."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client

        mock_layers_paginator = MagicMock()
        mock_layers_paginator.paginate.return_value = [{
            "Layers": [{
                "LayerArn": "arn:aws:lambda:us-east-1:123456789012:layer:my-layer",
                "LayerName": "my-layer",
                "LatestMatchingVersion": {"Version": 2, "CompatibleRuntimes": ["python3.9"]}
            }]
        }]
        mock_client.get_paginator.return_value = mock_layers_paginator
        
        mock_client.list_layer_versions.return_value = {
            "LayerVersions": [
                {"LayerVersionArn": "arn:aws:lambda:...:layer:my-layer:1", "Version": 1, "CreatedDate": "2023-01-01"},
                {"LayerVersionArn": "arn:aws:lambda:...:layer:my-layer:2", "Version": 2, "CreatedDate": "2023-02-01"},
            ]
        }

        resources = handler._list_layers_with_versions(mock_client)

        # Should have layer + 2 layer versions
        assert len(resources) == 3
        layer_resources = [r for r in resources if r["type"] == "layer"]
        version_resources = [r for r in resources if r["type"] == "layer_version"]
        assert len(layer_resources) == 1
        assert len(version_resources) == 2

    def test_list_event_source_mappings(self, handler):
        """Test listing event source mappings."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client

        mock_paginator = MagicMock()
        mock_paginator.paginate.return_value = [{
            "EventSourceMappings": [{
                "UUID": "uuid-1234",
                "FunctionArn": "arn:aws:lambda:us-east-1:123456789012:function:my-function",
                "EventSourceArn": "arn:aws:sqs:us-east-1:123456789012:my-queue",
                "State": "Enabled",
                "BatchSize": 10,
                "LastModified": "2023-01-01T00:00:00Z"
            }]
        }]
        mock_client.get_paginator.return_value = mock_paginator

        resources = handler._list_event_source_mappings(mock_client)

        assert len(resources) == 1
        assert resources[0]["id"] == "uuid-1234"
        assert resources[0]["type"] == "event_source_mapping"
        assert resources[0]["source_type"] == "sqs"

    def test_get_event_source_type_kinesis(self, handler):
        """Test event source type detection for Kinesis."""
        arn = "arn:aws:kinesis:us-east-1:123456789012:stream/my-stream"
        assert handler._get_event_source_type(arn) == "kinesis"

    def test_get_event_source_type_dynamodb(self, handler):
        """Test event source type detection for DynamoDB."""
        arn = "arn:aws:dynamodb:us-east-1:123456789012:table/my-table/stream/..."
        assert handler._get_event_source_type(arn) == "dynamodb"

    def test_get_event_source_type_sqs(self, handler):
        """Test event source type detection for SQS."""
        arn = "arn:aws:sqs:us-east-1:123456789012:my-queue"
        assert handler._get_event_source_type(arn) == "sqs"

    def test_get_event_source_type_kafka(self, handler):
        """Test event source type detection for Kafka."""
        arn = "arn:aws:kafka:us-east-1:123456789012:cluster/my-cluster"
        assert handler._get_event_source_type(arn) == "kafka"

    def test_get_event_source_type_mq(self, handler):
        """Test event source type detection for MQ."""
        arn = "arn:aws:mq:us-east-1:123456789012:broker/my-broker"
        assert handler._get_event_source_type(arn) == "mq"

    def test_get_event_source_type_unknown(self, handler):
        """Test event source type detection for unknown ARN."""
        assert handler._get_event_source_type("") == "unknown"
        assert handler._get_event_source_type("arn:aws:other:...") == "other"

    def test_delete_function(self, handler):
        """Test deleting a Lambda function."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client

        result = handler._delete_function(mock_client, "my-function")

        assert result is True
        mock_client.delete_function.assert_called_once_with(FunctionName="my-function")

    def test_delete_layer(self, handler):
        """Test deleting all versions of a Lambda layer."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client

        mock_client.list_layer_versions.return_value = {
            "LayerVersions": [
                {"Version": 1},
                {"Version": 2},
            ]
        }

        result = handler._delete_layer(mock_client, "my-layer")

        assert result is True
        assert mock_client.delete_layer_version.call_count == 2

    def test_delete_layer_version(self, handler):
        """Test deleting a specific layer version."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client

        result = handler._delete_layer_version(mock_client, "my-layer", 1)

        assert result is True
        mock_client.delete_layer_version.assert_called_once_with(
            LayerName="my-layer",
            VersionNumber=1
        )

    def test_delete_event_source_mapping(self, handler):
        """Test deleting an event source mapping."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client

        result = handler._delete_event_source_mapping(mock_client, "uuid-1234")

        assert result is True
        mock_client.delete_event_source_mapping.assert_called_once_with(UUID="uuid-1234")

    def test_delete_code_signing_config(self, handler):
        """Test deleting a code signing config."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client

        result = handler._delete_code_signing_config(mock_client, "csc-arn")

        assert result is True
        mock_client.delete_code_signing_config.assert_called_once_with(
            CodeSigningConfigArn="csc-arn"
        )

    def test_delete_function_url(self, handler):
        """Test deleting a function URL."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client

        result = handler._delete_function_url(mock_client, "my-function")

        assert result is True
        mock_client.delete_function_url_config.assert_called_once_with(
            FunctionName="my-function"
        )

    def test_delete_resource_function(self, handler):
        """Test delete_resource dispatches to correct method for function."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client

        resource = {"id": "arn:...", "name": "my-function", "type": "function"}
        result = handler.delete_resource(resource)

        assert result is True
        mock_client.delete_function.assert_called_once()

    def test_delete_resource_unknown_type(self, handler):
        """Test delete_resource returns False for unknown type."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client

        resource = {"id": "unknown", "type": "unknown_type"}
        result = handler.delete_resource(resource)

        assert result is False

    def test_delete_resource_handles_error(self, handler):
        """Test error handling during deletion."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client
        mock_client.delete_function.side_effect = ClientError(
            {"Error": {"Code": "ResourceNotFound", "Message": "Not found"}},
            "DeleteFunction"
        )

        resource = {"id": "arn:...", "name": "my-function", "type": "function"}
        result = handler.delete_resource(resource)

        assert result is False
        handler.logger.error.assert_called()
