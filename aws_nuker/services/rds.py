"""
RDS Service - Cleanup RDS resources
"""
import boto3
from typing import List, Dict, Any
from botocore.exceptions import ClientError
from .base import BaseService


class RDSInstanceService(BaseService):
    """RDS Instance cleanup"""
    
    def __init__(self, region: str, dry_run: bool = False):
        super().__init__(region, dry_run)
        self.client = boto3.client('rds', region_name=region)
    
    def get_service_name(self) -> str:
        return "RDS Instances"
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List all RDS instances"""
        resources = []
        try:
            response = self.client.describe_db_instances()
            for instance in response.get('DBInstances', []):
                resources.append({
                    'id': instance['DBInstanceIdentifier'],
                    'name': instance['DBInstanceIdentifier'],
                    'status': instance.get('DBInstanceStatus', 'N/A'),
                    'engine': instance.get('Engine', 'N/A')
                })
        except Exception as e:
            self.log_error("Error listing RDS instances", e)
        return resources
    
    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete an RDS instance"""
        try:
            self.client.delete_db_instance(
                DBInstanceIdentifier=resource['id'],
                SkipFinalSnapshot=True,
                DeleteAutomatedBackups=True
            )
            return True
        except Exception as e:
            self.log_error(f"Error deleting RDS instance {resource['id']}", e)
            return False


class RDSClusterService(BaseService):
    """RDS Cluster cleanup"""
    
    def __init__(self, region: str, dry_run: bool = False):
        super().__init__(region, dry_run)
        self.client = boto3.client('rds', region_name=region)
    
    def get_service_name(self) -> str:
        return "RDS Clusters"
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List all RDS clusters"""
        resources = []
        try:
            response = self.client.describe_db_clusters()
            for cluster in response.get('DBClusters', []):
                resources.append({
                    'id': cluster['DBClusterIdentifier'],
                    'name': cluster['DBClusterIdentifier'],
                    'status': cluster.get('Status', 'N/A'),
                    'engine': cluster.get('Engine', 'N/A')
                })
        except Exception as e:
            self.log_error("Error listing RDS clusters", e)
        return resources
    
    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete an RDS cluster"""
        try:
            # Delete cluster instances first
            instances = self.client.describe_db_instances(
                Filters=[
                    {'Name': 'db-cluster-id', 'Values': [resource['id']]}
                ]
            )
            for instance in instances.get('DBInstances', []):
                try:
                    self.client.delete_db_instance(
                        DBInstanceIdentifier=instance['DBInstanceIdentifier'],
                        SkipFinalSnapshot=True
                    )
                except:
                    pass
            
            # Delete the cluster
            self.client.delete_db_cluster(
                DBClusterIdentifier=resource['id'],
                SkipFinalSnapshot=True
            )
            return True
        except Exception as e:
            self.log_error(f"Error deleting RDS cluster {resource['id']}", e)
            return False


class RDSSnapshotService(BaseService):
    """RDS Snapshot cleanup"""
    
    def __init__(self, region: str, dry_run: bool = False):
        super().__init__(region, dry_run)
        self.client = boto3.client('rds', region_name=region)
    
    def get_service_name(self) -> str:
        return "RDS Snapshots"
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List all RDS snapshots"""
        resources = []
        try:
            response = self.client.describe_db_snapshots()
            for snapshot in response.get('DBSnapshots', []):
                resources.append({
                    'id': snapshot['DBSnapshotIdentifier'],
                    'name': snapshot['DBSnapshotIdentifier'],
                    'status': snapshot.get('Status', 'N/A')
                })
        except Exception as e:
            self.log_error("Error listing RDS snapshots", e)
        return resources
    
    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete an RDS snapshot"""
        try:
            self.client.delete_db_snapshot(
                DBSnapshotIdentifier=resource['id']
            )
            return True
        except Exception as e:
            self.log_error(f"Error deleting RDS snapshot {resource['id']}", e)
            return False
