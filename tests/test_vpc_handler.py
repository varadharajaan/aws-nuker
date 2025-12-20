"""Tests for VPC Handler."""

import pytest
from unittest.mock import MagicMock, patch
from botocore.exceptions import ClientError

from aws_nuker.handlers.vpc_handler import VPCHandler


class TestVPCHandler:
    """Tests for VPCHandler class."""

    @pytest.fixture
    def handler(self):
        """Create VPCHandler with mocked session."""
        with patch('aws_nuker.handlers.vpc_handler.ResourceHandler.__init__'):
            handler = VPCHandler.__new__(VPCHandler)
            handler.region = "us-east-1"
            handler.dry_run = False
            handler.force = False
            handler.logger = MagicMock()
            handler.session = MagicMock()
        return handler

    def test_service_name(self, handler):
        """Test service_name property."""
        assert handler.service_name == "vpc"

    def test_list_resources_vpcs(self, handler):
        """Test listing VPCs (excluding default)."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client

        mock_client.describe_vpcs.return_value = {
            "Vpcs": [
                {"VpcId": "vpc-default", "IsDefault": True, "Tags": []},
                {"VpcId": "vpc-custom", "IsDefault": False, "Tags": [{"Key": "Name", "Value": "my-vpc"}]},
            ]
        }
        mock_client.describe_subnets.return_value = {"Subnets": []}
        mock_client.describe_internet_gateways.return_value = {"InternetGateways": []}
        mock_client.describe_nat_gateways.return_value = {"NatGateways": []}
        mock_client.describe_route_tables.return_value = {"RouteTables": []}

        resources = handler.list_resources()

        vpcs = [r for r in resources if r["type"] == "vpc"]
        # Only non-default VPC should be listed
        assert len(vpcs) == 1
        assert vpcs[0]["id"] == "vpc-custom"

    def test_list_resources_subnets(self, handler):
        """Test listing subnets."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client

        mock_client.describe_vpcs.side_effect = [
            {"Vpcs": []},  # First call - list VPCs
            {"Vpcs": [{"VpcId": "vpc-123", "IsDefault": False}]},  # describe_vpcs for subnet
        ]
        mock_client.describe_subnets.return_value = {
            "Subnets": [{
                "SubnetId": "subnet-123",
                "VpcId": "vpc-123",
                "Tags": [{"Key": "Name", "Value": "my-subnet"}]
            }]
        }
        mock_client.describe_internet_gateways.return_value = {"InternetGateways": []}
        mock_client.describe_nat_gateways.return_value = {"NatGateways": []}

        resources = handler.list_resources()

        subnets = [r for r in resources if r["type"] == "subnet"]
        assert len(subnets) == 1
        assert subnets[0]["id"] == "subnet-123"

    def test_list_resources_internet_gateways(self, handler):
        """Test listing internet gateways."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client

        mock_client.describe_vpcs.side_effect = [
            {"Vpcs": []},  # First call - list VPCs
            {"Vpcs": [{"VpcId": "vpc-123", "IsDefault": False}]},  # describe_vpcs for IGW
        ]
        mock_client.describe_subnets.return_value = {"Subnets": []}
        mock_client.describe_internet_gateways.return_value = {
            "InternetGateways": [{
                "InternetGatewayId": "igw-123",
                "Attachments": [{"VpcId": "vpc-123"}],
                "Tags": []
            }]
        }
        mock_client.describe_nat_gateways.return_value = {"NatGateways": []}

        resources = handler.list_resources()

        igws = [r for r in resources if r["type"] == "internet_gateway"]
        assert len(igws) == 1
        assert igws[0]["id"] == "igw-123"

    def test_list_resources_nat_gateways(self, handler):
        """Test listing NAT gateways."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client

        mock_client.describe_vpcs.return_value = {"Vpcs": []}
        mock_client.describe_subnets.return_value = {"Subnets": []}
        mock_client.describe_internet_gateways.return_value = {"InternetGateways": []}
        mock_client.describe_nat_gateways.return_value = {
            "NatGateways": [{
                "NatGatewayId": "nat-123",
                "VpcId": "vpc-123",
                "State": "available",
                "Tags": []
            }]
        }
        mock_client.describe_route_tables.return_value = {"RouteTables": []}

        resources = handler.list_resources()

        nats = [r for r in resources if r["type"] == "nat_gateway"]
        assert len(nats) == 1
        assert nats[0]["id"] == "nat-123"

    def test_list_resources_handles_error(self, handler):
        """Test error handling during list."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client
        mock_client.describe_vpcs.side_effect = ClientError(
            {"Error": {"Code": "AccessDenied", "Message": "Access Denied"}},
            "DescribeVpcs"
        )

        resources = handler.list_resources()

        assert resources == []
        handler.logger.error.assert_called()

    def test_delete_vpc(self, handler):
        """Test deleting a VPC."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client

        resource = {"id": "vpc-123", "name": "my-vpc", "type": "vpc"}
        result = handler.delete_resource(resource)

        assert result is True
        mock_client.delete_vpc.assert_called_once_with(VpcId="vpc-123")

    def test_delete_subnet(self, handler):
        """Test deleting a subnet."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client

        resource = {"id": "subnet-123", "type": "subnet"}
        result = handler.delete_resource(resource)

        assert result is True
        mock_client.delete_subnet.assert_called_once_with(SubnetId="subnet-123")

    def test_delete_internet_gateway(self, handler):
        """Test deleting an internet gateway."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client

        resource = {"id": "igw-123", "type": "internet_gateway", "vpc_id": "vpc-123"}
        result = handler.delete_resource(resource)

        # Should detach first, then delete
        assert result is True
        mock_client.delete_internet_gateway.assert_called()

    def test_delete_nat_gateway(self, handler):
        """Test deleting a NAT gateway."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client

        resource = {"id": "nat-123", "type": "nat_gateway"}
        result = handler.delete_resource(resource)

        assert result is True
        mock_client.delete_nat_gateway.assert_called_once_with(NatGatewayId="nat-123")

    def test_is_default_resource_default_vpc(self, handler):
        """Test identifying default VPC."""
        resource = {"type": "vpc", "is_default": True}
        assert handler.is_default_resource(resource) is True

    def test_is_default_resource_custom_vpc(self, handler):
        """Test identifying custom VPC."""
        resource = {"type": "vpc", "is_default": False}
        assert handler.is_default_resource(resource) is False
