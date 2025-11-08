"""
IAM Service - Cleanup IAM resources
"""
import boto3
from typing import List, Dict, Any
from botocore.exceptions import ClientError
from .base import BaseService


class IAMUserService(BaseService):
    """IAM User cleanup"""
    
    def __init__(self, region: str, dry_run: bool = False):
        super().__init__(region, dry_run)
        self.client = boto3.client('iam')  # IAM is global
    
    def get_service_name(self) -> str:
        return "IAM Users"
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List all IAM users"""
        resources = []
        try:
            paginator = self.client.get_paginator('list_users')
            for page in paginator.paginate():
                for user in page.get('Users', []):
                    resources.append({
                        'id': user['UserName'],
                        'name': user['UserName'],
                        'arn': user.get('Arn', 'N/A')
                    })
        except Exception as e:
            self.log_error("Error listing IAM users", e)
        return resources
    
    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete an IAM user with all dependencies"""
        try:
            username = resource['id']
            
            # Delete access keys
            try:
                keys = self.client.list_access_keys(UserName=username)
                for key in keys.get('AccessKeyMetadata', []):
                    self.client.delete_access_key(
                        UserName=username,
                        AccessKeyId=key['AccessKeyId']
                    )
            except:
                pass
            
            # Delete signing certificates
            try:
                certs = self.client.list_signing_certificates(UserName=username)
                for cert in certs.get('Certificates', []):
                    self.client.delete_signing_certificate(
                        UserName=username,
                        CertificateId=cert['CertificateId']
                    )
            except:
                pass
            
            # Delete SSH public keys
            try:
                keys = self.client.list_ssh_public_keys(UserName=username)
                for key in keys.get('SSHPublicKeys', []):
                    self.client.delete_ssh_public_key(
                        UserName=username,
                        SSHPublicKeyId=key['SSHPublicKeyId']
                    )
            except:
                pass
            
            # Delete service specific credentials
            try:
                creds = self.client.list_service_specific_credentials(UserName=username)
                for cred in creds.get('ServiceSpecificCredentials', []):
                    self.client.delete_service_specific_credential(
                        UserName=username,
                        ServiceSpecificCredentialId=cred['ServiceSpecificCredentialId']
                    )
            except:
                pass
            
            # Delete login profile
            try:
                self.client.delete_login_profile(UserName=username)
            except:
                pass
            
            # Remove from groups
            try:
                groups = self.client.list_groups_for_user(UserName=username)
                for group in groups.get('Groups', []):
                    self.client.remove_user_from_group(
                        UserName=username,
                        GroupName=group['GroupName']
                    )
            except:
                pass
            
            # Detach managed policies
            try:
                policies = self.client.list_attached_user_policies(UserName=username)
                for policy in policies.get('AttachedPolicies', []):
                    self.client.detach_user_policy(
                        UserName=username,
                        PolicyArn=policy['PolicyArn']
                    )
            except:
                pass
            
            # Delete inline policies
            try:
                policies = self.client.list_user_policies(UserName=username)
                for policy_name in policies.get('PolicyNames', []):
                    self.client.delete_user_policy(
                        UserName=username,
                        PolicyName=policy_name
                    )
            except:
                pass
            
            # Delete MFA devices
            try:
                devices = self.client.list_mfa_devices(UserName=username)
                for device in devices.get('MFADevices', []):
                    self.client.deactivate_mfa_device(
                        UserName=username,
                        SerialNumber=device['SerialNumber']
                    )
            except:
                pass
            
            # Delete the user
            self.client.delete_user(UserName=username)
            return True
        except Exception as e:
            self.log_error(f"Error deleting IAM user {resource['id']}", e)
            return False


class IAMRoleService(BaseService):
    """IAM Role cleanup"""
    
    def __init__(self, region: str, dry_run: bool = False):
        super().__init__(region, dry_run)
        self.client = boto3.client('iam')  # IAM is global
    
    def get_service_name(self) -> str:
        return "IAM Roles"
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List all IAM roles (excluding AWS service roles)"""
        resources = []
        try:
            paginator = self.client.get_paginator('list_roles')
            for page in paginator.paginate():
                for role in page.get('Roles', []):
                    # Skip AWS service-linked roles
                    if '/aws-service-role/' not in role.get('Path', ''):
                        resources.append({
                            'id': role['RoleName'],
                            'name': role['RoleName'],
                            'arn': role.get('Arn', 'N/A')
                        })
        except Exception as e:
            self.log_error("Error listing IAM roles", e)
        return resources
    
    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete an IAM role with all dependencies"""
        try:
            role_name = resource['id']
            
            # Detach managed policies
            try:
                policies = self.client.list_attached_role_policies(RoleName=role_name)
                for policy in policies.get('AttachedPolicies', []):
                    self.client.detach_role_policy(
                        RoleName=role_name,
                        PolicyArn=policy['PolicyArn']
                    )
            except:
                pass
            
            # Delete inline policies
            try:
                policies = self.client.list_role_policies(RoleName=role_name)
                for policy_name in policies.get('PolicyNames', []):
                    self.client.delete_role_policy(
                        RoleName=role_name,
                        PolicyName=policy_name
                    )
            except:
                pass
            
            # Delete instance profiles
            try:
                profiles = self.client.list_instance_profiles_for_role(RoleName=role_name)
                for profile in profiles.get('InstanceProfiles', []):
                    self.client.remove_role_from_instance_profile(
                        InstanceProfileName=profile['InstanceProfileName'],
                        RoleName=role_name
                    )
                    try:
                        self.client.delete_instance_profile(
                            InstanceProfileName=profile['InstanceProfileName']
                        )
                    except:
                        pass
            except:
                pass
            
            # Delete the role
            self.client.delete_role(RoleName=role_name)
            return True
        except Exception as e:
            self.log_error(f"Error deleting IAM role {resource['id']}", e)
            return False


class IAMPolicyService(BaseService):
    """IAM Policy cleanup (customer managed only)"""
    
    def __init__(self, region: str, dry_run: bool = False):
        super().__init__(region, dry_run)
        self.client = boto3.client('iam')  # IAM is global
    
    def get_service_name(self) -> str:
        return "IAM Policies"
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List all customer managed IAM policies"""
        resources = []
        try:
            paginator = self.client.get_paginator('list_policies')
            for page in paginator.paginate(Scope='Local'):  # Only customer managed
                for policy in page.get('Policies', []):
                    resources.append({
                        'id': policy['PolicyName'],
                        'name': policy['PolicyName'],
                        'arn': policy.get('Arn', 'N/A')
                    })
        except Exception as e:
            self.log_error("Error listing IAM policies", e)
        return resources
    
    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete an IAM policy"""
        try:
            # Get policy ARN
            policies = self.client.list_policies(Scope='Local')
            policy_arn = None
            for policy in policies.get('Policies', []):
                if policy['PolicyName'] == resource['id']:
                    policy_arn = policy['Arn']
                    break
            
            if not policy_arn:
                return False
            
            # Delete all non-default versions
            try:
                versions = self.client.list_policy_versions(PolicyArn=policy_arn)
                for version in versions.get('Versions', []):
                    if not version.get('IsDefaultVersion', False):
                        self.client.delete_policy_version(
                            PolicyArn=policy_arn,
                            VersionId=version['VersionId']
                        )
            except:
                pass
            
            # Detach from all entities
            # This would require listing all users/roles/groups and checking
            # For simplicity, we'll try to delete and let it fail if attached
            
            # Delete the policy
            self.client.delete_policy(PolicyArn=policy_arn)
            return True
        except Exception as e:
            self.log_error(f"Error deleting IAM policy {resource['id']}", e)
            return False


class IAMGroupService(BaseService):
    """IAM Group cleanup"""
    
    def __init__(self, region: str, dry_run: bool = False):
        super().__init__(region, dry_run)
        self.client = boto3.client('iam')  # IAM is global
    
    def get_service_name(self) -> str:
        return "IAM Groups"
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List all IAM groups"""
        resources = []
        try:
            paginator = self.client.get_paginator('list_groups')
            for page in paginator.paginate():
                for group in page.get('Groups', []):
                    resources.append({
                        'id': group['GroupName'],
                        'name': group['GroupName'],
                        'arn': group.get('Arn', 'N/A')
                    })
        except Exception as e:
            self.log_error("Error listing IAM groups", e)
        return resources
    
    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete an IAM group"""
        try:
            group_name = resource['id']
            
            # Remove all users from group
            try:
                users = self.client.get_group(GroupName=group_name)
                for user in users.get('Users', []):
                    self.client.remove_user_from_group(
                        GroupName=group_name,
                        UserName=user['UserName']
                    )
            except:
                pass
            
            # Detach managed policies
            try:
                policies = self.client.list_attached_group_policies(GroupName=group_name)
                for policy in policies.get('AttachedPolicies', []):
                    self.client.detach_group_policy(
                        GroupName=group_name,
                        PolicyArn=policy['PolicyArn']
                    )
            except:
                pass
            
            # Delete inline policies
            try:
                policies = self.client.list_group_policies(GroupName=group_name)
                for policy_name in policies.get('PolicyNames', []):
                    self.client.delete_group_policy(
                        GroupName=group_name,
                        PolicyName=policy_name
                    )
            except:
                pass
            
            # Delete the group
            self.client.delete_group(GroupName=group_name)
            return True
        except Exception as e:
            self.log_error(f"Error deleting IAM group {resource['id']}", e)
            return False
