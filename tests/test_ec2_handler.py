"""Tests for EC2 Handler."""

import pytest
from unittest.mock import MagicMock, patch
from botocore.exceptions import ClientError

from aws_nuker.handlers.ec2_handler import EC2Handler


class TestEC2Handler:
    """Tests for EC2Handler class."""

    @pytest.fixture
    def handler(self):
        """Create EC2Handler with mocked session."""
        with patch('aws_nuker.handlers.ec2_handler.ResourceHandler.__init__'):
            handler = EC2Handler.__new__(EC2Handler)
            handler.region = "us-east-1"
            handler.dry_run = False
            handler.force = False
            handler.logger = MagicMock()
            handler.session = MagicMock()
        return handler

    def test_service_name(self, handler):
        """Test service_name property."""
        assert handler.service_name == "ec2"

    def test_list_resources_instances(self, handler):
        """Test listing EC2 instances."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client

        mock_client.describe_instances.return_value = {
            "Reservations": [{
                "Instances": [{
                    "InstanceId": "i-1234567890abcdef0",
                    "State": {"Name": "running"},
                    "Tags": [{"Key": "Name", "Value": "test-instance"}]
                }]
            }]
        }
        mock_client.describe_volumes.return_value = {"Volumes": []}
        mock_client.describe_snapshots.return_value = {"Snapshots": []}
        mock_client.describe_images.return_value = {"Images": []}
        mock_client.describe_security_groups.return_value = {"SecurityGroups": []}
        mock_client.describe_key_pairs.return_value = {"KeyPairs": []}
        mock_client.describe_addresses.return_value = {"Addresses": []}

        resources = handler.list_resources()

        assert len(resources) == 1
        assert resources[0]["id"] == "i-1234567890abcdef0"
        assert resources[0]["type"] == "instance"
        assert resources[0]["name"] == "test-instance"

    def test_list_resources_volumes(self, handler):
        """Test listing unattached EBS volumes."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client

        mock_client.describe_instances.return_value = {"Reservations": []}
        mock_client.describe_volumes.return_value = {
            "Volumes": [{
                "VolumeId": "vol-1234567890abcdef0",
                "State": "available",
                "Attachments": [],
                "Tags": [{"Key": "Name", "Value": "test-volume"}]
            }]
        }
        mock_client.describe_snapshots.return_value = {"Snapshots": []}
        mock_client.describe_images.return_value = {"Images": []}
        mock_client.describe_security_groups.return_value = {"SecurityGroups": []}
        mock_client.describe_key_pairs.return_value = {"KeyPairs": []}
        mock_client.describe_addresses.return_value = {"Addresses": []}

        resources = handler.list_resources()

        assert len(resources) == 1
        assert resources[0]["id"] == "vol-1234567890abcdef0"
        assert resources[0]["type"] == "volume"

    def test_list_resources_skips_attached_volumes(self, handler):
        """Test that attached volumes are skipped."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client

        mock_client.describe_instances.return_value = {"Reservations": []}
        mock_client.describe_volumes.return_value = {
            "Volumes": [{
                "VolumeId": "vol-attached",
                "State": "in-use",
                "Attachments": [{"InstanceId": "i-123"}]
            }]
        }
        mock_client.describe_snapshots.return_value = {"Snapshots": []}
        mock_client.describe_images.return_value = {"Images": []}
        mock_client.describe_security_groups.return_value = {"SecurityGroups": []}
        mock_client.describe_key_pairs.return_value = {"KeyPairs": []}
        mock_client.describe_addresses.return_value = {"Addresses": []}

        resources = handler.list_resources()

        # Attached volumes should not be in the list
        volume_ids = [r["id"] for r in resources if r.get("type") == "volume"]
        assert "vol-attached" not in volume_ids

    def test_list_resources_snapshots(self, handler):
        """Test listing EBS snapshots."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client

        mock_client.describe_instances.return_value = {"Reservations": []}
        mock_client.describe_volumes.return_value = {"Volumes": []}
        mock_client.describe_snapshots.return_value = {
            "Snapshots": [{
                "SnapshotId": "snap-1234567890abcdef0",
                "State": "completed",
                "Tags": []
            }]
        }
        mock_client.describe_images.return_value = {"Images": []}
        mock_client.describe_security_groups.return_value = {"SecurityGroups": []}
        mock_client.describe_key_pairs.return_value = {"KeyPairs": []}
        mock_client.describe_addresses.return_value = {"Addresses": []}

        resources = handler.list_resources()

        assert len(resources) == 1
        assert resources[0]["id"] == "snap-1234567890abcdef0"
        assert resources[0]["type"] == "snapshot"

    def test_list_resources_security_groups(self, handler):
        """Test listing security groups (excluding default)."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client

        mock_client.describe_instances.return_value = {"Reservations": []}
        mock_client.describe_volumes.return_value = {"Volumes": []}
        mock_client.describe_snapshots.return_value = {"Snapshots": []}
        mock_client.describe_images.return_value = {"Images": []}
        mock_client.describe_security_groups.return_value = {
            "SecurityGroups": [
                {"GroupId": "sg-default", "GroupName": "default"},
                {"GroupId": "sg-custom", "GroupName": "my-sg"}
            ]
        }
        mock_client.describe_key_pairs.return_value = {"KeyPairs": []}
        mock_client.describe_addresses.return_value = {"Addresses": []}

        resources = handler.list_resources()

        # Only non-default security group should be listed
        sg_ids = [r["id"] for r in resources if r.get("type") == "security_group"]
        assert "sg-custom" in sg_ids
        assert "sg-default" not in sg_ids

    def test_list_resources_handles_error(self, handler):
        """Test error handling during list."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client
        mock_client.describe_instances.side_effect = ClientError(
            {"Error": {"Code": "AccessDenied", "Message": "Access Denied"}},
            "DescribeInstances"
        )

        resources = handler.list_resources()

        assert resources == []
        handler.logger.error.assert_called()

    def test_delete_resource_instance(self, handler):
        """Test deleting an EC2 instance."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client

        resource = {"id": "i-1234567890abcdef0", "type": "instance"}
        result = handler.delete_resource(resource)

        assert result is True
        mock_client.terminate_instances.assert_called_once_with(
            InstanceIds=["i-1234567890abcdef0"]
        )

    def test_delete_resource_volume(self, handler):
        """Test deleting an EBS volume."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client

        resource = {"id": "vol-1234567890abcdef0", "type": "volume"}
        result = handler.delete_resource(resource)

        assert result is True
        mock_client.delete_volume.assert_called_once_with(
            VolumeId="vol-1234567890abcdef0"
        )

    def test_delete_resource_snapshot(self, handler):
        """Test deleting an EBS snapshot."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client

        resource = {"id": "snap-1234567890abcdef0", "type": "snapshot"}
        result = handler.delete_resource(resource)

        assert result is True
        mock_client.delete_snapshot.assert_called_once_with(
            SnapshotId="snap-1234567890abcdef0"
        )

    def test_delete_resource_ami(self, handler):
        """Test deregistering an AMI."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client

        resource = {"id": "ami-1234567890abcdef0", "type": "ami"}
        result = handler.delete_resource(resource)

        assert result is True
        mock_client.deregister_image.assert_called_once_with(
            ImageId="ami-1234567890abcdef0"
        )

    def test_delete_resource_security_group(self, handler):
        """Test deleting a security group."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client

        resource = {"id": "sg-1234567890abcdef0", "type": "security_group"}
        result = handler.delete_resource(resource)

        assert result is True
        mock_client.delete_security_group.assert_called_once_with(
            GroupId="sg-1234567890abcdef0"
        )

    def test_delete_resource_key_pair(self, handler):
        """Test deleting a key pair."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client

        resource = {"id": "key-1234567890abcdef0", "type": "key_pair"}
        result = handler.delete_resource(resource)

        assert result is True
        mock_client.delete_key_pair.assert_called_once_with(
            KeyPairId="key-1234567890abcdef0"
        )

    def test_delete_resource_elastic_ip_allocation(self, handler):
        """Test releasing an elastic IP by allocation ID."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client

        resource = {"id": "eipalloc-1234567890abcdef0", "type": "elastic_ip"}
        result = handler.delete_resource(resource)

        assert result is True
        mock_client.release_address.assert_called_once_with(
            AllocationId="eipalloc-1234567890abcdef0"
        )

    def test_delete_resource_elastic_ip_public(self, handler):
        """Test releasing an elastic IP by public IP."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client

        resource = {"id": "1.2.3.4", "type": "elastic_ip"}
        result = handler.delete_resource(resource)

        assert result is True
        mock_client.release_address.assert_called_once_with(PublicIp="1.2.3.4")

    def test_delete_resource_unknown_type(self, handler):
        """Test deleting an unknown resource type."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client

        resource = {"id": "unknown-123", "type": "unknown_type"}
        result = handler.delete_resource(resource)

        assert result is False

    def test_delete_resource_handles_error(self, handler):
        """Test error handling during deletion."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client
        mock_client.terminate_instances.side_effect = ClientError(
            {"Error": {"Code": "InstanceNotFound", "Message": "Not found"}},
            "TerminateInstances"
        )

        resource = {"id": "i-1234567890abcdef0", "type": "instance"}
        result = handler.delete_resource(resource)

        assert result is False
        handler.logger.error.assert_called()

    def test_is_default_resource_default_sg(self, handler):
        """Test identifying default security group."""
        resource = {"type": "security_group", "name": "default"}
        assert handler.is_default_resource(resource) is True

    def test_is_default_resource_non_default(self, handler):
        """Test identifying non-default resource."""
        resource = {"type": "security_group", "name": "my-sg"}
        assert handler.is_default_resource(resource) is False

    def test_get_tag_name(self):
        """Test extracting name from tags."""
        tags = [{"Key": "Name", "Value": "my-resource"}, {"Key": "Env", "Value": "prod"}]
        assert EC2Handler._get_tag_name(tags) == "my-resource"

    def test_get_tag_name_no_name_tag(self):
        """Test extracting name when Name tag is missing."""
        tags = [{"Key": "Env", "Value": "prod"}]
        assert EC2Handler._get_tag_name(tags) == ""

    def test_get_tag_name_empty_tags(self):
        """Test extracting name from empty tags list."""
        assert EC2Handler._get_tag_name([]) == ""
