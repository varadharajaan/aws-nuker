"""Tests for API Gateway Handler."""

import pytest
from unittest.mock import MagicMock, patch
from botocore.exceptions import ClientError

from aws_nuker.handlers.apigateway_handler import APIGatewayHandler


class TestAPIGatewayHandler:
    """Tests for APIGatewayHandler class."""

    @pytest.fixture
    def handler(self):
        """Create APIGatewayHandler with mocked session."""
        with patch('aws_nuker.handlers.apigateway_handler.ResourceHandler.__init__'):
            handler = APIGatewayHandler.__new__(APIGatewayHandler)
            handler.region = "us-east-1"
            handler.dry_run = False
            handler.force = False
            handler.logger = MagicMock()
            handler.session = MagicMock()
        return handler

    def test_service_name(self, handler):
        """Test service_name property."""
        assert handler.service_name == "apigateway"

    def test_list_resources_rest_apis(self, handler):
        """Test listing REST APIs."""
        mock_apigw = MagicMock()
        mock_apigwv2 = MagicMock()
        
        def client_factory(service, **kwargs):
            if service == "apigateway":
                return mock_apigw
            elif service == "apigatewayv2":
                return mock_apigwv2
            return MagicMock()
        
        handler.session.client.side_effect = client_factory

        mock_apigw.get_rest_apis.return_value = {
            "items": [{
                "id": "api123",
                "name": "my-rest-api",
                "description": "Test API"
            }]
        }
        mock_apigwv2.get_apis.return_value = {"Items": []}

        resources = handler.list_resources()

        rest_apis = [r for r in resources if r["type"] == "rest_api"]
        assert len(rest_apis) == 1
        assert rest_apis[0]["name"] == "my-rest-api"

    def test_list_resources_handles_error(self, handler):
        """Test error handling during list."""
        mock_apigw = MagicMock()
        mock_apigwv2 = MagicMock()
        
        def client_factory(service, **kwargs):
            if service == "apigateway":
                return mock_apigw
            elif service == "apigatewayv2":
                return mock_apigwv2
            return MagicMock()
        
        handler.session.client.side_effect = client_factory
        mock_apigw.get_rest_apis.side_effect = ClientError(
            {"Error": {"Code": "AccessDenied", "Message": "Access Denied"}},
            "GetRestApis"
        )

        resources = handler.list_resources()

        assert resources == []
        handler.logger.error.assert_called()

    def test_delete_rest_api(self, handler):
        """Test deleting a REST API."""
        mock_apigw = MagicMock()
        handler.session.client.return_value = mock_apigw

        resource = {"id": "api123", "name": "my-rest-api", "type": "rest_api"}
        result = handler.delete_resource(resource)

        assert result is True
        mock_apigw.delete_rest_api.assert_called_once_with(restApiId="api123")

    def test_delete_handles_error(self, handler):
        """Test error handling during deletion."""
        mock_apigw = MagicMock()
        handler.session.client.return_value = mock_apigw
        mock_apigw.delete_rest_api.side_effect = ClientError(
            {"Error": {"Code": "NotFoundException", "Message": "Not found"}},
            "DeleteRestApi"
        )

        resource = {"id": "api123", "name": "my-rest-api", "type": "rest_api"}
        result = handler.delete_resource(resource)

        assert result is False
        handler.logger.error.assert_called()
