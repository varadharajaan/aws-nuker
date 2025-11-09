"""
EC2 Service - Cleanup EC2 resources
"""
import boto3
from typing import List, Dict, Any
from botocore.exceptions import ClientError
from .base import BaseService
from ..utils import is_default_resource, get_default_vpc_id
import time


class EC2Service(BaseService):
    """EC2 resource cleanup"""
    
    def __init__(self, region: str, dry_run: bool = False):
        super().__init__(region, dry_run)
        self.client = boto3.client('ec2', region_name=region)
        self.default_vpc_id = get_default_vpc_id(self.client)
    
    def get_service_name(self) -> str:
        return "EC2"
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List all EC2 instances"""
        resources = []
        try:
            response = self.client.describe_instances()
            for reservation in response.get('Reservations', []):
                for instance in reservation.get('Instances', []):
                    if instance['State']['Name'] not in ['terminated', 'terminating']:
                        name = 'N/A'
                        tags = instance.get('Tags', [])
                        for tag in tags:
                            if tag['Key'] == 'Name':
                                name = tag['Value']
                                break
                        resources.append({
                            'id': instance['InstanceId'],
                            'name': name,
                            'state': instance['State']['Name'],
                            'tags': tags
                        })
        except Exception as e:
            self.log_error("Error listing EC2 instances", e)
        return resources
    
    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Terminate an EC2 instance"""
        try:
            # Disable termination protection if enabled
            try:
                self.client.modify_instance_attribute(
                    InstanceId=resource['id'],
                    DisableApiTermination={'Value': False}
                )
            except:
                pass
            
            self.client.terminate_instances(InstanceIds=[resource['id']])
            return True
        except Exception as e:
            self.log_error(f"Error terminating instance {resource['id']}", e)
            return False


class EBSService(BaseService):
    """EBS Volume cleanup"""
    
    def __init__(self, region: str, dry_run: bool = False):
        super().__init__(region, dry_run)
        self.client = boto3.client('ec2', region_name=region)
    
    def get_service_name(self) -> str:
        return "EBS Volumes"
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List all EBS volumes"""
        resources = []
        try:
            response = self.client.describe_volumes()
            for volume in response.get('Volumes', []):
                name = 'N/A'
                for tag in volume.get('Tags', []):
                    if tag['Key'] == 'Name':
                        name = tag['Value']
                        break
                resources.append({
                    'id': volume['VolumeId'],
                    'name': name,
                    'state': volume['State'],
                    'size': volume['Size']
                })
        except Exception as e:
            self.log_error("Error listing EBS volumes", e)
        return resources
    
    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete an EBS volume"""
        try:
            # Force detach if attached
            if resource['state'] == 'in-use':
                try:
                    self.client.detach_volume(VolumeId=resource['id'], Force=True)
                    time.sleep(2)  # Wait for detachment
                except:
                    pass
            
            self.client.delete_volume(VolumeId=resource['id'])
            return True
        except Exception as e:
            self.log_error(f"Error deleting volume {resource['id']}", e)
            return False


class EBSSnapshotService(BaseService):
    """EBS Snapshot cleanup"""
    
    def __init__(self, region: str, dry_run: bool = False):
        super().__init__(region, dry_run)
        self.client = boto3.client('ec2', region_name=region)
    
    def get_service_name(self) -> str:
        return "EBS Snapshots"
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List all EBS snapshots owned by the account"""
        resources = []
        try:
            response = self.client.describe_snapshots(OwnerIds=['self'])
            for snapshot in response.get('Snapshots', []):
                name = 'N/A'
                for tag in snapshot.get('Tags', []):
                    if tag['Key'] == 'Name':
                        name = tag['Value']
                        break
                resources.append({
                    'id': snapshot['SnapshotId'],
                    'name': name,
                    'description': snapshot.get('Description', 'N/A')
                })
        except Exception as e:
            self.log_error("Error listing EBS snapshots", e)
        return resources
    
    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete an EBS snapshot"""
        try:
            self.client.delete_snapshot(SnapshotId=resource['id'])
            return True
        except Exception as e:
            self.log_error(f"Error deleting snapshot {resource['id']}", e)
            return False


class AMIService(BaseService):
    """AMI cleanup"""
    
    def __init__(self, region: str, dry_run: bool = False):
        super().__init__(region, dry_run)
        self.client = boto3.client('ec2', region_name=region)
    
    def get_service_name(self) -> str:
        return "AMIs"
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List all AMIs owned by the account"""
        resources = []
        try:
            response = self.client.describe_images(Owners=['self'])
            for image in response.get('Images', []):
                resources.append({
                    'id': image['ImageId'],
                    'name': image.get('Name', 'N/A'),
                    'description': image.get('Description', 'N/A')
                })
        except Exception as e:
            self.log_error("Error listing AMIs", e)
        return resources
    
    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Deregister an AMI"""
        try:
            self.client.deregister_image(ImageId=resource['id'])
            return True
        except Exception as e:
            self.log_error(f"Error deregistering AMI {resource['id']}", e)
            return False


class ElasticIPService(BaseService):
    """Elastic IP cleanup"""
    
    def __init__(self, region: str, dry_run: bool = False):
        super().__init__(region, dry_run)
        self.client = boto3.client('ec2', region_name=region)
    
    def get_service_name(self) -> str:
        return "Elastic IPs"
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List all Elastic IPs"""
        resources = []
        try:
            response = self.client.describe_addresses()
            for address in response.get('Addresses', []):
                resources.append({
                    'id': address.get('AllocationId', address.get('PublicIp')),
                    'name': address.get('PublicIp', 'N/A'),
                    'allocation_id': address.get('AllocationId')
                })
        except Exception as e:
            self.log_error("Error listing Elastic IPs", e)
        return resources
    
    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Release an Elastic IP"""
        try:
            if resource.get('allocation_id'):
                self.client.release_address(AllocationId=resource['allocation_id'])
            else:
                self.client.release_address(PublicIp=resource['name'])
            return True
        except Exception as e:
            self.log_error(f"Error releasing Elastic IP {resource['id']}", e)
            return False


class KeyPairService(BaseService):
    """Key Pair cleanup"""
    
    def __init__(self, region: str, dry_run: bool = False):
        super().__init__(region, dry_run)
        self.client = boto3.client('ec2', region_name=region)
    
    def get_service_name(self) -> str:
        return "Key Pairs"
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List all Key Pairs"""
        resources = []
        try:
            response = self.client.describe_key_pairs()
            for key_pair in response.get('KeyPairs', []):
                resources.append({
                    'id': key_pair['KeyPairId'],
                    'name': key_pair['KeyName']
                })
        except Exception as e:
            self.log_error("Error listing Key Pairs", e)
        return resources
    
    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a Key Pair"""
        try:
            self.client.delete_key_pair(KeyPairId=resource['id'])
            return True
        except Exception as e:
            self.log_error(f"Error deleting Key Pair {resource['id']}", e)
            return False
