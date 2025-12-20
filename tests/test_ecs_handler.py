"""Tests for ECS Handler."""

import pytest
from unittest.mock import MagicMock, patch
from botocore.exceptions import ClientError

from aws_nuker.handlers.ecs_handler import ECSHandler


class TestECSHandler:
    """Tests for ECSHandler class."""

    @pytest.fixture
    def handler(self):
        """Create ECSHandler with mocked session."""
        with patch('aws_nuker.handlers.ecs_handler.ResourceHandler.__init__'):
            handler = ECSHandler.__new__(ECSHandler)
            handler.region = "us-east-1"
            handler.dry_run = False
            handler.force = False
            handler.logger = MagicMock()
            handler.session = MagicMock()
        return handler

    def test_service_name(self, handler):
        """Test service_name property."""
        assert handler.service_name == "ecs"

    def test_list_resources_clusters(self, handler):
        """Test listing ECS clusters."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client

        mock_client.list_clusters.return_value = {
            "clusterArns": [
                "arn:aws:ecs:us-east-1:123456789012:cluster/my-cluster"
            ]
        }
        mock_client.describe_clusters.return_value = {
            "clusters": [{
                "clusterArn": "arn:aws:ecs:us-east-1:123456789012:cluster/my-cluster",
                "clusterName": "my-cluster",
                "status": "ACTIVE"
            }]
        }

        resources = handler.list_resources()

        clusters = [r for r in resources if r["type"] == "cluster"]
        assert len(clusters) == 1
        assert clusters[0]["name"] == "my-cluster"

    def test_list_resources_handles_error(self, handler):
        """Test error handling during list."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client
        mock_client.list_clusters.side_effect = ClientError(
            {"Error": {"Code": "AccessDenied", "Message": "Access Denied"}},
            "ListClusters"
        )

        resources = handler.list_resources()

        assert resources == []
        handler.logger.error.assert_called()

    def test_delete_cluster(self, handler):
        """Test deleting an ECS cluster."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client
        mock_client.list_services.return_value = {"serviceArns": []}
        mock_client.list_tasks.return_value = {"taskArns": []}

        resource = {"id": "arn:...", "name": "my-cluster", "type": "cluster"}
        result = handler.delete_resource(resource)

        assert result is True
        mock_client.delete_cluster.assert_called_once()

    def test_delete_service(self, handler):
        """Test deleting an ECS service."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client

        resource = {
            "id": "arn:...",
            "name": "my-service",
            "type": "service",
            "cluster": "my-cluster"
        }
        result = handler.delete_resource(resource)

        # Should update to 0 and then delete
        assert result is True
