"""
S3 Service - Cleanup S3 buckets
"""
import boto3
from typing import List, Dict, Any
from botocore.exceptions import ClientError
from .base import BaseService


class S3Service(BaseService):
    """S3 bucket cleanup with force empty"""
    
    def __init__(self, region: str, dry_run: bool = False):
        super().__init__(region, dry_run)
        self.client = boto3.client('s3', region_name=region)
        self.resource = boto3.resource('s3', region_name=region)
    
    def get_service_name(self) -> str:
        return "S3 Buckets"
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List all S3 buckets in the account"""
        resources = []
        try:
            response = self.client.list_buckets()
            for bucket in response.get('Buckets', []):
                # Check if bucket is in this region
                try:
                    bucket_region = self.client.get_bucket_location(
                        Bucket=bucket['Name']
                    ).get('LocationConstraint', 'us-east-1')
                    # LocationConstraint is None for us-east-1
                    if bucket_region is None:
                        bucket_region = 'us-east-1'
                    
                    if bucket_region == self.region:
                        resources.append({
                            'id': bucket['Name'],
                            'name': bucket['Name'],
                            'created': bucket.get('CreationDate', 'N/A')
                        })
                except:
                    # If we can't get location, skip it
                    pass
        except Exception as e:
            self.log_error("Error listing S3 buckets", e)
        return resources
    
    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete an S3 bucket forcefully (empty first)"""
        try:
            bucket_name = resource['id']
            bucket = self.resource.Bucket(bucket_name)
            
            # Delete all versions and delete markers
            try:
                bucket.object_versions.delete()
            except:
                pass
            
            # Delete all objects
            try:
                bucket.objects.all().delete()
            except:
                pass
            
            # Delete the bucket
            bucket.delete()
            return True
        except Exception as e:
            self.log_error(f"Error deleting S3 bucket {resource['id']}", e)
            return False
