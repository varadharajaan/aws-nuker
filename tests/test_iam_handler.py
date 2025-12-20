"""Tests for IAM Handler."""

import pytest
from unittest.mock import MagicMock, patch
from botocore.exceptions import ClientError

from aws_nuker.handlers.iam_handler import IAMHandler


class TestIAMHandler:
    """Tests for IAMHandler class."""

    @pytest.fixture
    def handler(self):
        """Create IAMHandler with mocked session."""
        with patch('aws_nuker.handlers.iam_handler.ResourceHandler.__init__'):
            handler = IAMHandler.__new__(IAMHandler)
            handler.region = "us-east-1"
            handler.dry_run = False
            handler.force = False
            handler.logger = MagicMock()
            handler.session = MagicMock()
        return handler

    def test_service_name(self, handler):
        """Test service_name property."""
        assert handler.service_name == "iam"

    def test_list_resources_users(self, handler):
        """Test listing IAM users."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client

        mock_paginator = MagicMock()
        mock_paginator.paginate.return_value = [{
            "Users": [{
                "UserName": "test-user",
                "Arn": "arn:aws:iam::123456789012:user/test-user"
            }]
        }]
        mock_client.get_paginator.return_value = mock_paginator
        mock_client.list_roles.return_value = {"Roles": []}
        mock_client.list_policies.return_value = {"Policies": []}

        resources = handler.list_resources()

        users = [r for r in resources if r["type"] == "user"]
        assert len(users) == 1
        assert users[0]["name"] == "test-user"

    def test_list_resources_roles(self, handler):
        """Test listing IAM roles (excluding service-linked)."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client

        # Mock users paginator
        mock_users_paginator = MagicMock()
        mock_users_paginator.paginate.return_value = [{"Users": []}]
        
        # Mock roles paginator
        mock_roles_paginator = MagicMock()
        mock_roles_paginator.paginate.return_value = [{
            "Roles": [
                {"RoleName": "my-role", "Path": "/", "Arn": "arn:aws:iam::..."},
                {"RoleName": "AWSServiceRoleForAutoScaling", "Path": "/aws-service-role/", "Arn": "arn:aws:iam::..."},
            ]
        }]
        
        # Mock policies paginator
        mock_policies_paginator = MagicMock()
        mock_policies_paginator.paginate.return_value = [{"Policies": []}]
        
        mock_client.get_paginator.side_effect = [
            mock_users_paginator, mock_roles_paginator, mock_policies_paginator
        ]

        resources = handler.list_resources()

        roles = [r for r in resources if r["type"] == "role"]
        # Should only include non-service-linked role
        assert len(roles) == 1
        assert roles[0]["name"] == "my-role"

    def test_list_resources_policies(self, handler):
        """Test listing customer-managed IAM policies."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client

        # Mock users paginator
        mock_users_paginator = MagicMock()
        mock_users_paginator.paginate.return_value = [{"Users": []}]
        
        # Mock roles paginator
        mock_roles_paginator = MagicMock()
        mock_roles_paginator.paginate.return_value = [{"Roles": []}]
        
        # Mock policies paginator
        mock_policies_paginator = MagicMock()
        mock_policies_paginator.paginate.return_value = [{
            "Policies": [{
                "PolicyName": "my-policy",
                "Arn": "arn:aws:iam::123456789012:policy/my-policy"
            }]
        }]
        
        mock_client.get_paginator.side_effect = [
            mock_users_paginator, mock_roles_paginator, mock_policies_paginator
        ]

        resources = handler.list_resources()

        policies = [r for r in resources if r["type"] == "policy"]
        assert len(policies) == 1
        assert policies[0]["name"] == "my-policy"

    def test_list_resources_handles_error(self, handler):
        """Test error handling during list."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client
        
        mock_paginator = MagicMock()
        mock_paginator.paginate.side_effect = ClientError(
            {"Error": {"Code": "AccessDenied", "Message": "Access Denied"}},
            "ListUsers"
        )
        mock_client.get_paginator.return_value = mock_paginator

        resources = handler.list_resources()

        assert resources == []
        handler.logger.error.assert_called()

    def test_delete_user(self, handler):
        """Test deleting an IAM user."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client
        
        # Mock user cleanup methods
        mock_client.list_attached_user_policies.return_value = {"AttachedPolicies": []}
        mock_client.list_user_policies.return_value = {"PolicyNames": []}
        mock_client.list_access_keys.return_value = {"AccessKeyMetadata": []}
        mock_client.list_mfa_devices.return_value = {"MFADevices": []}
        mock_client.list_groups_for_user.return_value = {"Groups": []}

        resource = {"id": "test-user", "name": "test-user", "type": "user"}
        result = handler.delete_resource(resource)

        assert result is True
        mock_client.delete_user.assert_called_once_with(UserName="test-user")

    def test_delete_role(self, handler):
        """Test deleting an IAM role."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client
        
        # Mock role cleanup methods
        mock_client.list_attached_role_policies.return_value = {"AttachedPolicies": []}
        mock_client.list_role_policies.return_value = {"PolicyNames": []}
        mock_client.list_instance_profiles_for_role.return_value = {"InstanceProfiles": []}

        resource = {"id": "my-role", "name": "my-role", "type": "role"}
        result = handler.delete_resource(resource)

        assert result is True
        mock_client.delete_role.assert_called_once_with(RoleName="my-role")

    def test_delete_policy(self, handler):
        """Test deleting an IAM policy."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client
        
        mock_client.list_policy_versions.return_value = {
            "Versions": [{"VersionId": "v1", "IsDefaultVersion": True}]
        }

        resource = {
            "id": "arn:aws:iam::123456789012:policy/my-policy",
            "name": "my-policy",
            "type": "policy"
        }
        result = handler.delete_resource(resource)

        assert result is True
        mock_client.delete_policy.assert_called_once()

    def test_delete_unknown_type(self, handler):
        """Test deleting an unknown resource type."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client

        resource = {"id": "unknown", "name": "unknown", "type": "unknown_type"}
        result = handler.delete_resource(resource)

        assert result is False

    def test_delete_handles_error(self, handler):
        """Test error handling during deletion."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client
        mock_client.list_attached_user_policies.return_value = {"AttachedPolicies": []}
        mock_client.list_user_policies.return_value = {"PolicyNames": []}
        mock_client.list_access_keys.return_value = {"AccessKeyMetadata": []}
        mock_client.list_mfa_devices.return_value = {"MFADevices": []}
        mock_client.list_groups_for_user.return_value = {"Groups": []}
        mock_client.delete_user.side_effect = ClientError(
            {"Error": {"Code": "NoSuchEntity", "Message": "Not found"}},
            "DeleteUser"
        )

        resource = {"id": "test-user", "name": "test-user", "type": "user"}
        result = handler.delete_resource(resource)

        assert result is False
        handler.logger.error.assert_called()

    def test_is_default_resource_aws_path(self, handler):
        """Test identifying AWS-managed resources.
        
        Note: The IAM handler doesn't have is_default_resource implemented,
        so this test just verifies the base behavior.
        """
        # The base handler returns False for all resources
        resource = {"type": "role", "path": "/aws-service-role/"}
        # Service-linked roles are filtered out in list_resources, not is_default_resource
        assert handler.is_default_resource(resource) is False

    def test_is_default_resource_customer(self, handler):
        """Test identifying customer resources."""
        resource = {"type": "role", "path": "/"}
        assert handler.is_default_resource(resource) is False
