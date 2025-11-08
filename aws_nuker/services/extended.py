"""
Additional AWS Services - Load Balancers, Auto Scaling, Secrets Manager, etc.
"""
import boto3
from typing import List, Dict, Any
from botocore.exceptions import ClientError
from .base import BaseService
import time


class ELBService(BaseService):
    """Classic Load Balancer cleanup"""
    
    def __init__(self, region: str, dry_run: bool = False):
        super().__init__(region, dry_run)
        self.client = boto3.client('elb', region_name=region)
    
    def get_service_name(self) -> str:
        return "Classic Load Balancers (ELB)"
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List all Classic Load Balancers"""
        resources = []
        try:
            paginator = self.client.get_paginator('describe_load_balancers')
            for page in paginator.paginate():
                for lb in page.get('LoadBalancerDescriptions', []):
                    resources.append({
                        'id': lb['LoadBalancerName'],
                        'name': lb['LoadBalancerName'],
                        'dns': lb.get('DNSName', 'N/A')
                    })
        except Exception as e:
            self.log_error("Error listing Classic Load Balancers", e)
        return resources
    
    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a Classic Load Balancer"""
        try:
            self.client.delete_load_balancer(
                LoadBalancerName=resource['id']
            )
            return True
        except Exception as e:
            self.log_error(f"Error deleting Classic Load Balancer {resource['id']}", e)
            return False


class ELBv2Service(BaseService):
    """Application/Network Load Balancer cleanup"""
    
    def __init__(self, region: str, dry_run: bool = False):
        super().__init__(region, dry_run)
        self.client = boto3.client('elbv2', region_name=region)
    
    def get_service_name(self) -> str:
        return "Application/Network Load Balancers (ALB/NLB)"
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List all Application and Network Load Balancers"""
        resources = []
        try:
            paginator = self.client.get_paginator('describe_load_balancers')
            for page in paginator.paginate():
                for lb in page.get('LoadBalancers', []):
                    resources.append({
                        'id': lb['LoadBalancerArn'],
                        'name': lb['LoadBalancerName'],
                        'type': lb.get('Type', 'N/A'),
                        'dns': lb.get('DNSName', 'N/A')
                    })
        except Exception as e:
            self.log_error("Error listing ALB/NLB Load Balancers", e)
        return resources
    
    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete an Application or Network Load Balancer"""
        try:
            self.client.delete_load_balancer(
                LoadBalancerArn=resource['id']
            )
            return True
        except Exception as e:
            self.log_error(f"Error deleting Load Balancer {resource['id']}", e)
            return False


class AutoScalingGroupService(BaseService):
    """Auto Scaling Group cleanup"""
    
    def __init__(self, region: str, dry_run: bool = False):
        super().__init__(region, dry_run)
        self.client = boto3.client('autoscaling', region_name=region)
    
    def get_service_name(self) -> str:
        return "Auto Scaling Groups"
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List all Auto Scaling Groups"""
        resources = []
        try:
            paginator = self.client.get_paginator('describe_auto_scaling_groups')
            for page in paginator.paginate():
                for asg in page.get('AutoScalingGroups', []):
                    resources.append({
                        'id': asg['AutoScalingGroupName'],
                        'name': asg['AutoScalingGroupName'],
                        'instances': len(asg.get('Instances', []))
                    })
        except Exception as e:
            self.log_error("Error listing Auto Scaling Groups", e)
        return resources
    
    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete an Auto Scaling Group"""
        try:
            # Force delete with instances
            self.client.delete_auto_scaling_group(
                AutoScalingGroupName=resource['id'],
                ForceDelete=True
            )
            return True
        except Exception as e:
            self.log_error(f"Error deleting Auto Scaling Group {resource['id']}", e)
            return False


class LaunchTemplateService(BaseService):
    """Launch Template cleanup"""
    
    def __init__(self, region: str, dry_run: bool = False):
        super().__init__(region, dry_run)
        self.client = boto3.client('ec2', region_name=region)
    
    def get_service_name(self) -> str:
        return "Launch Templates"
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List all Launch Templates"""
        resources = []
        try:
            paginator = self.client.get_paginator('describe_launch_templates')
            for page in paginator.paginate():
                for lt in page.get('LaunchTemplates', []):
                    resources.append({
                        'id': lt['LaunchTemplateId'],
                        'name': lt['LaunchTemplateName']
                    })
        except Exception as e:
            self.log_error("Error listing Launch Templates", e)
        return resources
    
    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a Launch Template"""
        try:
            self.client.delete_launch_template(
                LaunchTemplateId=resource['id']
            )
            return True
        except Exception as e:
            self.log_error(f"Error deleting Launch Template {resource['id']}", e)
            return False


class SecretsManagerService(BaseService):
    """Secrets Manager Secret cleanup"""
    
    def __init__(self, region: str, dry_run: bool = False):
        super().__init__(region, dry_run)
        self.client = boto3.client('secretsmanager', region_name=region)
    
    def get_service_name(self) -> str:
        return "Secrets Manager Secrets"
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List all Secrets Manager secrets"""
        resources = []
        try:
            paginator = self.client.get_paginator('list_secrets')
            for page in paginator.paginate():
                for secret in page.get('SecretList', []):
                    resources.append({
                        'id': secret['ARN'],
                        'name': secret['Name'],
                        'arn': secret['ARN']
                    })
        except Exception as e:
            self.log_error("Error listing Secrets Manager secrets", e)
        return resources
    
    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a Secrets Manager secret"""
        try:
            # Force delete without recovery window
            self.client.delete_secret(
                SecretId=resource['id'],
                ForceDeleteWithoutRecovery=True
            )
            return True
        except Exception as e:
            self.log_error(f"Error deleting Secret {resource['id']}", e)
            return False


class CloudWatchAlarmsService(BaseService):
    """CloudWatch Alarms cleanup"""
    
    def __init__(self, region: str, dry_run: bool = False):
        super().__init__(region, dry_run)
        self.client = boto3.client('cloudwatch', region_name=region)
    
    def get_service_name(self) -> str:
        return "CloudWatch Alarms"
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List all CloudWatch alarms"""
        resources = []
        try:
            paginator = self.client.get_paginator('describe_alarms')
            for page in paginator.paginate():
                for alarm in page.get('MetricAlarms', []):
                    resources.append({
                        'id': alarm['AlarmName'],
                        'name': alarm['AlarmName'],
                        'state': alarm.get('StateValue', 'N/A')
                    })
        except Exception as e:
            self.log_error("Error listing CloudWatch alarms", e)
        return resources
    
    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a CloudWatch alarm"""
        try:
            self.client.delete_alarms(
                AlarmNames=[resource['id']]
            )
            return True
        except Exception as e:
            self.log_error(f"Error deleting CloudWatch alarm {resource['id']}", e)
            return False


class ECRService(BaseService):
    """ECR Repository cleanup"""
    
    def __init__(self, region: str, dry_run: bool = False):
        super().__init__(region, dry_run)
        self.client = boto3.client('ecr', region_name=region)
    
    def get_service_name(self) -> str:
        return "ECR Repositories"
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List all ECR repositories"""
        resources = []
        try:
            paginator = self.client.get_paginator('describe_repositories')
            for page in paginator.paginate():
                for repo in page.get('repositories', []):
                    resources.append({
                        'id': repo['repositoryName'],
                        'name': repo['repositoryName'],
                        'uri': repo.get('repositoryUri', 'N/A')
                    })
        except Exception as e:
            self.log_error("Error listing ECR repositories", e)
        return resources
    
    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete an ECR repository"""
        try:
            # Force delete with all images
            self.client.delete_repository(
                repositoryName=resource['id'],
                force=True
            )
            return True
        except Exception as e:
            self.log_error(f"Error deleting ECR repository {resource['id']}", e)
            return False


class KinesisStreamService(BaseService):
    """Kinesis Stream cleanup"""
    
    def __init__(self, region: str, dry_run: bool = False):
        super().__init__(region, dry_run)
        self.client = boto3.client('kinesis', region_name=region)
    
    def get_service_name(self) -> str:
        return "Kinesis Streams"
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List all Kinesis streams"""
        resources = []
        try:
            paginator = self.client.get_paginator('list_streams')
            for page in paginator.paginate():
                for stream_name in page.get('StreamNames', []):
                    resources.append({
                        'id': stream_name,
                        'name': stream_name
                    })
        except Exception as e:
            self.log_error("Error listing Kinesis streams", e)
        return resources
    
    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a Kinesis stream"""
        try:
            self.client.delete_stream(
                StreamName=resource['id'],
                EnforceConsumerDeletion=True
            )
            return True
        except Exception as e:
            self.log_error(f"Error deleting Kinesis stream {resource['id']}", e)
            return False


class BackupVaultService(BaseService):
    """AWS Backup Vault cleanup"""
    
    def __init__(self, region: str, dry_run: bool = False):
        super().__init__(region, dry_run)
        self.client = boto3.client('backup', region_name=region)
    
    def get_service_name(self) -> str:
        return "AWS Backup Vaults"
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List all AWS Backup vaults"""
        resources = []
        try:
            paginator = self.client.get_paginator('list_backup_vaults')
            for page in paginator.paginate():
                for vault in page.get('BackupVaultList', []):
                    # Skip default vault
                    if vault['BackupVaultName'] != 'Default':
                        resources.append({
                            'id': vault['BackupVaultName'],
                            'name': vault['BackupVaultName']
                        })
        except Exception as e:
            self.log_error("Error listing AWS Backup vaults", e)
        return resources
    
    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete an AWS Backup vault"""
        try:
            # Delete all recovery points first
            try:
                recovery_points = self.client.list_recovery_points_by_backup_vault(
                    BackupVaultName=resource['id']
                )
                for rp in recovery_points.get('RecoveryPoints', []):
                    try:
                        self.client.delete_recovery_point(
                            BackupVaultName=resource['id'],
                            RecoveryPointArn=rp['RecoveryPointArn']
                        )
                    except:
                        pass
                time.sleep(2)
            except:
                pass
            
            # Delete the vault
            self.client.delete_backup_vault(
                BackupVaultName=resource['id']
            )
            return True
        except Exception as e:
            self.log_error(f"Error deleting Backup vault {resource['id']}", e)
            return False
