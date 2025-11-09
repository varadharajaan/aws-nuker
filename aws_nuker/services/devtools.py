"""
Developer Tools and CI/CD Services - CodeCommit, CodeBuild, CodeDeploy, CodePipeline, etc.
"""
import boto3
from typing import List, Dict, Any
from botocore.exceptions import ClientError
from .base import BaseService


class CodeCommitRepositoryService(BaseService):
    """CodeCommit Repository cleanup"""
    
    def __init__(self, region: str, dry_run: bool = False):
        super().__init__(region, dry_run)
        self.client = boto3.client('codecommit', region_name=region)
    
    def get_service_name(self) -> str:
        return "CodeCommit Repositories"
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List all CodeCommit repositories"""
        resources = []
        try:
            paginator = self.client.get_paginator('list_repositories')
            for page in paginator.paginate():
                for repo in page.get('repositories', []):
                    resources.append({
                        'id': repo['repositoryName'],
                        'name': repo['repositoryName']
                    })
        except Exception as e:
            self.log_error("Error listing CodeCommit repositories", e)
        return resources
    
    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a CodeCommit repository"""
        try:
            self.client.delete_repository(repositoryName=resource['id'])
            return True
        except Exception as e:
            self.log_error(f"Error deleting CodeCommit repository {resource['id']}", e)
            return False


class CodeBuildProjectService(BaseService):
    """CodeBuild Project cleanup"""
    
    def __init__(self, region: str, dry_run: bool = False):
        super().__init__(region, dry_run)
        self.client = boto3.client('codebuild', region_name=region)
    
    def get_service_name(self) -> str:
        return "CodeBuild Projects"
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List all CodeBuild projects"""
        resources = []
        try:
            paginator = self.client.get_paginator('list_projects')
            for page in paginator.paginate():
                for project_name in page.get('projects', []):
                    resources.append({
                        'id': project_name,
                        'name': project_name
                    })
        except Exception as e:
            self.log_error("Error listing CodeBuild projects", e)
        return resources
    
    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a CodeBuild project"""
        try:
            self.client.delete_project(name=resource['id'])
            return True
        except Exception as e:
            self.log_error(f"Error deleting CodeBuild project {resource['id']}", e)
            return False


class CodeDeployApplicationService(BaseService):
    """CodeDeploy Application cleanup"""
    
    def __init__(self, region: str, dry_run: bool = False):
        super().__init__(region, dry_run)
        self.client = boto3.client('codedeploy', region_name=region)
    
    def get_service_name(self) -> str:
        return "CodeDeploy Applications"
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List all CodeDeploy applications"""
        resources = []
        try:
            paginator = self.client.get_paginator('list_applications')
            for page in paginator.paginate():
                for app_name in page.get('applications', []):
                    resources.append({
                        'id': app_name,
                        'name': app_name
                    })
        except Exception as e:
            self.log_error("Error listing CodeDeploy applications", e)
        return resources
    
    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a CodeDeploy application"""
        try:
            self.client.delete_application(applicationName=resource['id'])
            return True
        except Exception as e:
            self.log_error(f"Error deleting CodeDeploy application {resource['id']}", e)
            return False


class CodePipelineService(BaseService):
    """CodePipeline cleanup"""
    
    def __init__(self, region: str, dry_run: bool = False):
        super().__init__(region, dry_run)
        self.client = boto3.client('codepipeline', region_name=region)
    
    def get_service_name(self) -> str:
        return "CodePipelines"
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List all CodePipelines"""
        resources = []
        try:
            paginator = self.client.get_paginator('list_pipelines')
            for page in paginator.paginate():
                for pipeline in page.get('pipelines', []):
                    resources.append({
                        'id': pipeline['name'],
                        'name': pipeline['name']
                    })
        except Exception as e:
            self.log_error("Error listing CodePipelines", e)
        return resources
    
    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a CodePipeline"""
        try:
            self.client.delete_pipeline(name=resource['id'])
            return True
        except Exception as e:
            self.log_error(f"Error deleting CodePipeline {resource['id']}", e)
            return False


class CodeArtifactRepositoryService(BaseService):
    """CodeArtifact Repository cleanup"""
    
    def __init__(self, region: str, dry_run: bool = False):
        super().__init__(region, dry_run)
        self.client = boto3.client('codeartifact', region_name=region)
    
    def get_service_name(self) -> str:
        return "CodeArtifact Repositories"
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List all CodeArtifact repositories"""
        resources = []
        try:
            paginator = self.client.get_paginator('list_repositories')
            for page in paginator.paginate():
                for repo in page.get('repositories', []):
                    resources.append({
                        'id': f"{repo['domainName']}:{repo['name']}",
                        'name': repo['name'],
                        'domain': repo['domainName']
                    })
        except Exception as e:
            self.log_error("Error listing CodeArtifact repositories", e)
        return resources
    
    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a CodeArtifact repository"""
        try:
            domain, repo = resource['id'].split(':')
            self.client.delete_repository(
                domain=domain,
                repository=repo
            )
            return True
        except Exception as e:
            self.log_error(f"Error deleting CodeArtifact repository {resource['id']}", e)
            return False
