"""Tests for ElastiCache Handler."""

import pytest
from unittest.mock import MagicMock, patch
from botocore.exceptions import ClientError

from aws_nuker.handlers.elasticache_handler import ElastiCacheHandler


class TestElastiCacheHandler:
    """Tests for ElastiCacheHandler class."""

    @pytest.fixture
    def handler(self):
        """Create ElastiCacheHandler with mocked session."""
        with patch('aws_nuker.handlers.elasticache_handler.ResourceHandler.__init__'):
            handler = ElastiCacheHandler.__new__(ElastiCacheHandler)
            handler.region = "us-east-1"
            handler.dry_run = False
            handler.force = False
            handler.logger = MagicMock()
            handler.session = MagicMock()
        return handler

    def test_service_name(self, handler):
        """Test service_name property."""
        assert handler.service_name == "elasticache"

    def test_list_resources_clusters(self, handler):
        """Test listing ElastiCache clusters."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client

        mock_client.describe_cache_clusters.return_value = {
            "CacheClusters": [{
                "CacheClusterId": "my-redis-cluster",
                "CacheNodeType": "cache.t3.micro",
                "Engine": "redis",
                "CacheClusterStatus": "available"
            }]
        }
        mock_client.describe_replication_groups.return_value = {
            "ReplicationGroups": []
        }

        resources = handler.list_resources()

        clusters = [r for r in resources if r["type"] == "cache_cluster"]
        assert len(clusters) == 1
        assert clusters[0]["name"] == "my-redis-cluster"
        assert clusters[0]["engine"] == "redis"

    def test_list_resources_replication_groups(self, handler):
        """Test listing ElastiCache replication groups."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client

        mock_client.describe_cache_clusters.return_value = {"CacheClusters": []}
        mock_client.describe_replication_groups.return_value = {
            "ReplicationGroups": [{
                "ReplicationGroupId": "my-replication-group",
                "Description": "My Redis Cluster",
                "Status": "available"
            }]
        }

        resources = handler.list_resources()

        rgs = [r for r in resources if r["type"] == "replication_group"]
        assert len(rgs) == 1
        assert rgs[0]["name"] == "my-replication-group"

    def test_list_resources_handles_error(self, handler):
        """Test error handling during list."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client
        mock_client.describe_cache_clusters.side_effect = ClientError(
            {"Error": {"Code": "AccessDenied", "Message": "Access Denied"}},
            "DescribeCacheClusters"
        )

        resources = handler.list_resources()

        assert resources == []
        handler.logger.error.assert_called()

    def test_delete_cluster(self, handler):
        """Test deleting an ElastiCache cluster."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client

        resource = {"id": "my-redis-cluster", "name": "my-redis-cluster", "type": "cache_cluster"}
        result = handler.delete_resource(resource)

        assert result is True
        mock_client.delete_cache_cluster.assert_called_once_with(
            CacheClusterId="my-redis-cluster"
        )

    def test_delete_replication_group(self, handler):
        """Test deleting an ElastiCache replication group."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client

        resource = {
            "id": "my-replication-group",
            "name": "my-replication-group",
            "type": "replication_group"
        }
        result = handler.delete_resource(resource)

        assert result is True
        mock_client.delete_replication_group.assert_called_once()

    def test_delete_handles_error(self, handler):
        """Test error handling during deletion."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client
        mock_client.delete_cache_cluster.side_effect = ClientError(
            {"Error": {"Code": "CacheClusterNotFound", "Message": "Not found"}},
            "DeleteCacheCluster"
        )

        resource = {"id": "my-cluster", "name": "my-cluster", "type": "cache_cluster"}
        result = handler.delete_resource(resource)

        assert result is False
        handler.logger.error.assert_called()
