"""
Machine Learning Services - SageMaker, Comprehend, Rekognition, etc.
"""
import boto3
from typing import List, Dict, Any
from botocore.exceptions import ClientError
from .base import BaseService


class SageMakerNotebookService(BaseService):
    """SageMaker Notebook Instance cleanup"""
    
    def __init__(self, region: str, dry_run: bool = False):
        super().__init__(region, dry_run)
        self.client = boto3.client('sagemaker', region_name=region)
    
    def get_service_name(self) -> str:
        return "SageMaker Notebook Instances"
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List all SageMaker notebook instances"""
        resources = []
        try:
            paginator = self.client.get_paginator('list_notebook_instances')
            for page in paginator.paginate():
                for notebook in page.get('NotebookInstances', []):
                    resources.append({
                        'id': notebook['NotebookInstanceName'],
                        'name': notebook['NotebookInstanceName'],
                        'status': notebook.get('NotebookInstanceStatus', 'N/A')
                    })
        except Exception as e:
            self.log_error("Error listing SageMaker notebook instances", e)
        return resources
    
    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a SageMaker notebook instance"""
        try:
            # Stop if running
            try:
                self.client.stop_notebook_instance(NotebookInstanceName=resource['id'])
            except:
                pass
            
            # Delete the instance
            self.client.delete_notebook_instance(NotebookInstanceName=resource['id'])
            return True
        except Exception as e:
            self.log_error(f"Error deleting SageMaker notebook {resource['id']}", e)
            return False


class SageMakerEndpointService(BaseService):
    """SageMaker Endpoint cleanup"""
    
    def __init__(self, region: str, dry_run: bool = False):
        super().__init__(region, dry_run)
        self.client = boto3.client('sagemaker', region_name=region)
    
    def get_service_name(self) -> str:
        return "SageMaker Endpoints"
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List all SageMaker endpoints"""
        resources = []
        try:
            paginator = self.client.get_paginator('list_endpoints')
            for page in paginator.paginate():
                for endpoint in page.get('Endpoints', []):
                    resources.append({
                        'id': endpoint['EndpointName'],
                        'name': endpoint['EndpointName'],
                        'status': endpoint.get('EndpointStatus', 'N/A')
                    })
        except Exception as e:
            self.log_error("Error listing SageMaker endpoints", e)
        return resources
    
    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a SageMaker endpoint"""
        try:
            self.client.delete_endpoint(EndpointName=resource['id'])
            return True
        except Exception as e:
            self.log_error(f"Error deleting SageMaker endpoint {resource['id']}", e)
            return False


class SageMakerModelService(BaseService):
    """SageMaker Model cleanup"""
    
    def __init__(self, region: str, dry_run: bool = False):
        super().__init__(region, dry_run)
        self.client = boto3.client('sagemaker', region_name=region)
    
    def get_service_name(self) -> str:
        return "SageMaker Models"
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List all SageMaker models"""
        resources = []
        try:
            paginator = self.client.get_paginator('list_models')
            for page in paginator.paginate():
                for model in page.get('Models', []):
                    resources.append({
                        'id': model['ModelName'],
                        'name': model['ModelName']
                    })
        except Exception as e:
            self.log_error("Error listing SageMaker models", e)
        return resources
    
    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a SageMaker model"""
        try:
            self.client.delete_model(ModelName=resource['id'])
            return True
        except Exception as e:
            self.log_error(f"Error deleting SageMaker model {resource['id']}", e)
            return False


class ComprehendService(BaseService):
    """Comprehend Entity Recognizer cleanup"""
    
    def __init__(self, region: str, dry_run: bool = False):
        super().__init__(region, dry_run)
        self.client = boto3.client('comprehend', region_name=region)
    
    def get_service_name(self) -> str:
        return "Comprehend Entity Recognizers"
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List all Comprehend entity recognizers"""
        resources = []
        try:
            paginator = self.client.get_paginator('list_entity_recognizers')
            for page in paginator.paginate():
                for recognizer in page.get('EntityRecognizerPropertiesList', []):
                    resources.append({
                        'id': recognizer['EntityRecognizerArn'],
                        'name': recognizer.get('LanguageCode', 'N/A'),
                        'status': recognizer.get('Status', 'N/A')
                    })
        except Exception as e:
            self.log_error("Error listing Comprehend entity recognizers", e)
        return resources
    
    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a Comprehend entity recognizer"""
        try:
            self.client.delete_entity_recognizer(EntityRecognizerArn=resource['id'])
            return True
        except Exception as e:
            self.log_error(f"Error deleting Comprehend entity recognizer {resource['id']}", e)
            return False


class RekognitionCollectionService(BaseService):
    """Rekognition Collection cleanup"""
    
    def __init__(self, region: str, dry_run: bool = False):
        super().__init__(region, dry_run)
        self.client = boto3.client('rekognition', region_name=region)
    
    def get_service_name(self) -> str:
        return "Rekognition Collections"
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List all Rekognition collections"""
        resources = []
        try:
            paginator = self.client.get_paginator('list_collections')
            for page in paginator.paginate():
                for collection_id in page.get('CollectionIds', []):
                    resources.append({
                        'id': collection_id,
                        'name': collection_id
                    })
        except Exception as e:
            self.log_error("Error listing Rekognition collections", e)
        return resources
    
    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a Rekognition collection"""
        try:
            self.client.delete_collection(CollectionId=resource['id'])
            return True
        except Exception as e:
            self.log_error(f"Error deleting Rekognition collection {resource['id']}", e)
            return False
