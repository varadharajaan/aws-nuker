"""Tests for SNS Handler."""

import pytest
from unittest.mock import MagicMock, patch
from botocore.exceptions import ClientError

from aws_nuker.handlers.sns_handler import SNSHandler


class TestSNSHandler:
    """Tests for SNSHandler class."""

    @pytest.fixture
    def handler(self):
        """Create SNSHandler with mocked session."""
        with patch('aws_nuker.handlers.sns_handler.ResourceHandler.__init__'):
            handler = SNSHandler.__new__(SNSHandler)
            handler.region = "us-east-1"
            handler.dry_run = False
            handler.force = False
            handler.logger = MagicMock()
            handler.session = MagicMock()
        return handler

    def test_service_name(self, handler):
        """Test service_name property."""
        assert handler.service_name == "sns"

    def test_list_resources_topics(self, handler):
        """Test listing SNS topics."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client

        mock_paginator = MagicMock()
        mock_paginator.paginate.return_value = [{
            "Topics": [
                {"TopicArn": "arn:aws:sns:us-east-1:123456789012:my-topic"}
            ]
        }]
        mock_client.get_paginator.return_value = mock_paginator

        resources = handler.list_resources()

        assert len(resources) == 1
        assert resources[0]["id"] == "arn:aws:sns:us-east-1:123456789012:my-topic"
        assert resources[0]["type"] == "topic"

    def test_list_resources_handles_error(self, handler):
        """Test error handling during list."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client
        
        mock_paginator = MagicMock()
        mock_paginator.paginate.side_effect = ClientError(
            {"Error": {"Code": "AccessDenied", "Message": "Access Denied"}},
            "ListTopics"
        )
        mock_client.get_paginator.return_value = mock_paginator

        resources = handler.list_resources()

        assert resources == []
        handler.logger.error.assert_called()

    def test_delete_topic(self, handler):
        """Test deleting an SNS topic."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client

        resource = {
            "id": "arn:aws:sns:us-east-1:123456789012:my-topic",
            "type": "topic"
        }
        result = handler.delete_resource(resource)

        assert result is True
        mock_client.delete_topic.assert_called_once()

    def test_delete_handles_error(self, handler):
        """Test error handling during deletion."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client
        mock_client.delete_topic.side_effect = ClientError(
            {"Error": {"Code": "NotFound", "Message": "Not found"}},
            "DeleteTopic"
        )

        resource = {
            "id": "arn:aws:sns:us-east-1:123456789012:my-topic",
            "type": "topic"
        }
        result = handler.delete_resource(resource)

        assert result is False
        handler.logger.error.assert_called()
