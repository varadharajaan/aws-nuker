"""Tests for SQS Handler."""

import pytest
from unittest.mock import MagicMock, patch
from botocore.exceptions import ClientError

from aws_nuker.handlers.sqs_handler import SQSHandler


class TestSQSHandler:
    """Tests for SQSHandler class."""

    @pytest.fixture
    def handler(self):
        """Create SQSHandler with mocked session."""
        with patch('aws_nuker.handlers.sqs_handler.ResourceHandler.__init__'):
            handler = SQSHandler.__new__(SQSHandler)
            handler.region = "us-east-1"
            handler.dry_run = False
            handler.force = False
            handler.logger = MagicMock()
            handler.session = MagicMock()
        return handler

    def test_service_name(self, handler):
        """Test service_name property."""
        assert handler.service_name == "sqs"

    def test_list_resources_queues(self, handler):
        """Test listing SQS queues."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client

        mock_paginator = MagicMock()
        mock_paginator.paginate.return_value = [{
            "QueueUrls": [
                "https://sqs.us-east-1.amazonaws.com/123456789012/my-queue"
            ]
        }]
        mock_client.get_paginator.return_value = mock_paginator

        resources = handler.list_resources()

        assert len(resources) == 1
        assert resources[0]["id"] == "https://sqs.us-east-1.amazonaws.com/123456789012/my-queue"
        assert resources[0]["type"] == "queue"

    def test_list_resources_empty(self, handler):
        """Test listing when no queues exist."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client

        mock_paginator = MagicMock()
        mock_paginator.paginate.return_value = [{"QueueUrls": []}]
        mock_client.get_paginator.return_value = mock_paginator

        resources = handler.list_resources()

        assert len(resources) == 0

    def test_list_resources_handles_error(self, handler):
        """Test error handling during list."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client
        
        mock_paginator = MagicMock()
        mock_paginator.paginate.side_effect = ClientError(
            {"Error": {"Code": "AccessDenied", "Message": "Access Denied"}},
            "ListQueues"
        )
        mock_client.get_paginator.return_value = mock_paginator

        resources = handler.list_resources()

        assert resources == []
        handler.logger.error.assert_called()

    def test_delete_queue(self, handler):
        """Test deleting an SQS queue."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client

        resource = {
            "id": "https://sqs.us-east-1.amazonaws.com/123456789012/my-queue",
            "type": "queue"
        }
        result = handler.delete_resource(resource)

        assert result is True
        mock_client.delete_queue.assert_called_once_with(
            QueueUrl="https://sqs.us-east-1.amazonaws.com/123456789012/my-queue"
        )

    def test_delete_handles_error(self, handler):
        """Test error handling during deletion."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client
        mock_client.delete_queue.side_effect = ClientError(
            {"Error": {"Code": "NonExistentQueue", "Message": "Not found"}},
            "DeleteQueue"
        )

        resource = {
            "id": "https://sqs.us-east-1.amazonaws.com/123456789012/my-queue",
            "type": "queue"
        }
        result = handler.delete_resource(resource)

        assert result is False
        handler.logger.error.assert_called()
