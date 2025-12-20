"""
Configuration management for AWS Nuker.

Handles region selection, resource filtering, and other configuration options.
"""

from dataclasses import dataclass, field
from typing import List, Set


# Comprehensive list of AWS regions
ALL_AWS_REGIONS = [
    "us-east-1", "us-east-2", "us-west-1", "us-west-2",
    "af-south-1",
    "ap-east-1", "ap-south-1", "ap-south-2", "ap-southeast-1",
    "ap-southeast-2", "ap-southeast-3", "ap-northeast-1",
    "ap-northeast-2", "ap-northeast-3",
    "ca-central-1",
    "eu-central-1", "eu-central-2", "eu-west-1", "eu-west-2",
    "eu-west-3", "eu-south-1", "eu-south-2", "eu-north-1",
    "me-south-1", "me-central-1",
    "sa-east-1",
]

# Comprehensive list of AWS services (A-Z) - Expanded to 100+ services
ALL_AWS_SERVICES = [
    "acm",                   # AWS Certificate Manager
    "apigateway",            # API Gateway
    "apigatewayv2",          # API Gateway V2
    "appflow",               # Amazon AppFlow
    "appmesh",               # AWS App Mesh
    "apprunner",             # AWS App Runner
    "appstream",             # Amazon AppStream 2.0
    "athena",                # Amazon Athena
    "autoscaling",           # AWS Auto Scaling
    "backup",                # AWS Backup
    "batch",                 # AWS Batch
    "chime",                 # Amazon Chime
    "cloud9",                # AWS Cloud9
    "cloudformation",        # AWS CloudFormation
    "cloudfront",            # Amazon CloudFront
    "cloudhsm",              # AWS CloudHSM
    "cloudmap",              # AWS Cloud Map
    "cloudsearch",           # Amazon CloudSearch
    "cloudtrail",            # AWS CloudTrail
    "cloudwatch",            # Amazon CloudWatch
    "codeartifact",          # AWS CodeArtifact
    "codebuild",             # AWS CodeBuild
    "codecommit",            # AWS CodeCommit
    "codedeploy",            # AWS CodeDeploy
    "codepipeline",          # AWS CodePipeline
    "cognito",               # Amazon Cognito
    "comprehend",            # Amazon Comprehend
    "config",                # AWS Config
    "connect",               # Amazon Connect
    "datasync",              # AWS DataSync
    "detective",             # Amazon Detective
    "directconnect",         # AWS Direct Connect
    "dms",                   # AWS Database Migration Service
    "docdb",                 # Amazon DocumentDB
    "dynamodb",              # Amazon DynamoDB
    "ec2",                   # Amazon EC2
    "ecr",                   # Amazon Elastic Container Registry
    "ecs",                   # Amazon Elastic Container Service
    "efs",                   # Amazon Elastic File System
    "eks",                   # Amazon Elastic Kubernetes Service
    "elasticache",           # Amazon ElastiCache
    "elasticbeanstalk",      # AWS Elastic Beanstalk
    "elastictranscoder",     # Amazon Elastic Transcoder
    "elb",                   # Elastic Load Balancing (Classic)
    "elbv2",                 # Elastic Load Balancing v2 (ALB/NLB)
    "emr",                   # Amazon EMR (Elastic MapReduce)
    "eventbridge",           # Amazon EventBridge
    "firehose",              # Amazon Data Firehose (Kinesis Firehose)
    "fms",                   # AWS Firewall Manager
    "forecast",              # Amazon Forecast
    "frauddetector",         # Amazon Fraud Detector
    "fsx",                   # Amazon FSx
    "glacier",               # Amazon S3 Glacier
    "globalaccelerator",     # AWS Global Accelerator
    "glue",                  # AWS Glue
    "guardduty",             # Amazon GuardDuty
    "iam",                   # AWS Identity and Access Management
    "imagebuilder",          # EC2 Image Builder
    "inspector",             # Amazon Inspector
    "iot",                   # AWS IoT Core
    "iotanalytics",          # AWS IoT Analytics
    "iotevents",             # AWS IoT Events
    "iotsitewise",           # AWS IoT SiteWise
    "ivs",                   # Amazon Interactive Video Service
    "kafka",                 # Amazon MSK (Managed Streaming for Apache Kafka)
    "kendra",                # Amazon Kendra
    "keyspaces",             # Amazon Keyspaces (for Apache Cassandra)
    "kinesis",               # Amazon Kinesis
    "kms",                   # AWS Key Management Service
    "lakeformation",         # AWS Lake Formation
    "lambda",                # AWS Lambda
    "lightsail",             # Amazon Lightsail
    "logs",                  # Amazon CloudWatch Logs
    "macie",                 # Amazon Macie
    "mediaconvert",          # AWS Elemental MediaConvert
    "medialive",             # AWS Elemental MediaLive
    "mediapackage",          # AWS Elemental MediaPackage
    "mediastore",            # AWS Elemental MediaStore
    "mediatailor",           # AWS Elemental MediaTailor
    "memorydb",              # Amazon MemoryDB for Redis
    "mq",                    # Amazon MQ
    "neptune",               # Amazon Neptune
    "opensearch",            # Amazon OpenSearch Service
    "opsworks",              # AWS OpsWorks
    "organizations",         # AWS Organizations
    "outposts",              # AWS Outposts
    "personalize",           # Amazon Personalize
    "pinpoint",              # Amazon Pinpoint
    "polly",                 # Amazon Polly
    "qldb",                  # Amazon QLDB
    "quicksight",            # Amazon QuickSight
    "ram",                   # AWS Resource Access Manager
    "rds",                   # Amazon Relational Database Service
    "redshift",              # Amazon Redshift
    "rekognition",           # Amazon Rekognition
    "route53",               # Amazon Route 53
    "s3",                    # Amazon Simple Storage Service
    "sagemaker",             # Amazon SageMaker
    "secretsmanager",        # AWS Secrets Manager
    "securityhub",           # AWS Security Hub
    "serverlessrepo",        # AWS Serverless Application Repository
    "servicecatalog",        # AWS Service Catalog
    "ses",                   # Amazon Simple Email Service
    "shield",                # AWS Shield
    "signer",                # AWS Signer
    "sns",                   # Amazon Simple Notification Service
    "sqs",                   # Amazon Simple Queue Service
    "ssm",                   # AWS Systems Manager
    "stepfunctions",         # AWS Step Functions
    "storagegateway",        # AWS Storage Gateway
    "sts",                   # AWS Security Token Service
    "swf",                   # Amazon Simple Workflow Service
    "textract",              # Amazon Textract
    "timestream",            # Amazon Timestream
    "transcribe",            # Amazon Transcribe
    "transfer",              # AWS Transfer Family
    "translate",             # Amazon Translate
    "waf",                   # AWS WAF (Web Application Firewall)
    "wafv2",                 # AWS WAF v2
    "workdocs",              # Amazon WorkDocs
    "workmail",              # Amazon WorkMail
    "workspaces",            # Amazon WorkSpaces
    "xray",                  # AWS X-Ray
]


@dataclass
class NukerConfig:
    """Configuration for AWS Nuker execution."""

    regions: List[str] = field(default_factory=list)
    services: Set[str] = field(default_factory=set)
    dry_run: bool = False
    force: bool = False
    exclude_default_resources: bool = True
    parallel_execution: bool = False
    max_workers: int = 5

    def __post_init__(self):
        """Validate configuration after initialization."""
        if not self.regions:
            self.regions = ["us-east-1"]  # Default region

        if not self.services:
            self.services = set(ALL_AWS_SERVICES)  # All services by default

    @staticmethod
    def parse_regions(region_input: str) -> List[str]:
        """
        Parse region input string.

        Supports:
        - Single region: "us-east-1"
        - Comma-separated: "us-east-1,us-west-2,eu-west-1"
        - Range: "us-east-1..us-west-2" (all regions in between alphabetically)
        - Wildcard: "us-*" or "*" for all regions

        Args:
            region_input: Region specification string

        Returns:
            List of region names
        """
        if not region_input or region_input.strip() == "":
            return ["us-east-1"]

        region_input = region_input.strip()

        # Handle wildcard for all regions
        if region_input == "*":
            return ALL_AWS_REGIONS

        # Handle prefix wildcard (e.g., "us-*")
        if "*" in region_input:
            prefix = region_input.replace("*", "")
            return [r for r in ALL_AWS_REGIONS if r.startswith(prefix)]

        # Handle range notation (e.g., "us-east-1..us-west-2")
        if ".." in region_input:
            parts = region_input.split("..")
            if len(parts) == 2:
                start_region = parts[0].strip()
                end_region = parts[1].strip()

                try:
                    start_idx = ALL_AWS_REGIONS.index(start_region)
                    end_idx = ALL_AWS_REGIONS.index(end_region)

                    if start_idx <= end_idx:
                        return ALL_AWS_REGIONS[start_idx:end_idx + 1]
                    else:
                        return ALL_AWS_REGIONS[end_idx:start_idx + 1]
                except ValueError:
                    # If region not found, fall through to comma-separated logic
                    pass

        # Handle comma-separated regions
        regions = [r.strip() for r in region_input.split(",")]

        # Validate regions
        valid_regions = []
        for region in regions:
            if region in ALL_AWS_REGIONS:
                valid_regions.append(region)
            else:
                # Invalid region will be logged but not added
                pass

        return valid_regions if valid_regions else ["us-east-1"]

    @staticmethod
    def parse_services(service_input: str) -> Set[str]:
        """
        Parse service input string.

        Supports:
        - Single service: "ec2"
        - Comma-separated: "ec2,s3,rds"
        - Wildcard: "*" for all services
        - Prefix: "cloud*" for all services starting with "cloud"

        Args:
            service_input: Service specification string

        Returns:
            Set of service names
        """
        if not service_input or service_input.strip() == "":
            return set(ALL_AWS_SERVICES)

        service_input = service_input.strip()

        # Handle wildcard for all services
        if service_input == "*":
            return set(ALL_AWS_SERVICES)

        # Handle prefix wildcard (e.g., "cloud*")
        if "*" in service_input:
            prefix = service_input.replace("*", "").lower()
            return {s for s in ALL_AWS_SERVICES if s.startswith(prefix)}

        # Handle comma-separated services
        services = [s.strip().lower() for s in service_input.split(",")]

        # Validate services
        valid_services = set()
        for service in services:
            if service in ALL_AWS_SERVICES:
                valid_services.add(service)

        return valid_services if valid_services else set(ALL_AWS_SERVICES)
