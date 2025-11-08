"""
CloudFormation Service - Cleanup CloudFormation stacks
"""
import boto3
from typing import List, Dict, Any
from botocore.exceptions import ClientError
from .base import BaseService
import time


class CloudFormationService(BaseService):
    """CloudFormation Stack cleanup"""
    
    def __init__(self, region: str, dry_run: bool = False):
        super().__init__(region, dry_run)
        self.client = boto3.client('cloudformation', region_name=region)
    
    def get_service_name(self) -> str:
        return "CloudFormation Stacks"
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List all CloudFormation stacks"""
        resources = []
        try:
            paginator = self.client.get_paginator('list_stacks')
            for page in paginator.paginate(
                StackStatusFilter=[
                    'CREATE_COMPLETE', 'UPDATE_COMPLETE', 'UPDATE_ROLLBACK_COMPLETE',
                    'ROLLBACK_COMPLETE', 'IMPORT_COMPLETE', 'IMPORT_ROLLBACK_COMPLETE'
                ]
            ):
                for stack in page.get('StackSummaries', []):
                    resources.append({
                        'id': stack['StackName'],
                        'name': stack['StackName'],
                        'status': stack.get('StackStatus', 'N/A')
                    })
        except Exception as e:
            self.log_error("Error listing CloudFormation stacks", e)
        return resources
    
    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a CloudFormation stack"""
        try:
            # Delete with retain resources option disabled (force delete)
            self.client.delete_stack(
                StackName=resource['id']
            )
            return True
        except Exception as e:
            self.log_error(f"Error deleting CloudFormation stack {resource['id']}", e)
            return False
