"""Tests for Kinesis Handler."""

import pytest
from unittest.mock import MagicMock, patch
from botocore.exceptions import ClientError

from aws_nuker.handlers.kinesis_handler import KinesisHandler


class TestKinesisHandler:
    """Tests for KinesisHandler class."""

    @pytest.fixture
    def handler(self):
        """Create KinesisHandler with mocked session."""
        with patch('aws_nuker.handlers.kinesis_handler.ResourceHandler.__init__'):
            handler = KinesisHandler.__new__(KinesisHandler)
            handler.region = "us-east-1"
            handler.dry_run = False
            handler.force = False
            handler.logger = MagicMock()
            handler.session = MagicMock()
        return handler

    def test_service_name(self, handler):
        """Test service_name property."""
        assert handler.service_name == "kinesis"

    def test_list_resources_streams(self, handler):
        """Test listing Kinesis streams."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client

        mock_paginator = MagicMock()
        mock_paginator.paginate.return_value = [{
            "StreamNames": ["my-stream-1", "my-stream-2"]
        }]
        mock_client.get_paginator.return_value = mock_paginator

        resources = handler.list_resources()

        streams = [r for r in resources if r["type"] == "stream"]
        assert len(streams) == 2
        assert streams[0]["name"] == "my-stream-1"

    def test_list_resources_empty(self, handler):
        """Test listing when no streams exist."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client

        mock_paginator = MagicMock()
        mock_paginator.paginate.return_value = [{"StreamNames": []}]
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
            "ListStreams"
        )
        mock_client.get_paginator.return_value = mock_paginator

        resources = handler.list_resources()

        assert resources == []
        handler.logger.error.assert_called()

    def test_delete_stream(self, handler):
        """Test deleting a Kinesis stream."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client

        resource = {"id": "arn:...", "name": "my-stream", "type": "stream"}
        result = handler.delete_resource(resource)

        assert result is True
        mock_client.delete_stream.assert_called_once()

    def test_delete_handles_error(self, handler):
        """Test error handling during deletion."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client
        mock_client.delete_stream.side_effect = ClientError(
            {"Error": {"Code": "ResourceNotFoundException", "Message": "Not found"}},
            "DeleteStream"
        )

        resource = {"id": "arn:...", "name": "my-stream", "type": "stream"}
        result = handler.delete_resource(resource)

        assert result is False
        handler.logger.error.assert_called()
