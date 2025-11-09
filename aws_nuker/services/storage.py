"""
Storage and File System Services - EFS, FSx, Storage Gateway, etc.
"""
import boto3
from typing import List, Dict, Any
from botocore.exceptions import ClientError
from .base import BaseService


class EFSFileSystemService(BaseService):
    """EFS File System cleanup"""
    
    def __init__(self, region: str, dry_run: bool = False):
        super().__init__(region, dry_run)
        self.client = boto3.client('efs', region_name=region)
    
    def get_service_name(self) -> str:
        return "EFS File Systems"
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List all EFS file systems"""
        resources = []
        try:
            paginator = self.client.get_paginator('describe_file_systems')
            for page in paginator.paginate():
                for fs in page.get('FileSystems', []):
                    resources.append({
                        'id': fs['FileSystemId'],
                        'name': fs.get('Name', 'N/A'),
                        'state': fs.get('LifeCycleState', 'N/A')
                    })
        except Exception as e:
            self.log_error("Error listing EFS file systems", e)
        return resources
    
    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete an EFS file system"""
        try:
            # Delete all mount targets first
            try:
                mts = self.client.describe_mount_targets(FileSystemId=resource['id'])
                for mt in mts.get('MountTargets', []):
                    try:
                        self.client.delete_mount_target(MountTargetId=mt['MountTargetId'])
                    except:
                        pass
            except:
                pass
            
            # Delete the file system
            self.client.delete_file_system(FileSystemId=resource['id'])
            return True
        except Exception as e:
            self.log_error(f"Error deleting EFS file system {resource['id']}", e)
            return False


class FSxFileSystemService(BaseService):
    """FSx File System cleanup"""
    
    def __init__(self, region: str, dry_run: bool = False):
        super().__init__(region, dry_run)
        self.client = boto3.client('fsx', region_name=region)
    
    def get_service_name(self) -> str:
        return "FSx File Systems"
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List all FSx file systems"""
        resources = []
        try:
            paginator = self.client.get_paginator('describe_file_systems')
            for page in paginator.paginate():
                for fs in page.get('FileSystems', []):
                    resources.append({
                        'id': fs['FileSystemId'],
                        'name': fs.get('FileSystemId', 'N/A'),
                        'type': fs.get('FileSystemType', 'N/A'),
                        'state': fs.get('Lifecycle', 'N/A')
                    })
        except Exception as e:
            self.log_error("Error listing FSx file systems", e)
        return resources
    
    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete an FSx file system"""
        try:
            self.client.delete_file_system(
                FileSystemId=resource['id']
            )
            return True
        except Exception as e:
            self.log_error(f"Error deleting FSx file system {resource['id']}", e)
            return False


class StorageGatewayService(BaseService):
    """Storage Gateway cleanup"""
    
    def __init__(self, region: str, dry_run: bool = False):
        super().__init__(region, dry_run)
        self.client = boto3.client('storagegateway', region_name=region)
    
    def get_service_name(self) -> str:
        return "Storage Gateways"
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List all Storage Gateways"""
        resources = []
        try:
            paginator = self.client.get_paginator('list_gateways')
            for page in paginator.paginate():
                for gateway in page.get('Gateways', []):
                    resources.append({
                        'id': gateway['GatewayARN'],
                        'name': gateway.get('GatewayName', 'N/A'),
                        'type': gateway.get('GatewayType', 'N/A')
                    })
        except Exception as e:
            self.log_error("Error listing Storage Gateways", e)
        return resources
    
    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a Storage Gateway"""
        try:
            self.client.delete_gateway(GatewayARN=resource['id'])
            return True
        except Exception as e:
            self.log_error(f"Error deleting Storage Gateway {resource['id']}", e)
            return False


class GlacierVaultService(BaseService):
    """S3 Glacier Vault cleanup"""
    
    def __init__(self, region: str, dry_run: bool = False):
        super().__init__(region, dry_run)
        self.client = boto3.client('glacier', region_name=region)
    
    def get_service_name(self) -> str:
        return "S3 Glacier Vaults"
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List all Glacier vaults"""
        resources = []
        try:
            paginator = self.client.get_paginator('list_vaults')
            for page in paginator.paginate():
                for vault in page.get('VaultList', []):
                    resources.append({
                        'id': vault['VaultName'],
                        'name': vault['VaultName']
                    })
        except Exception as e:
            self.log_error("Error listing Glacier vaults", e)
        return resources
    
    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a Glacier vault"""
        try:
            self.client.delete_vault(vaultName=resource['id'])
            return True
        except Exception as e:
            self.log_error(f"Error deleting Glacier vault {resource['id']}", e)
            return False
