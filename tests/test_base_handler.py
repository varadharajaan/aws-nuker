"""Tests for Base Handler class."""

import pytest
from unittest.mock import MagicMock, patch
from botocore.exceptions import ClientError

from aws_nuker.base_handler import ResourceHandler


class ConcreteHandler(ResourceHandler):
    """Concrete implementation of ResourceHandler for testing."""

    @property
    def service_name(self) -> str:
        return "test_service"

    def list_resources(self):
        return [
            {"id": "resource-1", "name": "Resource 1"},
            {"id": "resource-2", "name": "Resource 2"},
        ]

    def delete_resource(self, resource):
        return True


class FailingHandler(ResourceHandler):
    """Handler that fails on every delete."""

    @property
    def service_name(self) -> str:
        return "failing_service"

    def list_resources(self):
        return [{"id": "fail-resource", "name": "Failing Resource"}]

    def delete_resource(self, resource):
        return False


class TestResourceHandler:
    """Tests for ResourceHandler base class."""

    @pytest.fixture
    def handler(self):
        """Create ConcreteHandler with mocked logger."""
        with patch('aws_nuker.base_handler.boto3.Session'):
            with patch('aws_nuker.base_handler.get_logger') as mock_logger:
                mock_logger.return_value = MagicMock()
                handler = ConcreteHandler("us-east-1", dry_run=False, force=False)
        return handler

    @pytest.fixture
    def dry_run_handler(self):
        """Create handler in dry-run mode."""
        with patch('aws_nuker.base_handler.boto3.Session'):
            with patch('aws_nuker.base_handler.get_logger') as mock_logger:
                mock_logger.return_value = MagicMock()
                handler = ConcreteHandler("us-east-1", dry_run=True, force=False)
        return handler

    def test_init(self, handler):
        """Test handler initialization."""
        assert handler.region == "us-east-1"
        assert handler.dry_run is False
        assert handler.force is False
        assert handler.logger is not None
        assert handler.session is not None

    def test_service_name(self, handler):
        """Test service_name property."""
        assert handler.service_name == "test_service"

    def test_is_default_resource(self, handler):
        """Test default is_default_resource implementation."""
        resource = {"id": "any-resource"}
        assert handler.is_default_resource(resource) is False

    def test_nuke_all(self, handler):
        """Test nuke_all method."""
        stats = handler.nuke_all()

        assert stats["service"] == "test_service"
        assert stats["region"] == "us-east-1"
        assert stats["total"] == 2
        assert stats["deleted"] == 2
        assert stats["failed"] == 0
        assert stats["skipped"] == 0
        assert "elapsed_time" in stats

    def test_nuke_all_dry_run(self, dry_run_handler):
        """Test nuke_all in dry-run mode."""
        stats = dry_run_handler.nuke_all()

        assert stats["total"] == 2
        assert stats["deleted"] == 2  # Still counted as "deleted" in dry-run
        assert stats["failed"] == 0

    def test_nuke_all_with_failures(self):
        """Test nuke_all with deletion failures."""
        with patch('aws_nuker.base_handler.boto3.Session'):
            with patch('aws_nuker.base_handler.get_logger') as mock_logger:
                mock_logger.return_value = MagicMock()
                handler = FailingHandler("us-east-1", dry_run=False, force=False)

        stats = handler.nuke_all()

        assert stats["total"] == 1
        assert stats["deleted"] == 0
        assert stats["failed"] == 1


class TestDeleteWithRetry:
    """Tests for _delete_with_retry method."""

    @pytest.fixture
    def handler(self):
        """Create ConcreteHandler."""
        with patch('aws_nuker.base_handler.boto3.Session'):
            with patch('aws_nuker.base_handler.get_logger') as mock_logger:
                mock_logger.return_value = MagicMock()
                handler = ConcreteHandler("us-east-1", dry_run=False, force=False)
        return handler

    def test_delete_with_retry_success(self, handler):
        """Test successful delete with retry."""
        resource = {"id": "resource-1", "name": "Resource 1"}
        result = handler._delete_with_retry(resource)

        assert result is True

    def test_delete_with_retry_dependency_violation_no_force(self, handler):
        """Test dependency violation without force."""
        with patch.object(handler, 'delete_resource') as mock_delete:
            mock_delete.side_effect = ClientError(
                {"Error": {"Code": "DependencyViolation", "Message": "Has dependencies"}},
                "DeleteResource"
            )

            resource = {"id": "resource-1"}
            result = handler._delete_with_retry(resource, max_retries=1)

            assert result is False

    def test_delete_with_retry_dependency_violation_with_force(self, handler):
        """Test dependency violation with force enabled."""
        handler.force = True
        call_count = 0

        def side_effect(resource):
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ClientError(
                    {"Error": {"Code": "DependencyViolation", "Message": "Has deps"}},
                    "DeleteResource"
                )
            return True

        with patch.object(handler, 'delete_resource', side_effect=side_effect):
            with patch('time.sleep'):  # Don't actually sleep in tests
                resource = {"id": "resource-1"}
                result = handler._delete_with_retry(resource, max_retries=3)

                assert result is True
                assert call_count == 2

    def test_delete_with_retry_unexpected_error(self, handler):
        """Test unexpected error during delete."""
        with patch.object(handler, 'delete_resource') as mock_delete:
            mock_delete.side_effect = Exception("Unexpected error")

            resource = {"id": "resource-1"}
            result = handler._delete_with_retry(resource)

            assert result is False


class TestSkipDefaultResources:
    """Tests for skipping default resources."""

    def test_skip_default_resource(self):
        """Test that default resources are skipped."""

        class HandlerWithDefaults(ResourceHandler):
            @property
            def service_name(self):
                return "test"

            def list_resources(self):
                return [
                    {"id": "default-1", "name": "Default", "is_default": True},
                    {"id": "custom-1", "name": "Custom", "is_default": False},
                ]

            def delete_resource(self, resource):
                return True

            def is_default_resource(self, resource):
                return resource.get("is_default", False)

        with patch('aws_nuker.base_handler.boto3.Session'):
            with patch('aws_nuker.base_handler.get_logger') as mock_logger:
                mock_logger.return_value = MagicMock()
                handler = HandlerWithDefaults("us-east-1", dry_run=False, force=False)

        stats = handler.nuke_all()

        assert stats["total"] == 2
        assert stats["deleted"] == 1  # Only custom resource deleted
        assert stats["skipped"] == 1  # Default resource skipped

    def test_force_delete_default_resource(self):
        """Test that default resources are deleted when force=True."""

        class HandlerWithDefaults(ResourceHandler):
            @property
            def service_name(self):
                return "test"

            def list_resources(self):
                return [{"id": "default-1", "is_default": True}]

            def delete_resource(self, resource):
                return True

            def is_default_resource(self, resource):
                return resource.get("is_default", False)

        with patch('aws_nuker.base_handler.boto3.Session'):
            with patch('aws_nuker.base_handler.get_logger') as mock_logger:
                mock_logger.return_value = MagicMock()
                # force=True
                handler = HandlerWithDefaults("us-east-1", dry_run=False, force=True)

        stats = handler.nuke_all()

        assert stats["deleted"] == 1
        assert stats["skipped"] == 0
