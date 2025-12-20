"""Tests for RDS Handler."""

import pytest
from unittest.mock import MagicMock, patch
from botocore.exceptions import ClientError

from aws_nuker.handlers.rds_handler import RDSHandler


class TestRDSHandler:
    """Tests for RDSHandler class."""

    @pytest.fixture
    def handler(self):
        """Create RDSHandler with mocked session."""
        with patch('aws_nuker.handlers.rds_handler.ResourceHandler.__init__'):
            handler = RDSHandler.__new__(RDSHandler)
            handler.region = "us-east-1"
            handler.dry_run = False
            handler.force = False
            handler.logger = MagicMock()
            handler.session = MagicMock()
        return handler

    def test_service_name(self, handler):
        """Test service_name property."""
        assert handler.service_name == "rds"

    def test_list_resources_instances(self, handler):
        """Test listing RDS instances."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client

        mock_client.describe_db_instances.return_value = {
            "DBInstances": [{
                "DBInstanceIdentifier": "my-db-instance",
                "Engine": "mysql",
                "DBInstanceStatus": "available"
            }]
        }
        mock_client.describe_db_clusters.return_value = {"DBClusters": []}
        mock_client.describe_db_snapshots.return_value = {"DBSnapshots": []}

        resources = handler.list_resources()

        assert len(resources) == 1
        assert resources[0]["id"] == "my-db-instance"
        assert resources[0]["type"] == "db_instance"
        assert resources[0]["engine"] == "mysql"

    def test_list_resources_clusters(self, handler):
        """Test listing RDS clusters (Aurora)."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client

        mock_client.describe_db_instances.return_value = {"DBInstances": []}
        mock_client.describe_db_clusters.return_value = {
            "DBClusters": [{
                "DBClusterIdentifier": "my-aurora-cluster",
                "Engine": "aurora-mysql",
                "Status": "available"
            }]
        }
        mock_client.describe_db_snapshots.return_value = {"DBSnapshots": []}

        resources = handler.list_resources()

        assert len(resources) == 1
        assert resources[0]["id"] == "my-aurora-cluster"
        assert resources[0]["type"] == "db_cluster"

    def test_list_resources_manual_snapshots(self, handler):
        """Test listing manual RDS snapshots."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client

        mock_client.describe_db_instances.return_value = {"DBInstances": []}
        mock_client.describe_db_clusters.return_value = {"DBClusters": []}
        mock_client.describe_db_snapshots.return_value = {
            "DBSnapshots": [
                {"DBSnapshotIdentifier": "manual-snap", "SnapshotType": "manual", "Status": "available"},
                {"DBSnapshotIdentifier": "automated-snap", "SnapshotType": "automated", "Status": "available"},
            ]
        }

        resources = handler.list_resources()

        # Only manual snapshots should be listed
        assert len(resources) == 1
        assert resources[0]["id"] == "manual-snap"
        assert resources[0]["type"] == "db_snapshot"

    def test_list_resources_handles_error(self, handler):
        """Test error handling during list."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client
        mock_client.describe_db_instances.side_effect = ClientError(
            {"Error": {"Code": "AccessDenied", "Message": "Access Denied"}},
            "DescribeDBInstances"
        )

        resources = handler.list_resources()

        assert resources == []
        handler.logger.error.assert_called()

    def test_delete_db_instance(self, handler):
        """Test deleting a DB instance."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client

        resource = {"id": "my-db-instance", "type": "db_instance"}
        result = handler.delete_resource(resource)

        assert result is True
        mock_client.delete_db_instance.assert_called_once_with(
            DBInstanceIdentifier="my-db-instance",
            SkipFinalSnapshot=True,
            DeleteAutomatedBackups=True
        )

    def test_delete_db_cluster(self, handler):
        """Test deleting a DB cluster."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client

        resource = {"id": "my-aurora-cluster", "type": "db_cluster"}
        result = handler.delete_resource(resource)

        assert result is True
        mock_client.delete_db_cluster.assert_called_once_with(
            DBClusterIdentifier="my-aurora-cluster",
            SkipFinalSnapshot=True
        )

    def test_delete_db_snapshot(self, handler):
        """Test deleting a DB snapshot."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client

        resource = {"id": "my-snapshot", "type": "db_snapshot"}
        result = handler.delete_resource(resource)

        assert result is True
        mock_client.delete_db_snapshot.assert_called_once_with(
            DBSnapshotIdentifier="my-snapshot"
        )

    def test_delete_unknown_type(self, handler):
        """Test deleting an unknown resource type."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client

        resource = {"id": "unknown", "type": "unknown_type"}
        result = handler.delete_resource(resource)

        assert result is False

    def test_delete_handles_error(self, handler):
        """Test error handling during deletion."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client
        mock_client.delete_db_instance.side_effect = ClientError(
            {"Error": {"Code": "DBInstanceNotFound", "Message": "Not found"}},
            "DeleteDBInstance"
        )

        resource = {"id": "my-db-instance", "type": "db_instance"}
        result = handler.delete_resource(resource)

        assert result is False
        handler.logger.error.assert_called()
