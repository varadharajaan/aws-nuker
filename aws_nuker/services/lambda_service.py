"""
Lambda Service - Cleanup Lambda functions
"""
import boto3
from typing import List, Dict, Any
from botocore.exceptions import ClientError
from .base import BaseService


class LambdaService(BaseService):
    """Lambda function cleanup"""
    
    def __init__(self, region: str, dry_run: bool = False):
        super().__init__(region, dry_run)
        self.client = boto3.client('lambda', region_name=region)
    
    def get_service_name(self) -> str:
        return "Lambda Functions"
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List all Lambda functions"""
        resources = []
        try:
            paginator = self.client.get_paginator('list_functions')
            for page in paginator.paginate():
                for function in page.get('Functions', []):
                    resources.append({
                        'id': function['FunctionName'],
                        'name': function['FunctionName'],
                        'runtime': function.get('Runtime', 'N/A'),
                        'arn': function.get('FunctionArn', 'N/A')
                    })
        except Exception as e:
            self.log_error("Error listing Lambda functions", e)
        return resources
    
    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a Lambda function"""
        try:
            self.client.delete_function(
                FunctionName=resource['id']
            )
            return True
        except Exception as e:
            self.log_error(f"Error deleting Lambda function {resource['id']}", e)
            return False


class LambdaLayerService(BaseService):
    """Lambda Layer cleanup"""
    
    def __init__(self, region: str, dry_run: bool = False):
        super().__init__(region, dry_run)
        self.client = boto3.client('lambda', region_name=region)
    
    def get_service_name(self) -> str:
        return "Lambda Layers"
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List all Lambda layers"""
        resources = []
        try:
            paginator = self.client.get_paginator('list_layers')
            for page in paginator.paginate():
                for layer in page.get('Layers', []):
                    # Get all versions of the layer
                    layer_name = layer['LayerName']
                    versions = self.client.list_layer_versions(LayerName=layer_name)
                    for version in versions.get('LayerVersions', []):
                        resources.append({
                            'id': f"{layer_name}:{version['Version']}",
                            'name': layer_name,
                            'version': version['Version']
                        })
        except Exception as e:
            self.log_error("Error listing Lambda layers", e)
        return resources
    
    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a Lambda layer version"""
        try:
            self.client.delete_layer_version(
                LayerName=resource['name'],
                VersionNumber=resource['version']
            )
            return True
        except Exception as e:
            self.log_error(f"Error deleting Lambda layer {resource['id']}", e)
            return False
