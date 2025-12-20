"""Tests for CloudWatch Handler."""

import pytest
from unittest.mock import MagicMock, patch
from botocore.exceptions import ClientError

from aws_nuker.handlers.cloudwatch_handler import CloudWatchHandler


class TestCloudWatchHandler:
    """Tests for CloudWatchHandler class."""

    @pytest.fixture
    def handler(self):
        """Create CloudWatchHandler with mocked session."""
        with patch('aws_nuker.handlers.cloudwatch_handler.ResourceHandler.__init__'):
            handler = CloudWatchHandler.__new__(CloudWatchHandler)
            handler.region = "us-east-1"
            handler.dry_run = False
            handler.force = False
            handler.logger = MagicMock()
            handler.session = MagicMock()
        return handler

    def test_service_name(self, handler):
        """Test service_name property."""
        assert handler.service_name == "cloudwatch"

    def test_list_resources_alarms(self, handler):
        """Test listing CloudWatch alarms."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client

        mock_paginator = MagicMock()
        mock_paginator.paginate.return_value = [{
            "MetricAlarms": [{
                "AlarmName": "my-alarm",
                "AlarmArn": "arn:aws:cloudwatch:us-east-1:123456789012:alarm:my-alarm"
            }]
        }]
        mock_client.get_paginator.return_value = mock_paginator

        resources = handler.list_resources()

        alarms = [r for r in resources if r["type"] == "alarm"]
        assert len(alarms) == 1
        assert alarms[0]["name"] == "my-alarm"

    def test_list_resources_dashboards(self, handler):
        """Test listing CloudWatch log groups (actual implementation uses logs, not dashboards)."""
        mock_cw = MagicMock()
        mock_logs = MagicMock()
        
        def client_factory(service, **kwargs):
            if service == "cloudwatch":
                return mock_cw
            elif service == "logs":
                return mock_logs
            return MagicMock()
        
        handler.session.client.side_effect = client_factory

        mock_alarm_paginator = MagicMock()
        mock_alarm_paginator.paginate.return_value = [{"MetricAlarms": []}]
        mock_cw.get_paginator.return_value = mock_alarm_paginator
        
        mock_logs_paginator = MagicMock()
        mock_logs_paginator.paginate.return_value = [{
            "logGroups": [{
                "logGroupName": "/aws/lambda/my-function",
            }]
        }]
        mock_logs.get_paginator.return_value = mock_logs_paginator

        resources = handler.list_resources()

        log_groups = [r for r in resources if r["type"] == "log_group"]
        assert len(log_groups) == 1
        assert log_groups[0]["name"] == "/aws/lambda/my-function"

    def test_list_resources_handles_error(self, handler):
        """Test error handling during list."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client
        
        mock_paginator = MagicMock()
        mock_paginator.paginate.side_effect = ClientError(
            {"Error": {"Code": "AccessDenied", "Message": "Access Denied"}},
            "DescribeAlarms"
        )
        mock_client.get_paginator.return_value = mock_paginator

        resources = handler.list_resources()

        assert resources == []
        handler.logger.error.assert_called()

    def test_delete_alarm(self, handler):
        """Test deleting a CloudWatch alarm."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client

        resource = {"id": "arn:...", "name": "my-alarm", "type": "alarm"}
        result = handler.delete_resource(resource)

        assert result is True
        mock_client.delete_alarms.assert_called_once_with(AlarmNames=["my-alarm"])

    def test_delete_log_group(self, handler):
        """Test deleting a CloudWatch log group."""
        mock_logs = MagicMock()
        handler.session.client.return_value = mock_logs

        resource = {"id": "/aws/lambda/my-function", "name": "/aws/lambda/my-function", "type": "log_group"}
        result = handler.delete_resource(resource)

        assert result is True
        mock_logs.delete_log_group.assert_called_once_with(logGroupName="/aws/lambda/my-function")

    def test_delete_handles_error(self, handler):
        """Test error handling during deletion."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client
        mock_client.delete_alarms.side_effect = ClientError(
            {"Error": {"Code": "ResourceNotFound", "Message": "Not found"}},
            "DeleteAlarms"
        )

        resource = {"id": "arn:...", "name": "my-alarm", "type": "alarm"}
        result = handler.delete_resource(resource)

        assert result is False
        handler.logger.error.assert_called()
