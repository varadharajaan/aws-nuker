"""Tests for S3 Handler."""

import pytest
from unittest.mock import MagicMock, patch, PropertyMock
from botocore.exceptions import ClientError

from aws_nuker.handlers.s3_handler import S3Handler


class TestS3Handler:
    """Tests for S3Handler class."""

    @pytest.fixture
    def handler(self):
        """Create S3Handler with mocked session."""
        with patch('aws_nuker.handlers.s3_handler.ResourceHandler.__init__'):
            handler = S3Handler.__new__(S3Handler)
            handler.region = "us-east-1"
            handler.dry_run = False
            handler.force = False
            handler.logger = MagicMock()
            handler.session = MagicMock()
        return handler

    def test_service_name(self, handler):
        """Test service_name property."""
        assert handler.service_name == "s3"

    def test_list_resources_buckets(self, handler):
        """Test listing S3 buckets in the current region."""
        mock_s3 = MagicMock()
        mock_s3control = MagicMock()
        mock_sts = MagicMock()
        
        def client_factory(service, **kwargs):
            if service == "s3":
                return mock_s3
            elif service == "s3control":
                return mock_s3control
            elif service == "sts":
                return mock_sts
            return MagicMock()
        
        handler.session.client.side_effect = client_factory
        handler.session.resource.return_value = MagicMock()

        mock_s3.list_buckets.return_value = {
            "Buckets": [
                {"Name": "test-bucket-1", "CreationDate": "2023-01-01T00:00:00Z"},
            ]
        }
        mock_s3.get_bucket_location.return_value = {"LocationConstraint": None}  # us-east-1
        mock_s3.get_bucket_versioning.return_value = {"Status": "Disabled"}
        mock_s3.get_bucket_encryption.side_effect = ClientError(
            {"Error": {"Code": "ServerSideEncryptionConfigurationNotFoundError"}}, 
            "GetBucketEncryption"
        )

        # Mock S3 control calls to return empty lists
        mock_sts.get_caller_identity.return_value = {"Account": "123456789012"}
        mock_s3control.get_paginator.return_value.paginate.return_value = []

        resources = handler._list_buckets()

        assert len(resources) == 1
        assert resources[0]["id"] == "test-bucket-1"
        assert resources[0]["type"] == "bucket"

    def test_list_resources_different_region(self, handler):
        """Test that buckets in different regions are excluded."""
        mock_s3 = MagicMock()
        handler.session.client.return_value = mock_s3

        mock_s3.list_buckets.return_value = {
            "Buckets": [
                {"Name": "test-bucket-1"},
            ]
        }
        # Bucket is in eu-west-1, not us-east-1
        mock_s3.get_bucket_location.return_value = {"LocationConstraint": "eu-west-1"}

        resources = handler._list_buckets()

        assert len(resources) == 0

    def test_list_buckets_access_denied(self, handler):
        """Test handling access denied for bucket location."""
        mock_s3 = MagicMock()
        handler.session.client.return_value = mock_s3

        mock_s3.list_buckets.return_value = {
            "Buckets": [{"Name": "inaccessible-bucket"}]
        }
        mock_s3.get_bucket_location.side_effect = ClientError(
            {"Error": {"Code": "AccessDenied", "Message": "Access Denied"}},
            "GetBucketLocation"
        )

        resources = handler._list_buckets()

        assert len(resources) == 0

    def test_delete_bucket(self, handler):
        """Test deleting an S3 bucket."""
        mock_s3 = MagicMock()
        mock_s3_resource = MagicMock()
        handler.session.client.return_value = mock_s3
        handler.session.resource.return_value = mock_s3_resource

        # Mock versioning status
        mock_versioning = MagicMock()
        mock_versioning.status = None  # Not enabled
        mock_s3_resource.BucketVersioning.return_value = mock_versioning

        # Mock bucket
        mock_bucket = MagicMock()
        mock_s3_resource.Bucket.return_value = mock_bucket

        resource = {"id": "test-bucket", "type": "bucket"}
        result = handler._delete_bucket("test-bucket")

        assert result is True
        mock_bucket.objects.all().delete.assert_called_once()
        mock_s3.delete_bucket.assert_called_once_with(Bucket="test-bucket")

    def test_empty_bucket_with_versioning(self, handler):
        """Test emptying a versioned bucket."""
        mock_s3_resource = MagicMock()
        handler.session.resource.return_value = mock_s3_resource

        # Mock versioning enabled
        mock_versioning = MagicMock()
        mock_versioning.status = "Enabled"
        mock_s3_resource.BucketVersioning.return_value = mock_versioning

        # Mock bucket
        mock_bucket = MagicMock()
        mock_s3_resource.Bucket.return_value = mock_bucket

        handler._empty_bucket("versioned-bucket")

        # Should delete object versions when versioning is enabled
        mock_bucket.object_versions.all().delete.assert_called_once()

    def test_extract_mrap_buckets(self, handler):
        """Test extracting bucket names from MRAP config."""
        regions_config = [
            {"Bucket": "bucket-1"},
            {"Bucket": "arn:aws:s3:::bucket-2"},
            {"Bucket": "account/bucket-3"},
        ]

        result = handler._extract_mrap_buckets(regions_config)

        assert "bucket-1" in result
        assert "bucket-2" in result
        assert "bucket-3" in result

    def test_delete_resource_unknown_type(self, handler):
        """Test deleting an unknown resource type."""
        resource = {"id": "unknown", "type": "unknown_type"}
        result = handler.delete_resource(resource)
        assert result is False


class TestS3AccessPoints:
    """Tests for S3 Access Points functionality."""

    @pytest.fixture
    def handler(self):
        """Create S3Handler with mocked session."""
        with patch('aws_nuker.handlers.s3_handler.ResourceHandler.__init__'):
            handler = S3Handler.__new__(S3Handler)
            handler.region = "us-east-1"
            handler.dry_run = False
            handler.force = False
            handler.logger = MagicMock()
            handler.session = MagicMock()
        return handler

    def test_list_access_points(self, handler):
        """Test listing S3 access points."""
        mock_s3control = MagicMock()
        mock_sts = MagicMock()

        def client_factory(service, **kwargs):
            if service == "s3control":
                return mock_s3control
            elif service == "sts":
                return mock_sts
            return MagicMock()

        handler.session.client.side_effect = client_factory

        mock_sts.get_caller_identity.return_value = {"Account": "123456789012"}

        mock_paginator = MagicMock()
        mock_paginator.paginate.return_value = [{
            "AccessPointList": [{
                "Name": "my-access-point",
                "Bucket": "my-bucket",
                "AccessPointArn": "arn:aws:s3:us-east-1:123456789012:accesspoint/my-access-point",
                "NetworkOrigin": "Internet"
            }]
        }]
        mock_s3control.get_paginator.return_value = mock_paginator

        resources = handler._list_access_points()

        assert len(resources) == 1
        assert resources[0]["id"] == "my-access-point"
        assert resources[0]["type"] == "access_point"
        assert resources[0]["bucket"] == "my-bucket"

    def test_delete_access_point(self, handler):
        """Test deleting an S3 access point."""
        mock_s3control = MagicMock()
        mock_sts = MagicMock()

        def client_factory(service, **kwargs):
            if service == "s3control":
                return mock_s3control
            elif service == "sts":
                return mock_sts
            return MagicMock()

        handler.session.client.side_effect = client_factory
        mock_sts.get_caller_identity.return_value = {"Account": "123456789012"}

        result = handler._delete_access_point("my-access-point")

        assert result is True
        mock_s3control.delete_access_point.assert_called_once_with(
            AccountId="123456789012",
            Name="my-access-point"
        )
