"""Tests for CloudFormation Handler."""

import pytest
from unittest.mock import MagicMock, patch
from botocore.exceptions import ClientError

from aws_nuker.handlers.cloudformation_handler import CloudFormationHandler


class TestCloudFormationHandler:
    """Tests for CloudFormationHandler class."""

    @pytest.fixture
    def handler(self):
        """Create CloudFormationHandler with mocked session."""
        with patch('aws_nuker.handlers.cloudformation_handler.ResourceHandler.__init__'):
            handler = CloudFormationHandler.__new__(CloudFormationHandler)
            handler.region = "us-east-1"
            handler.dry_run = False
            handler.force = False
            handler.logger = MagicMock()
            handler.session = MagicMock()
        return handler

    def test_service_name(self, handler):
        """Test service_name property."""
        assert handler.service_name == "cloudformation"

    def test_list_resources_stacks(self, handler):
        """Test listing CloudFormation stacks."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client

        mock_paginator = MagicMock()
        mock_paginator.paginate.return_value = [{
            "StackSummaries": [{
                "StackName": "my-stack",
                "StackId": "arn:aws:cloudformation:us-east-1:123456789012:stack/my-stack/...",
                "StackStatus": "CREATE_COMPLETE"
            }]
        }]
        mock_client.get_paginator.return_value = mock_paginator

        resources = handler.list_resources()

        stacks = [r for r in resources if r["type"] == "stack"]
        assert len(stacks) == 1
        assert stacks[0]["name"] == "my-stack"

    def test_list_resources_filters_deleted_stacks(self, handler):
        """Test that deleted stacks are filtered out."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client

        mock_paginator = MagicMock()
        mock_paginator.paginate.return_value = [{
            "StackSummaries": [
                {"StackName": "active-stack", "StackId": "arn:...:active", "StackStatus": "CREATE_COMPLETE"},
                {"StackName": "deleted-stack", "StackId": "arn:...:deleted", "StackStatus": "DELETE_COMPLETE"},
            ]
        }]
        mock_client.get_paginator.return_value = mock_paginator

        resources = handler.list_resources()

        # Only active stack should be listed
        assert len(resources) == 1
        assert resources[0]["name"] == "active-stack"

    def test_list_resources_handles_error(self, handler):
        """Test error handling during list."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client
        
        mock_paginator = MagicMock()
        mock_paginator.paginate.side_effect = ClientError(
            {"Error": {"Code": "AccessDenied", "Message": "Access Denied"}},
            "ListStacks"
        )
        mock_client.get_paginator.return_value = mock_paginator

        resources = handler.list_resources()

        assert resources == []
        handler.logger.error.assert_called()

    def test_delete_stack(self, handler):
        """Test deleting a CloudFormation stack."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client

        resource = {"id": "arn:...", "name": "my-stack", "type": "stack"}
        result = handler.delete_resource(resource)

        assert result is True
        mock_client.delete_stack.assert_called_once_with(StackName="my-stack")

    def test_delete_handles_error(self, handler):
        """Test error handling during deletion."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client
        mock_client.delete_stack.side_effect = ClientError(
            {"Error": {"Code": "StackNotFoundException", "Message": "Not found"}},
            "DeleteStack"
        )

        resource = {"id": "arn:...", "name": "my-stack", "type": "stack"}
        result = handler.delete_resource(resource)

        assert result is False
        handler.logger.error.assert_called()
