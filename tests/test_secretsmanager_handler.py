"""Tests for SecretsManager Handler."""

import pytest
from unittest.mock import MagicMock, patch
from botocore.exceptions import ClientError

from aws_nuker.handlers.secretsmanager_handler import SecretsManagerHandler


class TestSecretsManagerHandler:
    """Tests for SecretsManagerHandler class."""

    @pytest.fixture
    def handler(self):
        """Create SecretsManagerHandler with mocked session."""
        with patch('aws_nuker.handlers.secretsmanager_handler.ResourceHandler.__init__'):
            handler = SecretsManagerHandler.__new__(SecretsManagerHandler)
            handler.region = "us-east-1"
            handler.dry_run = False
            handler.force = False
            handler.logger = MagicMock()
            handler.session = MagicMock()
        return handler

    def test_service_name(self, handler):
        """Test service_name property."""
        assert handler.service_name == "secretsmanager"

    def test_list_resources_secrets(self, handler):
        """Test listing secrets."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client

        mock_paginator = MagicMock()
        mock_paginator.paginate.return_value = [{
            "SecretList": [{
                "Name": "my-secret",
                "ARN": "arn:aws:secretsmanager:us-east-1:123456789012:secret:my-secret"
            }]
        }]
        mock_client.get_paginator.return_value = mock_paginator

        resources = handler.list_resources()

        assert len(resources) == 1
        assert resources[0]["name"] == "my-secret"
        assert resources[0]["type"] == "secret"

    def test_list_resources_handles_error(self, handler):
        """Test error handling during list."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client
        
        mock_paginator = MagicMock()
        mock_paginator.paginate.side_effect = ClientError(
            {"Error": {"Code": "AccessDenied", "Message": "Access Denied"}},
            "ListSecrets"
        )
        mock_client.get_paginator.return_value = mock_paginator

        resources = handler.list_resources()

        assert resources == []
        handler.logger.error.assert_called()

    def test_delete_secret(self, handler):
        """Test deleting a secret."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client

        resource = {
            "id": "arn:aws:secretsmanager:us-east-1:123456789012:secret:my-secret",
            "name": "my-secret",
            "type": "secret"
        }
        result = handler.delete_resource(resource)

        assert result is True
        mock_client.delete_secret.assert_called_once()

    def test_delete_secret_force_no_recovery(self, handler):
        """Test force deleting a secret without recovery window."""
        handler.force = True
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client

        resource = {
            "id": "arn:...",
            "name": "my-secret",
            "type": "secret"
        }
        result = handler.delete_resource(resource)

        assert result is True
        # Should be called with ForceDeleteWithoutRecovery when force=True
        call_args = mock_client.delete_secret.call_args
        # Check that the secret was deleted
        mock_client.delete_secret.assert_called_once()

    def test_delete_handles_error(self, handler):
        """Test error handling during deletion."""
        mock_client = MagicMock()
        handler.session.client.return_value = mock_client
        mock_client.delete_secret.side_effect = ClientError(
            {"Error": {"Code": "ResourceNotFoundException", "Message": "Not found"}},
            "DeleteSecret"
        )

        resource = {"id": "arn:...", "name": "my-secret", "type": "secret"}
        result = handler.delete_resource(resource)

        assert result is False
        handler.logger.error.assert_called()
