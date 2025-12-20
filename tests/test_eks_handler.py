"""Tests for EKS Handler."""

import pytest
from unittest.mock import MagicMock, patch
from botocore.exceptions import ClientError

from aws_nuker.handlers.eks_handler import EKSHandler


class TestEKSHandler:
    """Tests for EKSHandler class."""

    @pytest.fixture
    def handler(self):
        """Create EKSHandler with mocked session."""
        with patch('aws_nuker.handlers.eks_handler.ResourceHandler.__init__'):
            handler = EKSHandler.__new__(EKSHandler)
            handler.region = "us-east-1"
            handler.dry_run = False
            handler.force = False
            handler.logger = MagicMock()
            handler.session = MagicMock()
        return handler

    def test_service_name(self, handler):
        """Test service_name property."""
        assert handler.service_name == "eks"

    def test_list_resources_clusters(self, handler):
        """Test listing EKS clusters."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client

        mock_client.list_clusters.return_value = {
            "clusters": ["my-cluster"]
        }
        mock_client.describe_cluster.return_value = {
            "cluster": {
                "name": "my-cluster",
                "arn": "arn:aws:eks:us-east-1:123456789012:cluster/my-cluster",
                "status": "ACTIVE"
            }
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
        """Test deleting an EKS cluster."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client
        mock_client.list_nodegroups.return_value = {"nodegroups": []}
        mock_client.list_fargate_profiles.return_value = {"fargateProfileNames": []}

        resource = {"id": "arn:...", "name": "my-cluster", "type": "cluster"}
        result = handler.delete_resource(resource)

        assert result is True
        mock_client.delete_cluster.assert_called_once()


class TestEKSNodegroups:
    """Tests for EKS nodegroup functionality."""

    @pytest.fixture
    def handler(self):
        """Create EKSHandler with mocked session."""
        with patch('aws_nuker.handlers.eks_handler.ResourceHandler.__init__'):
            handler = EKSHandler.__new__(EKSHandler)
            handler.region = "us-east-1"
            handler.dry_run = False
            handler.force = False
            handler.logger = MagicMock()
            handler.session = MagicMock()
        return handler

    def test_delete_cluster_with_nodegroups(self, handler):
        """Test deleting an EKS cluster first deletes its nodegroups."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client

        mock_client.list_nodegroups.return_value = {
            "nodegroups": ["my-nodegroup"]
        }

        resource = {
            "id": "my-cluster",
            "name": "my-cluster",
            "type": "cluster"
        }
        result = handler.delete_resource(resource)

        assert result is True
        mock_client.delete_nodegroup.assert_called_once()
        mock_client.delete_cluster.assert_called_once_with(name="my-cluster")
