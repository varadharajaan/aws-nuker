"""
Additional AWS Services - DynamoDB, SNS, SQS, API Gateway, etc.
"""
import boto3
from typing import List, Dict, Any
from botocore.exceptions import ClientError
from .base import BaseService


class DynamoDBService(BaseService):
    """DynamoDB Table cleanup"""
    
    def __init__(self, region: str, dry_run: bool = False):
        super().__init__(region, dry_run)
        self.client = boto3.client('dynamodb', region_name=region)
    
    def get_service_name(self) -> str:
        return "DynamoDB Tables"
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List all DynamoDB tables"""
        resources = []
        try:
            paginator = self.client.get_paginator('list_tables')
            for page in paginator.paginate():
                for table_name in page.get('TableNames', []):
                    resources.append({
                        'id': table_name,
                        'name': table_name
                    })
        except Exception as e:
            self.log_error("Error listing DynamoDB tables", e)
        return resources
    
    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a DynamoDB table"""
        try:
            self.client.delete_table(TableName=resource['id'])
            return True
        except Exception as e:
            self.log_error(f"Error deleting DynamoDB table {resource['id']}", e)
            return False


class SNSService(BaseService):
    """SNS Topic cleanup"""
    
    def __init__(self, region: str, dry_run: bool = False):
        super().__init__(region, dry_run)
        self.client = boto3.client('sns', region_name=region)
    
    def get_service_name(self) -> str:
        return "SNS Topics"
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List all SNS topics"""
        resources = []
        try:
            paginator = self.client.get_paginator('list_topics')
            for page in paginator.paginate():
                for topic in page.get('Topics', []):
                    topic_arn = topic['TopicArn']
                    topic_name = topic_arn.split(':')[-1]
                    resources.append({
                        'id': topic_arn,
                        'name': topic_name,
                        'arn': topic_arn
                    })
        except Exception as e:
            self.log_error("Error listing SNS topics", e)
        return resources
    
    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete an SNS topic"""
        try:
            self.client.delete_topic(TopicArn=resource['id'])
            return True
        except Exception as e:
            self.log_error(f"Error deleting SNS topic {resource['id']}", e)
            return False


class SQSService(BaseService):
    """SQS Queue cleanup"""
    
    def __init__(self, region: str, dry_run: bool = False):
        super().__init__(region, dry_run)
        self.client = boto3.client('sqs', region_name=region)
    
    def get_service_name(self) -> str:
        return "SQS Queues"
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List all SQS queues"""
        resources = []
        try:
            paginator = self.client.get_paginator('list_queues')
            for page in paginator.paginate():
                for queue_url in page.get('QueueUrls', []):
                    queue_name = queue_url.split('/')[-1]
                    resources.append({
                        'id': queue_url,
                        'name': queue_name,
                        'url': queue_url
                    })
        except Exception as e:
            self.log_error("Error listing SQS queues", e)
        return resources
    
    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete an SQS queue"""
        try:
            self.client.delete_queue(QueueUrl=resource['id'])
            return True
        except Exception as e:
            self.log_error(f"Error deleting SQS queue {resource['id']}", e)
            return False


class APIGatewayService(BaseService):
    """API Gateway REST API cleanup"""
    
    def __init__(self, region: str, dry_run: bool = False):
        super().__init__(region, dry_run)
        self.client = boto3.client('apigateway', region_name=region)
    
    def get_service_name(self) -> str:
        return "API Gateway REST APIs"
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List all API Gateway REST APIs"""
        resources = []
        try:
            paginator = self.client.get_paginator('get_rest_apis')
            for page in paginator.paginate():
                for api in page.get('items', []):
                    resources.append({
                        'id': api['id'],
                        'name': api.get('name', 'N/A'),
                        'description': api.get('description', 'N/A')
                    })
        except Exception as e:
            self.log_error("Error listing API Gateway REST APIs", e)
        return resources
    
    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete an API Gateway REST API"""
        try:
            self.client.delete_rest_api(restApiId=resource['id'])
            return True
        except Exception as e:
            self.log_error(f"Error deleting API Gateway REST API {resource['id']}", e)
            return False


class APIGatewayV2Service(BaseService):
    """API Gateway V2 (HTTP/WebSocket) cleanup"""
    
    def __init__(self, region: str, dry_run: bool = False):
        super().__init__(region, dry_run)
        self.client = boto3.client('apigatewayv2', region_name=region)
    
    def get_service_name(self) -> str:
        return "API Gateway V2 APIs"
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List all API Gateway V2 APIs"""
        resources = []
        try:
            paginator = self.client.get_paginator('get_apis')
            for page in paginator.paginate():
                for api in page.get('Items', []):
                    resources.append({
                        'id': api['ApiId'],
                        'name': api.get('Name', 'N/A'),
                        'protocol': api.get('ProtocolType', 'N/A')
                    })
        except Exception as e:
            self.log_error("Error listing API Gateway V2 APIs", e)
        return resources
    
    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete an API Gateway V2 API"""
        try:
            self.client.delete_api(ApiId=resource['id'])
            return True
        except Exception as e:
            self.log_error(f"Error deleting API Gateway V2 API {resource['id']}", e)
            return False


class ElastiCacheService(BaseService):
    """ElastiCache Cluster cleanup"""
    
    def __init__(self, region: str, dry_run: bool = False):
        super().__init__(region, dry_run)
        self.client = boto3.client('elasticache', region_name=region)
    
    def get_service_name(self) -> str:
        return "ElastiCache Clusters"
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List all ElastiCache clusters"""
        resources = []
        try:
            paginator = self.client.get_paginator('describe_cache_clusters')
            for page in paginator.paginate():
                for cluster in page.get('CacheClusters', []):
                    resources.append({
                        'id': cluster['CacheClusterId'],
                        'name': cluster['CacheClusterId'],
                        'status': cluster.get('CacheClusterStatus', 'N/A')
                    })
        except Exception as e:
            self.log_error("Error listing ElastiCache clusters", e)
        return resources
    
    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete an ElastiCache cluster"""
        try:
            self.client.delete_cache_cluster(
                CacheClusterId=resource['id']
            )
            return True
        except Exception as e:
            self.log_error(f"Error deleting ElastiCache cluster {resource['id']}", e)
            return False


class CloudWatchLogsService(BaseService):
    """CloudWatch Log Groups cleanup"""
    
    def __init__(self, region: str, dry_run: bool = False):
        super().__init__(region, dry_run)
        self.client = boto3.client('logs', region_name=region)
    
    def get_service_name(self) -> str:
        return "CloudWatch Log Groups"
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List all CloudWatch log groups"""
        resources = []
        try:
            paginator = self.client.get_paginator('describe_log_groups')
            for page in paginator.paginate():
                for log_group in page.get('logGroups', []):
                    resources.append({
                        'id': log_group['logGroupName'],
                        'name': log_group['logGroupName']
                    })
        except Exception as e:
            self.log_error("Error listing CloudWatch log groups", e)
        return resources
    
    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a CloudWatch log group"""
        try:
            self.client.delete_log_group(logGroupName=resource['id'])
            return True
        except Exception as e:
            self.log_error(f"Error deleting CloudWatch log group {resource['id']}", e)
            return False


class Route53Service(BaseService):
    """Route53 Hosted Zone cleanup"""
    
    def __init__(self, region: str, dry_run: bool = False):
        super().__init__(region, dry_run)
        self.client = boto3.client('route53')  # Route53 is global
    
    def get_service_name(self) -> str:
        return "Route53 Hosted Zones"
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List all Route53 hosted zones"""
        resources = []
        try:
            paginator = self.client.get_paginator('list_hosted_zones')
            for page in paginator.paginate():
                for zone in page.get('HostedZones', []):
                    resources.append({
                        'id': zone['Id'],
                        'name': zone['Name'],
                        'private': zone.get('Config', {}).get('PrivateZone', False)
                    })
        except Exception as e:
            self.log_error("Error listing Route53 hosted zones", e)
        return resources
    
    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a Route53 hosted zone"""
        try:
            zone_id = resource['id'].split('/')[-1]
            
            # Delete all record sets except NS and SOA
            try:
                records = self.client.list_resource_record_sets(HostedZoneId=zone_id)
                for record in records.get('ResourceRecordSets', []):
                    if record['Type'] not in ['NS', 'SOA']:
                        try:
                            self.client.change_resource_record_sets(
                                HostedZoneId=zone_id,
                                ChangeBatch={
                                    'Changes': [{
                                        'Action': 'DELETE',
                                        'ResourceRecordSet': record
                                    }]
                                }
                            )
                        except:
                            pass
            except:
                pass
            
            # Delete the hosted zone
            self.client.delete_hosted_zone(Id=zone_id)
            return True
        except Exception as e:
            self.log_error(f"Error deleting Route53 hosted zone {resource['id']}", e)
            return False
