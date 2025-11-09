"""
AWS Nuker - Main CLI Interface
"""
import click
from colorama import init, Fore, Style
from typing import List
import sys

from .utils import parse_regions
from .services.ec2 import EC2Service, EBSService, EBSSnapshotService, AMIService, ElasticIPService, KeyPairService
from .services.vpc import VPCService, SecurityGroupService, SubnetService
from .services.s3 import S3Service
from .services.rds import RDSInstanceService, RDSClusterService, RDSSnapshotService
from .services.lambda_service import LambdaService, LambdaLayerService
from .services.iam import IAMUserService, IAMRoleService, IAMPolicyService, IAMGroupService
from .services.containers import ECSClusterService, ECSTaskDefinitionService, EKSClusterService
from .services.cloudformation import CloudFormationService
from .services.additional import (
    DynamoDBService, SNSService, SQSService, APIGatewayService, APIGatewayV2Service,
    ElastiCacheService, CloudWatchLogsService, Route53Service
)
from .services.extended import (
    ELBService, ELBv2Service, AutoScalingGroupService, LaunchTemplateService,
    SecretsManagerService, CloudWatchAlarmsService, ECRService, KinesisStreamService,
    BackupVaultService
)
from .services.analytics import (
    AthenaService, GlueService, GlueCrawlerService, EMRClusterService,
    DataPipelineService, RedshiftClusterService, OpenSearchDomainService
)
from .services.ml import (
    SageMakerNotebookService, SageMakerEndpointService, SageMakerModelService,
    ComprehendService, RekognitionCollectionService
)
from .services.compute import (
    BatchJobQueueService, BatchComputeEnvironmentService, ElasticBeanstalkService,
    AppRunnerService, LightsailInstanceService, Cloud9EnvironmentService
)
from .services.storage import (
    EFSFileSystemService, FSxFileSystemService, StorageGatewayService, GlacierVaultService
)
from .services.devtools import (
    CodeCommitRepositoryService, CodeBuildProjectService, CodeDeployApplicationService,
    CodePipelineService, CodeArtifactRepositoryService
)

# Initialize colorama
init(autoreset=True)

# All available services in alphabetical order
ALL_SERVICES = {
    'alb-nlb': ELBv2Service,
    'ami': AMIService,
    'apigateway': APIGatewayService,
    'apigatewayv2': APIGatewayV2Service,
    'app-runner': AppRunnerService,
    'athena': AthenaService,
    'autoscaling': AutoScalingGroupService,
    'backup-vaults': BackupVaultService,
    'batch-compute-envs': BatchComputeEnvironmentService,
    'batch-job-queues': BatchJobQueueService,
    'cloud9': Cloud9EnvironmentService,
    'cloudformation': CloudFormationService,
    'cloudwatch-alarms': CloudWatchAlarmsService,
    'cloudwatch-logs': CloudWatchLogsService,
    'codeartifact': CodeArtifactRepositoryService,
    'codebuild': CodeBuildProjectService,
    'codecommit': CodeCommitRepositoryService,
    'codedeploy': CodeDeployApplicationService,
    'codepipeline': CodePipelineService,
    'comprehend': ComprehendService,
    'data-pipeline': DataPipelineService,
    'dynamodb': DynamoDBService,
    'ebs': EBSService,
    'ebs-snapshots': EBSSnapshotService,
    'ec2': EC2Service,
    'ecr': ECRService,
    'ecs-clusters': ECSClusterService,
    'ecs-tasks': ECSTaskDefinitionService,
    'efs': EFSFileSystemService,
    'eks': EKSClusterService,
    'elasticache': ElastiCacheService,
    'elastic-beanstalk': ElasticBeanstalkService,
    'elastic-ips': ElasticIPService,
    'elb': ELBService,
    'emr': EMRClusterService,
    'fsx': FSxFileSystemService,
    'glacier-vaults': GlacierVaultService,
    'glue-crawlers': GlueCrawlerService,
    'glue-databases': GlueService,
    'iam-groups': IAMGroupService,
    'iam-policies': IAMPolicyService,
    'iam-roles': IAMRoleService,
    'iam-users': IAMUserService,
    'key-pairs': KeyPairService,
    'kinesis': KinesisStreamService,
    'lambda': LambdaService,
    'lambda-layers': LambdaLayerService,
    'launch-templates': LaunchTemplateService,
    'lightsail': LightsailInstanceService,
    'opensearch': OpenSearchDomainService,
    'rds-clusters': RDSClusterService,
    'rds-instances': RDSInstanceService,
    'rds-snapshots': RDSSnapshotService,
    'redshift': RedshiftClusterService,
    'rekognition': RekognitionCollectionService,
    'route53': Route53Service,
    's3': S3Service,
    'sagemaker-endpoints': SageMakerEndpointService,
    'sagemaker-models': SageMakerModelService,
    'sagemaker-notebooks': SageMakerNotebookService,
    'secrets-manager': SecretsManagerService,
    'security-groups': SecurityGroupService,
    'sns': SNSService,
    'sqs': SQSService,
    'storage-gateway': StorageGatewayService,
    'subnets': SubnetService,
    'vpcs': VPCService,
}


def print_banner():
    """Print AWS Nuker banner"""
    banner = f"""
{Fore.RED}{'='*80}
{Fore.RED}    ___    _       ______    _   ____  ____ __ ________ 
{Fore.RED}   /   |  | |     / / ___/   / | / / / / / //_// ____/ _ \\
{Fore.RED}  / /| |  | | /| / /\\__ \\   /  |/ / / / / ,<  / __/ / , _/
{Fore.RED} / ___ |  | |/ |/ /___/ /  / /|  / /_/ / /| |/ /___/ /| |  
{Fore.RED}/_/  |_|  |__/|__//____/  /_/ |_/\\____/_/ |_/_____/_/ |_|  
{Fore.RED}
{Fore.RED}AWS Resource Cleanup and Destroyer Tool
{Fore.RED}⚠️  WARNING: This tool will RUTHLESSLY DELETE AWS resources!
{Fore.RED}{'='*80}
{Style.RESET_ALL}"""
    print(banner)


@click.command()
@click.option(
    '--regions',
    '-r',
    default='all',
    help='AWS regions (single: us-east-1, multiple: us-east-1,us-west-2, or "all" for all regions)'
)
@click.option(
    '--services',
    '-s',
    default='all',
    help='Services to clean (comma-separated list or "all")'
)
@click.option(
    '--dry-run',
    '-d',
    is_flag=True,
    help='Dry run mode - show what would be deleted without actually deleting'
)
@click.option(
    '--list-services',
    '-l',
    is_flag=True,
    help='List all available services and exit'
)
@click.option(
    '--yes',
    '-y',
    is_flag=True,
    help='Skip confirmation prompt (DANGEROUS!)'
)
def main(regions, services, dry_run, list_services, yes):
    """
    AWS Nuker - Ruthlessly destroy AWS resources
    
    This tool will forcefully delete AWS resources in specified regions.
    Default resources (like default VPCs, subnets, security groups) are preserved.
    
    Examples:
    
        # List all available services
        aws-nuker --list-services
        
        # Dry run to see what would be deleted
        aws-nuker --regions us-east-1 --services ec2,s3 --dry-run
        
        # Delete all EC2 instances in us-east-1
        aws-nuker --regions us-east-1 --services ec2
        
        # Delete all resources in all regions (EXTREME CAUTION!)
        aws-nuker --regions all --services all
        
        # Delete specific services in multiple regions
        aws-nuker --regions us-east-1,us-west-2 --services ec2,rds-instances,s3
    """
    print_banner()
    
    # List services if requested
    if list_services:
        print(f"\n{Fore.CYAN}Available Services:{Style.RESET_ALL}\n")
        for i, service_name in enumerate(sorted(ALL_SERVICES.keys()), 1):
            print(f"  {i:2d}. {service_name}")
        print(f"\n{Fore.YELLOW}Use --services to specify which services to clean{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Use --services all to clean all services{Style.RESET_ALL}\n")
        return
    
    # Parse regions
    region_list = parse_regions(regions)
    if not region_list:
        print(f"{Fore.RED}Error: No regions found{Style.RESET_ALL}")
        sys.exit(1)
    
    # Parse services
    if services.lower() == 'all':
        service_list = list(ALL_SERVICES.keys())
    else:
        service_list = [s.strip() for s in services.split(',')]
        # Validate services
        invalid_services = [s for s in service_list if s not in ALL_SERVICES]
        if invalid_services:
            print(f"{Fore.RED}Error: Invalid services: {', '.join(invalid_services)}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Use --list-services to see all available services{Style.RESET_ALL}")
            sys.exit(1)
    
    # Show configuration
    # lgtm[py/clear-text-logging-sensitive-data]
    # Note: Logging region and service names for transparency - these are not secrets
    print(f"\n{Fore.CYAN}Configuration:{Style.RESET_ALL}")
    print(f"  Regions: {Fore.YELLOW}{', '.join(region_list)}{Style.RESET_ALL}")
    print(f"  Services: {Fore.YELLOW}{', '.join(service_list)}{Style.RESET_ALL}")
    print(f"  Dry Run: {Fore.YELLOW}{'Yes' if dry_run else 'No'}{Style.RESET_ALL}")
    
    # Confirmation prompt
    if not dry_run and not yes:
        print(f"\n{Fore.RED}{'='*80}{Style.RESET_ALL}")
        print(f"{Fore.RED}⚠️  WARNING: This will PERMANENTLY DELETE resources!{Style.RESET_ALL}")
        print(f"{Fore.RED}⚠️  Default VPCs and their resources will be preserved.{Style.RESET_ALL}")
        print(f"{Fore.RED}⚠️  All other resources will be RUTHLESSLY DESTROYED!{Style.RESET_ALL}")
        print(f"{Fore.RED}{'='*80}{Style.RESET_ALL}\n")
        
        confirmation = click.prompt(
            f"{Fore.YELLOW}Type 'DELETE' to confirm destruction{Style.RESET_ALL}",
            type=str
        )
        
        if confirmation != 'DELETE':
            print(f"\n{Fore.YELLOW}Operation cancelled{Style.RESET_ALL}")
            sys.exit(0)
    
    # Execute cleanup
    print(f"\n{Fore.GREEN}Starting AWS resource cleanup...{Style.RESET_ALL}\n")
    
    total_deleted = 0
    total_failed = 0
    total_skipped = 0
    
    for region in region_list:
        print(f"\n{Fore.MAGENTA}{'='*80}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}Processing Region: {region}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}{'='*80}{Style.RESET_ALL}")
        
        for service_name in service_list:
            service_class = ALL_SERVICES[service_name]
            
            try:
                service = service_class(region=region, dry_run=dry_run)
                result = service.cleanup()
                
                total_deleted += result['deleted']
                total_failed += result['failed']
                total_skipped += result['skipped']
                
            except Exception as e:
                # lgtm[py/clear-text-logging-sensitive-data]
                # Logging service name and region for debugging - not sensitive data
                error_type = type(e).__name__
                print(f"{Fore.RED}Error processing {service_name} in {region}: {error_type}{Style.RESET_ALL}")
                total_failed += 1
    
    # Final summary
    print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}FINAL SUMMARY{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
    print(f"  {Fore.GREEN}Total Deleted: {total_deleted}{Style.RESET_ALL}")
    print(f"  {Fore.RED}Total Failed: {total_failed}{Style.RESET_ALL}")
    print(f"  {Fore.YELLOW}Total Skipped: {total_skipped}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")
    
    if dry_run:
        print(f"{Fore.YELLOW}This was a DRY RUN - no resources were actually deleted{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Run without --dry-run to actually delete resources{Style.RESET_ALL}\n")
    else:
        print(f"{Fore.GREEN}AWS Nuker completed!{Style.RESET_ALL}\n")


if __name__ == '__main__':
    main()
