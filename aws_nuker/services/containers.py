"""
Container Services - Cleanup ECS and EKS resources
"""
import boto3
from typing import List, Dict, Any
from botocore.exceptions import ClientError
from .base import BaseService
import time


class ECSClusterService(BaseService):
    """ECS Cluster cleanup"""
    
    def __init__(self, region: str, dry_run: bool = False):
        super().__init__(region, dry_run)
        self.client = boto3.client('ecs', region_name=region)
    
    def get_service_name(self) -> str:
        return "ECS Clusters"
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List all ECS clusters"""
        resources = []
        try:
            cluster_arns = self.client.list_clusters().get('clusterArns', [])
            if cluster_arns:
                clusters = self.client.describe_clusters(clusters=cluster_arns)
                for cluster in clusters.get('clusters', []):
                    resources.append({
                        'id': cluster['clusterArn'],
                        'name': cluster['clusterName'],
                        'status': cluster.get('status', 'N/A')
                    })
        except Exception as e:
            self.log_error("Error listing ECS clusters", e)
        return resources
    
    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete an ECS cluster"""
        try:
            cluster_name = resource['name']
            
            # Delete all services in the cluster
            try:
                service_arns = self.client.list_services(cluster=cluster_name).get('serviceArns', [])
                for service_arn in service_arns:
                    try:
                        # Set desired count to 0
                        self.client.update_service(
                            cluster=cluster_name,
                            service=service_arn,
                            desiredCount=0
                        )
                        # Delete the service
                        self.client.delete_service(
                            cluster=cluster_name,
                            service=service_arn,
                            force=True
                        )
                    except:
                        pass
            except:
                pass
            
            # Stop all tasks
            try:
                task_arns = self.client.list_tasks(cluster=cluster_name).get('taskArns', [])
                for task_arn in task_arns:
                    try:
                        self.client.stop_task(cluster=cluster_name, task=task_arn)
                    except:
                        pass
            except:
                pass
            
            # Wait a bit for services and tasks to stop
            time.sleep(5)
            
            # Delete the cluster
            self.client.delete_cluster(cluster=cluster_name)
            return True
        except Exception as e:
            self.log_error(f"Error deleting ECS cluster {resource['id']}", e)
            return False


class ECSTaskDefinitionService(BaseService):
    """ECS Task Definition cleanup"""
    
    def __init__(self, region: str, dry_run: bool = False):
        super().__init__(region, dry_run)
        self.client = boto3.client('ecs', region_name=region)
    
    def get_service_name(self) -> str:
        return "ECS Task Definitions"
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List all ECS task definitions"""
        resources = []
        try:
            paginator = self.client.get_paginator('list_task_definitions')
            for page in paginator.paginate(status='ACTIVE'):
                for task_def_arn in page.get('taskDefinitionArns', []):
                    family = task_def_arn.split('/')[-1].split(':')[0]
                    resources.append({
                        'id': task_def_arn,
                        'name': family,
                        'arn': task_def_arn
                    })
        except Exception as e:
            self.log_error("Error listing ECS task definitions", e)
        return resources
    
    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Deregister an ECS task definition"""
        try:
            self.client.deregister_task_definition(
                taskDefinition=resource['id']
            )
            return True
        except Exception as e:
            self.log_error(f"Error deregistering task definition {resource['id']}", e)
            return False


class EKSClusterService(BaseService):
    """EKS Cluster cleanup"""
    
    def __init__(self, region: str, dry_run: bool = False):
        super().__init__(region, dry_run)
        self.client = boto3.client('eks', region_name=region)
    
    def get_service_name(self) -> str:
        return "EKS Clusters"
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List all EKS clusters"""
        resources = []
        try:
            clusters = self.client.list_clusters().get('clusters', [])
            for cluster_name in clusters:
                try:
                    cluster = self.client.describe_cluster(name=cluster_name)['cluster']
                    resources.append({
                        'id': cluster_name,
                        'name': cluster_name,
                        'status': cluster.get('status', 'N/A')
                    })
                except:
                    pass
        except Exception as e:
            self.log_error("Error listing EKS clusters", e)
        return resources
    
    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete an EKS cluster"""
        try:
            cluster_name = resource['id']
            
            # Delete all node groups
            try:
                nodegroups = self.client.list_nodegroups(clusterName=cluster_name).get('nodegroups', [])
                for nodegroup in nodegroups:
                    try:
                        self.client.delete_nodegroup(
                            clusterName=cluster_name,
                            nodegroupName=nodegroup
                        )
                    except:
                        pass
            except:
                pass
            
            # Delete all Fargate profiles
            try:
                profiles = self.client.list_fargate_profiles(clusterName=cluster_name).get('fargateProfileNames', [])
                for profile in profiles:
                    try:
                        self.client.delete_fargate_profile(
                            clusterName=cluster_name,
                            fargateProfileName=profile
                        )
                    except:
                        pass
            except:
                pass
            
            # Wait for node groups to delete
            time.sleep(10)
            
            # Delete the cluster
            self.client.delete_cluster(name=cluster_name)
            return True
        except Exception as e:
            self.log_error(f"Error deleting EKS cluster {resource['id']}", e)
            return False
