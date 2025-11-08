"""
VPC Service - Cleanup VPC resources
"""
import boto3
from typing import List, Dict, Any
from botocore.exceptions import ClientError
from .base import BaseService
from ..utils import is_default_resource, get_default_vpc_id
import time


class VPCService(BaseService):
    """VPC cleanup (excludes default VPCs)"""
    
    def __init__(self, region: str, dry_run: bool = False):
        super().__init__(region, dry_run)
        self.client = boto3.client('ec2', region_name=region)
        self.default_vpc_id = get_default_vpc_id(self.client)
    
    def get_service_name(self) -> str:
        return "VPCs"
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List all non-default VPCs"""
        resources = []
        try:
            response = self.client.describe_vpcs()
            for vpc in response.get('Vpcs', []):
                # Skip default VPC
                if vpc.get('IsDefault', False):
                    continue
                
                name = 'N/A'
                for tag in vpc.get('Tags', []):
                    if tag['Key'] == 'Name':
                        name = tag['Value']
                        break
                
                resources.append({
                    'id': vpc['VpcId'],
                    'name': name,
                    'cidr': vpc.get('CidrBlock', 'N/A')
                })
        except Exception as e:
            self.log_error("Error listing VPCs", e)
        return resources
    
    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a VPC and all its dependencies"""
        try:
            vpc_id = resource['id']
            
            # Delete dependencies first
            self._delete_vpc_dependencies(vpc_id)
            
            # Delete the VPC
            self.client.delete_vpc(VpcId=vpc_id)
            return True
        except Exception as e:
            self.log_error(f"Error deleting VPC {resource['id']}", e)
            return False
    
    def _delete_vpc_dependencies(self, vpc_id: str):
        """Delete all VPC dependencies forcefully"""
        try:
            # Delete NAT Gateways
            nat_gws = self.client.describe_nat_gateways(
                Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}]
            )
            for nat_gw in nat_gws.get('NatGateways', []):
                if nat_gw['State'] not in ['deleted', 'deleting']:
                    try:
                        self.client.delete_nat_gateway(NatGatewayId=nat_gw['NatGatewayId'])
                    except:
                        pass
            
            # Wait for NAT Gateways to delete
            time.sleep(5)
            
            # Delete Internet Gateways
            igws = self.client.describe_internet_gateways(
                Filters=[{'Name': 'attachment.vpc-id', 'Values': [vpc_id]}]
            )
            for igw in igws.get('InternetGateways', []):
                try:
                    self.client.detach_internet_gateway(
                        InternetGatewayId=igw['InternetGatewayId'],
                        VpcId=vpc_id
                    )
                    self.client.delete_internet_gateway(
                        InternetGatewayId=igw['InternetGatewayId']
                    )
                except:
                    pass
            
            # Delete Subnets
            subnets = self.client.describe_subnets(
                Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}]
            )
            for subnet in subnets.get('Subnets', []):
                try:
                    self.client.delete_subnet(SubnetId=subnet['SubnetId'])
                except:
                    pass
            
            # Delete Route Tables (except main)
            route_tables = self.client.describe_route_tables(
                Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}]
            )
            for rt in route_tables.get('RouteTables', []):
                # Skip main route table
                is_main = False
                for assoc in rt.get('Associations', []):
                    if assoc.get('Main', False):
                        is_main = True
                        break
                if not is_main:
                    try:
                        self.client.delete_route_table(RouteTableId=rt['RouteTableId'])
                    except:
                        pass
            
            # Delete Network ACLs (except default)
            nacls = self.client.describe_network_acls(
                Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}]
            )
            for nacl in nacls.get('NetworkAcls', []):
                if not nacl.get('IsDefault', False):
                    try:
                        self.client.delete_network_acl(NetworkAclId=nacl['NetworkAclId'])
                    except:
                        pass
            
            # Delete Security Groups (except default)
            sgs = self.client.describe_security_groups(
                Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}]
            )
            for sg in sgs.get('SecurityGroups', []):
                if sg['GroupName'] != 'default':
                    try:
                        # Remove all ingress/egress rules first
                        if sg.get('IpPermissions'):
                            self.client.revoke_security_group_ingress(
                                GroupId=sg['GroupId'],
                                IpPermissions=sg['IpPermissions']
                            )
                        if sg.get('IpPermissionsEgress'):
                            self.client.revoke_security_group_egress(
                                GroupId=sg['GroupId'],
                                IpPermissions=sg['IpPermissionsEgress']
                            )
                        self.client.delete_security_group(GroupId=sg['GroupId'])
                    except:
                        pass
            
            # Delete VPC Endpoints
            endpoints = self.client.describe_vpc_endpoints(
                Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}]
            )
            endpoint_ids = [ep['VpcEndpointId'] for ep in endpoints.get('VpcEndpoints', [])]
            if endpoint_ids:
                try:
                    self.client.delete_vpc_endpoints(VpcEndpointIds=endpoint_ids)
                except:
                    pass
            
        except Exception as e:
            self.log_error(f"Error deleting VPC dependencies for {vpc_id}", e)


class SecurityGroupService(BaseService):
    """Security Group cleanup (excludes default)"""
    
    def __init__(self, region: str, dry_run: bool = False):
        super().__init__(region, dry_run)
        self.client = boto3.client('ec2', region_name=region)
        self.default_vpc_id = get_default_vpc_id(self.client)
    
    def get_service_name(self) -> str:
        return "Security Groups"
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List all non-default security groups"""
        resources = []
        try:
            response = self.client.describe_security_groups()
            for sg in response.get('SecurityGroups', []):
                # Skip default security groups
                if sg['GroupName'] == 'default':
                    continue
                # Skip security groups in default VPC
                if sg.get('VpcId') == self.default_vpc_id:
                    continue
                
                resources.append({
                    'id': sg['GroupId'],
                    'name': sg['GroupName'],
                    'vpc_id': sg.get('VpcId', 'N/A')
                })
        except Exception as e:
            self.log_error("Error listing Security Groups", e)
        return resources
    
    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a security group"""
        try:
            # First, revoke all ingress and egress rules
            sg = self.client.describe_security_groups(GroupIds=[resource['id']])['SecurityGroups'][0]
            
            if sg.get('IpPermissions'):
                self.client.revoke_security_group_ingress(
                    GroupId=resource['id'],
                    IpPermissions=sg['IpPermissions']
                )
            
            if sg.get('IpPermissionsEgress'):
                self.client.revoke_security_group_egress(
                    GroupId=resource['id'],
                    IpPermissions=sg['IpPermissionsEgress']
                )
            
            # Delete the security group
            self.client.delete_security_group(GroupId=resource['id'])
            return True
        except Exception as e:
            self.log_error(f"Error deleting Security Group {resource['id']}", e)
            return False


class SubnetService(BaseService):
    """Subnet cleanup (excludes default VPC subnets)"""
    
    def __init__(self, region: str, dry_run: bool = False):
        super().__init__(region, dry_run)
        self.client = boto3.client('ec2', region_name=region)
        self.default_vpc_id = get_default_vpc_id(self.client)
    
    def get_service_name(self) -> str:
        return "Subnets"
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List all subnets not in default VPC"""
        resources = []
        try:
            response = self.client.describe_subnets()
            for subnet in response.get('Subnets', []):
                # Skip subnets in default VPC
                if subnet.get('VpcId') == self.default_vpc_id:
                    continue
                
                name = 'N/A'
                for tag in subnet.get('Tags', []):
                    if tag['Key'] == 'Name':
                        name = tag['Value']
                        break
                
                resources.append({
                    'id': subnet['SubnetId'],
                    'name': name,
                    'vpc_id': subnet.get('VpcId', 'N/A'),
                    'cidr': subnet.get('CidrBlock', 'N/A')
                })
        except Exception as e:
            self.log_error("Error listing Subnets", e)
        return resources
    
    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a subnet"""
        try:
            self.client.delete_subnet(SubnetId=resource['id'])
            return True
        except Exception as e:
            self.log_error(f"Error deleting Subnet {resource['id']}", e)
            return False
