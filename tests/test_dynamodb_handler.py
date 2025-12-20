"""Tests for DynamoDB Handler."""

import pytest
from unittest.mock import MagicMock, patch
from botocore.exceptions import ClientError

from aws_nuker.handlers.dynamodb_handler import DynamoDBHandler


class TestDynamoDBHandler:
    """Tests for DynamoDBHandler class."""

    @pytest.fixture
    def handler(self):
        """Create DynamoDBHandler with mocked session."""
        with patch('aws_nuker.handlers.dynamodb_handler.ResourceHandler.__init__'):
            handler = DynamoDBHandler.__new__(DynamoDBHandler)
            handler.region = "us-east-1"
            handler.dry_run = False
            handler.force = False
            handler.logger = MagicMock()
            handler.session = MagicMock()
        return handler

    def test_service_name(self, handler):
        """Test service_name property."""
        assert handler.service_name == "dynamodb"

    def test_list_resources_tables(self, handler):
        """Test listing DynamoDB tables."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client

        mock_paginator = MagicMock()
        mock_paginator.paginate.return_value = [
            {"TableNames": ["table-1", "table-2"]},
            {"TableNames": ["table-3"]},
        ]
        mock_client.get_paginator.return_value = mock_paginator

        resources = handler.list_resources()

        assert len(resources) == 3
        assert resources[0]["id"] == "table-1"
        assert resources[0]["type"] == "table"
        assert resources[1]["id"] == "table-2"
        assert resources[2]["id"] == "table-3"

    def test_list_resources_empty(self, handler):
        """Test listing when no tables exist."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client

        mock_paginator = MagicMock()
        mock_paginator.paginate.return_value = [{"TableNames": []}]
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
            "ListTables"
        )
        mock_client.get_paginator.return_value = mock_paginator

        resources = handler.list_resources()

        assert resources == []
        handler.logger.error.assert_called()

    def test_delete_table(self, handler):
        """Test deleting a DynamoDB table."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client

        resource = {"id": "my-table", "name": "my-table", "type": "table"}
        result = handler.delete_resource(resource)

        assert result is True
        mock_client.delete_table.assert_called_once_with(TableName="my-table")

    def test_delete_table_handles_error(self, handler):
        """Test error handling during deletion."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client
        mock_client.delete_table.side_effect = ClientError(
            {"Error": {"Code": "ResourceNotFoundException", "Message": "Not found"}},
            "DeleteTable"
        )

        resource = {"id": "my-table", "name": "my-table", "type": "table"}
        result = handler.delete_resource(resource)

        assert result is False
        handler.logger.error.assert_called()
