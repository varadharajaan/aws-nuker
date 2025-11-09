"""
Compute and Application Services - Batch, Elastic Beanstalk, App Runner, etc.
"""
import boto3
from typing import List, Dict, Any
from botocore.exceptions import ClientError
from .base import BaseService
import time


class BatchJobQueueService(BaseService):
    """AWS Batch Job Queue cleanup"""
    
    def __init__(self, region: str, dry_run: bool = False):
        super().__init__(region, dry_run)
        self.client = boto3.client('batch', region_name=region)
    
    def get_service_name(self) -> str:
        return "Batch Job Queues"
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List all Batch job queues"""
        resources = []
        try:
            paginator = self.client.get_paginator('describe_job_queues')
            for page in paginator.paginate():
                for queue in page.get('jobQueues', []):
                    resources.append({
                        'id': queue['jobQueueName'],
                        'name': queue['jobQueueName'],
                        'status': queue.get('status', 'N/A')
                    })
        except Exception as e:
            self.log_error("Error listing Batch job queues", e)
        return resources
    
    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a Batch job queue"""
        try:
            # Disable first
            try:
                self.client.update_job_queue(
                    jobQueue=resource['id'],
                    state='DISABLED'
                )
                time.sleep(2)
            except:
                pass
            
            self.client.delete_job_queue(jobQueue=resource['id'])
            return True
        except Exception as e:
            self.log_error(f"Error deleting Batch job queue {resource['id']}", e)
            return False


class BatchComputeEnvironmentService(BaseService):
    """AWS Batch Compute Environment cleanup"""
    
    def __init__(self, region: str, dry_run: bool = False):
        super().__init__(region, dry_run)
        self.client = boto3.client('batch', region_name=region)
    
    def get_service_name(self) -> str:
        return "Batch Compute Environments"
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List all Batch compute environments"""
        resources = []
        try:
            paginator = self.client.get_paginator('describe_compute_environments')
            for page in paginator.paginate():
                for env in page.get('computeEnvironments', []):
                    resources.append({
                        'id': env['computeEnvironmentName'],
                        'name': env['computeEnvironmentName'],
                        'status': env.get('status', 'N/A')
                    })
        except Exception as e:
            self.log_error("Error listing Batch compute environments", e)
        return resources
    
    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a Batch compute environment"""
        try:
            # Disable first
            try:
                self.client.update_compute_environment(
                    computeEnvironment=resource['id'],
                    state='DISABLED'
                )
                time.sleep(2)
            except:
                pass
            
            self.client.delete_compute_environment(computeEnvironment=resource['id'])
            return True
        except Exception as e:
            self.log_error(f"Error deleting Batch compute environment {resource['id']}", e)
            return False


class ElasticBeanstalkService(BaseService):
    """Elastic Beanstalk Application cleanup"""
    
    def __init__(self, region: str, dry_run: bool = False):
        super().__init__(region, dry_run)
        self.client = boto3.client('elasticbeanstalk', region_name=region)
    
    def get_service_name(self) -> str:
        return "Elastic Beanstalk Applications"
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List all Elastic Beanstalk applications"""
        resources = []
        try:
            response = self.client.describe_applications()
            for app in response.get('Applications', []):
                resources.append({
                    'id': app['ApplicationName'],
                    'name': app['ApplicationName']
                })
        except Exception as e:
            self.log_error("Error listing Elastic Beanstalk applications", e)
        return resources
    
    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete an Elastic Beanstalk application"""
        try:
            self.client.delete_application(
                ApplicationName=resource['id'],
                TerminateEnvByForce=True
            )
            return True
        except Exception as e:
            self.log_error(f"Error deleting Elastic Beanstalk application {resource['id']}", e)
            return False


class AppRunnerService(BaseService):
    """App Runner Service cleanup"""
    
    def __init__(self, region: str, dry_run: bool = False):
        super().__init__(region, dry_run)
        self.client = boto3.client('apprunner', region_name=region)
    
    def get_service_name(self) -> str:
        return "App Runner Services"
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List all App Runner services"""
        resources = []
        try:
            paginator = self.client.get_paginator('list_services')
            for page in paginator.paginate():
                for service in page.get('ServiceSummaryList', []):
                    resources.append({
                        'id': service['ServiceArn'],
                        'name': service.get('ServiceName', 'N/A'),
                        'status': service.get('Status', 'N/A')
                    })
        except Exception as e:
            self.log_error("Error listing App Runner services", e)
        return resources
    
    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete an App Runner service"""
        try:
            self.client.delete_service(ServiceArn=resource['id'])
            return True
        except Exception as e:
            self.log_error(f"Error deleting App Runner service {resource['id']}", e)
            return False


class LightsailInstanceService(BaseService):
    """Lightsail Instance cleanup"""
    
    def __init__(self, region: str, dry_run: bool = False):
        super().__init__(region, dry_run)
        self.client = boto3.client('lightsail', region_name=region)
    
    def get_service_name(self) -> str:
        return "Lightsail Instances"
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List all Lightsail instances"""
        resources = []
        try:
            paginator = self.client.get_paginator('get_instances')
            for page in paginator.paginate():
                for instance in page.get('instances', []):
                    resources.append({
                        'id': instance['name'],
                        'name': instance['name'],
                        'state': instance.get('state', {}).get('name', 'N/A')
                    })
        except Exception as e:
            self.log_error("Error listing Lightsail instances", e)
        return resources
    
    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a Lightsail instance"""
        try:
            self.client.delete_instance(instanceName=resource['id'], forceDeleteAddOns=True)
            return True
        except Exception as e:
            self.log_error(f"Error deleting Lightsail instance {resource['id']}", e)
            return False


class Cloud9EnvironmentService(BaseService):
    """Cloud9 Environment cleanup"""
    
    def __init__(self, region: str, dry_run: bool = False):
        super().__init__(region, dry_run)
        self.client = boto3.client('cloud9', region_name=region)
    
    def get_service_name(self) -> str:
        return "Cloud9 Environments"
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List all Cloud9 environments"""
        resources = []
        try:
            response = self.client.list_environments()
            env_ids = response.get('environmentIds', [])
            
            if env_ids:
                envs = self.client.describe_environments(environmentIds=env_ids)
                for env in envs.get('environments', []):
                    resources.append({
                        'id': env['id'],
                        'name': env.get('name', 'N/A'),
                        'type': env.get('type', 'N/A')
                    })
        except Exception as e:
            self.log_error("Error listing Cloud9 environments", e)
        return resources
    
    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a Cloud9 environment"""
        try:
            self.client.delete_environment(environmentId=resource['id'])
            return True
        except Exception as e:
            self.log_error(f"Error deleting Cloud9 environment {resource['id']}", e)
            return False
