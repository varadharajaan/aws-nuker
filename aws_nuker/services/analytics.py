"""
Analytics Services - Athena, Glue, EMR, Data Pipeline, etc.
"""
import boto3
from typing import List, Dict, Any
from botocore.exceptions import ClientError
from .base import BaseService


class AthenaService(BaseService):
    """Athena Workgroup cleanup"""
    
    def __init__(self, region: str, dry_run: bool = False):
        super().__init__(region, dry_run)
        self.client = boto3.client('athena', region_name=region)
    
    def get_service_name(self) -> str:
        return "Athena Workgroups"
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List all Athena workgroups"""
        resources = []
        try:
            paginator = self.client.get_paginator('list_work_groups')
            for page in paginator.paginate():
                for wg in page.get('WorkGroups', []):
                    # Skip primary workgroup
                    if wg['Name'] != 'primary':
                        resources.append({
                            'id': wg['Name'],
                            'name': wg['Name'],
                            'state': wg.get('State', 'N/A')
                        })
        except Exception as e:
            self.log_error("Error listing Athena workgroups", e)
        return resources
    
    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete an Athena workgroup"""
        try:
            self.client.delete_work_group(
                WorkGroup=resource['id'],
                RecursiveDeleteOption=True
            )
            return True
        except Exception as e:
            self.log_error(f"Error deleting Athena workgroup {resource['id']}", e)
            return False


class GlueService(BaseService):
    """Glue Database and Crawler cleanup"""
    
    def __init__(self, region: str, dry_run: bool = False):
        super().__init__(region, dry_run)
        self.client = boto3.client('glue', region_name=region)
    
    def get_service_name(self) -> str:
        return "Glue Databases"
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List all Glue databases"""
        resources = []
        try:
            paginator = self.client.get_paginator('get_databases')
            for page in paginator.paginate():
                for db in page.get('DatabaseList', []):
                    resources.append({
                        'id': db['Name'],
                        'name': db['Name']
                    })
        except Exception as e:
            self.log_error("Error listing Glue databases", e)
        return resources
    
    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a Glue database"""
        try:
            self.client.delete_database(Name=resource['id'])
            return True
        except Exception as e:
            self.log_error(f"Error deleting Glue database {resource['id']}", e)
            return False


class GlueCrawlerService(BaseService):
    """Glue Crawler cleanup"""
    
    def __init__(self, region: str, dry_run: bool = False):
        super().__init__(region, dry_run)
        self.client = boto3.client('glue', region_name=region)
    
    def get_service_name(self) -> str:
        return "Glue Crawlers"
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List all Glue crawlers"""
        resources = []
        try:
            paginator = self.client.get_paginator('get_crawlers')
            for page in paginator.paginate():
                for crawler in page.get('Crawlers', []):
                    resources.append({
                        'id': crawler['Name'],
                        'name': crawler['Name'],
                        'state': crawler.get('State', 'N/A')
                    })
        except Exception as e:
            self.log_error("Error listing Glue crawlers", e)
        return resources
    
    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a Glue crawler"""
        try:
            self.client.delete_crawler(Name=resource['id'])
            return True
        except Exception as e:
            self.log_error(f"Error deleting Glue crawler {resource['id']}", e)
            return False


class EMRClusterService(BaseService):
    """EMR Cluster cleanup"""
    
    def __init__(self, region: str, dry_run: bool = False):
        super().__init__(region, dry_run)
        self.client = boto3.client('emr', region_name=region)
    
    def get_service_name(self) -> str:
        return "EMR Clusters"
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List all EMR clusters"""
        resources = []
        try:
            paginator = self.client.get_paginator('list_clusters')
            for page in paginator.paginate(ClusterStates=['STARTING', 'BOOTSTRAPPING', 'RUNNING', 'WAITING']):
                for cluster in page.get('Clusters', []):
                    resources.append({
                        'id': cluster['Id'],
                        'name': cluster.get('Name', 'N/A'),
                        'status': cluster.get('Status', {}).get('State', 'N/A')
                    })
        except Exception as e:
            self.log_error("Error listing EMR clusters", e)
        return resources
    
    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Terminate an EMR cluster"""
        try:
            self.client.terminate_job_flows(JobFlowIds=[resource['id']])
            return True
        except Exception as e:
            self.log_error(f"Error terminating EMR cluster {resource['id']}", e)
            return False


class DataPipelineService(BaseService):
    """Data Pipeline cleanup"""
    
    def __init__(self, region: str, dry_run: bool = False):
        super().__init__(region, dry_run)
        self.client = boto3.client('datapipeline', region_name=region)
    
    def get_service_name(self) -> str:
        return "Data Pipelines"
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List all Data Pipelines"""
        resources = []
        try:
            paginator = self.client.get_paginator('list_pipelines')
            for page in paginator.paginate():
                for pipeline in page.get('pipelineIdList', []):
                    resources.append({
                        'id': pipeline['id'],
                        'name': pipeline.get('name', 'N/A')
                    })
        except Exception as e:
            self.log_error("Error listing Data Pipelines", e)
        return resources
    
    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a Data Pipeline"""
        try:
            self.client.delete_pipeline(pipelineId=resource['id'])
            return True
        except Exception as e:
            self.log_error(f"Error deleting Data Pipeline {resource['id']}", e)
            return False


class RedshiftClusterService(BaseService):
    """Redshift Cluster cleanup"""
    
    def __init__(self, region: str, dry_run: bool = False):
        super().__init__(region, dry_run)
        self.client = boto3.client('redshift', region_name=region)
    
    def get_service_name(self) -> str:
        return "Redshift Clusters"
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List all Redshift clusters"""
        resources = []
        try:
            paginator = self.client.get_paginator('describe_clusters')
            for page in paginator.paginate():
                for cluster in page.get('Clusters', []):
                    resources.append({
                        'id': cluster['ClusterIdentifier'],
                        'name': cluster['ClusterIdentifier'],
                        'status': cluster.get('ClusterStatus', 'N/A')
                    })
        except Exception as e:
            self.log_error("Error listing Redshift clusters", e)
        return resources
    
    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a Redshift cluster"""
        try:
            self.client.delete_cluster(
                ClusterIdentifier=resource['id'],
                SkipFinalClusterSnapshot=True
            )
            return True
        except Exception as e:
            self.log_error(f"Error deleting Redshift cluster {resource['id']}", e)
            return False


class OpenSearchDomainService(BaseService):
    """OpenSearch Domain cleanup"""
    
    def __init__(self, region: str, dry_run: bool = False):
        super().__init__(region, dry_run)
        self.client = boto3.client('opensearch', region_name=region)
    
    def get_service_name(self) -> str:
        return "OpenSearch Domains"
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List all OpenSearch domains"""
        resources = []
        try:
            response = self.client.list_domain_names()
            for domain in response.get('DomainNames', []):
                resources.append({
                    'id': domain['DomainName'],
                    'name': domain['DomainName']
                })
        except Exception as e:
            self.log_error("Error listing OpenSearch domains", e)
        return resources
    
    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete an OpenSearch domain"""
        try:
            self.client.delete_domain(DomainName=resource['id'])
            return True
        except Exception as e:
            self.log_error(f"Error deleting OpenSearch domain {resource['id']}", e)
            return False
