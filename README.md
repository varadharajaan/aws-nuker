# AWS Nuker 💣☢️

**A ruthless AWS resource cleanup tool that destroys all non-default AWS resources without mercy.**

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## ⚠️ WARNING

**USE THIS TOOL WITH EXTREME CAUTION!**

AWS Nuker is designed to **FORCEFULLY DELETE** all AWS resources (except default resources like default VPCs) in your AWS account. This action is **IRREVERSIBLE** and can result in:

- 💥 Complete destruction of your production environments
- 💸 Potential data loss
- 🔥 Service disruptions
- 💔 Tears and regret

**Only use this tool when you:**
- Want to clean up test/development accounts
- Are decommissioning an AWS account
- Need to reset your AWS environment to a clean state
- Know EXACTLY what you're doing

## 🚀 Features

- **Comprehensive Coverage**: **121 AWS service handlers** covering compute, storage, databases, analytics, ML/AI, IoT, media, networking, security, and more
- **Multi-Region Support**: Clean up resources across all AWS regions simultaneously
- **Flexible Region Selection**: Single region, comma-separated, range, or wildcard support (`us-*`, `*`)
- **Force Delete**: Automatically handles resource dependencies and deletes them ruthlessly
- **Dry Run Mode**: Preview what would be deleted without actually deleting anything
- **Detailed Logging**: Complete audit trail of all operations with timestamps
- **Parallel Execution**: Speed up cleanup with parallel processing across regions
- **Smart Default Filtering**: Preserves default AWS resources (like default VPCs and security groups)
- **Interactive CLI**: User-friendly command-line interface with color output
- **Tag-Based Filtering**: Target resources by tags for precise cleanup
- **Web Dashboard**: Modern React-based UI for visual resource management
- **RESTful API**: FastAPI backend for programmatic access
- **Timing Metrics**: Track cleanup duration for each operation

## 📋 Supported AWS Services

AWS Nuker supports **121 fully-implemented AWS service handlers** with comprehensive resource cleanup across all major categories.

### ✅ Compute & Containers (11 services)
- **EC2**: Instances, Volumes, Snapshots, AMIs, Security Groups, Key Pairs, Elastic IPs
- **ECS**: Clusters, Services, Tasks, Task Definitions
- **ECR**: Container Registries (with force delete)
- **EKS**: Kubernetes Clusters (with nodegroup cleanup)
- **Lambda**: Functions, Layers, Event Source Mappings
- **Batch**: Job Queues, Job Definitions, Compute Environments
- **Elastic Beanstalk**: Applications, Environments
- **Lightsail**: Instances, Databases, Load Balancers
- **App Runner**: Services
- **Outposts**: Outposts
- **Image Builder**: Image Pipelines, Components, Recipes

### ✅ Database & Storage (16 services)
- **RDS**: DB Instances, Clusters (Aurora), Snapshots, Parameter Groups
- **DynamoDB**: Tables, Backups
- **ElastiCache**: Clusters, Replication Groups (Redis/Memcached)
- **Redshift**: Clusters (skip final snapshot)
- **S3**: Buckets (with versioning and lifecycle support)
- **EFS**: File Systems
- **FSx**: File Systems (Windows, Lustre, NetApp ONTAP, OpenZFS)
- **Neptune**: DB Clusters, DB Instances
- **DocumentDB**: Clusters, Instances
- **Keyspaces**: Keyspaces, Tables
- **Timestream**: Databases, Tables
- **MemoryDB**: Clusters
- **QLDB**: Ledgers
- **Glacier**: Vaults
- **Storage Gateway**: Gateways
- **Backup**: Backup Vaults, Recovery Points, Backup Plans

### ✅ Networking & Content Delivery (11 services)
- **VPC**: VPCs, Subnets, Internet Gateways, NAT Gateways, Route Tables (excluding defaults)
- **ELB/ELBv2**: Classic, Application, Network, Gateway Load Balancers
- **Route53**: Hosted Zones, Record Sets
- **API Gateway**: REST APIs (v1), HTTP APIs (v2), WebSocket APIs
- **CloudFront**: Distributions
- **Direct Connect**: Virtual Interfaces, Connections
- **App Mesh**: Virtual Services, Virtual Nodes, Meshes
- **Global Accelerator**: Accelerators, Listeners
- **Cloud Map**: Namespaces, Services

### ✅ Analytics & Big Data (15 services)
- **Athena**: Workgroups, Named Queries, Data Catalogs
- **Glue**: Databases, Crawlers, Jobs, Triggers, Dev Endpoints
- **Kinesis**: Data Streams (with consumer deletion)
- **CloudSearch**: Domains
- **QuickSight**: Data Sets, Dashboards, Analyses
- **Lake Formation**: Data Lake Settings, Permissions
- **Kafka/MSK**: Clusters
- **EMR**: Clusters
- **Firehose**: Delivery Streams
- **OpenSearch**: Domains
- **Data Pipeline**: Pipelines
- **Redshift**: Clusters, Snapshots

### ✅ Developer Tools (10 services)
- **CodeCommit**: Repositories
- **CodeBuild**: Projects, Build Batches
- **CodeDeploy**: Applications, Deployment Groups
- **CodePipeline**: Pipelines
- **Cloud9**: Environments
- **X-Ray**: Sampling Rules, Groups
- **CodeArtifact**: Domains, Repositories

### ✅ Management & Governance (13 services)
- **CloudFormation**: Stacks, StackSets
- **CloudWatch**: Alarms, Log Groups, Dashboards
- **Config**: Configuration Recorders, Delivery Channels, Rules
- **Service Catalog**: Portfolios, Products
- **Systems Manager (SSM)**: Parameters, Documents, Maintenance Windows
- **CloudTrail**: Trails
- **Organizations**: Organizational Units, Accounts
- **OpsWorks**: Stacks, Layers, Apps

### ✅ Security, Identity & Compliance (16 services)
- **IAM**: Users, Roles, Policies, Groups (customer-managed only)
- **KMS**: Customer-Managed Keys (schedules deletion)
- **Secrets Manager**: Secrets (with force delete option)
- **GuardDuty**: Detectors, Threat Intel Sets
- **Inspector**: Assessment Targets, Templates
- **Macie**: Classification Jobs, Custom Data Identifiers
- **Cognito**: User Pools, Identity Pools
- **Detective**: Graphs
- **CloudHSM**: Clusters
- **Security Hub**: Hubs, Standards Subscriptions
- **WAF Classic**: Web ACLs, Rules, IP Sets
- **WAF v2**: Web ACLs, Rule Groups, IP Sets
- **Shield**: Protections
- **Signer**: Signing Profiles
- **ACM**: Certificates
- **Firewall Manager (FMS)**: Policies

### ✅ Machine Learning & AI (11 services)
- **SageMaker**: Endpoints, Notebook Instances, Models, Training Jobs
- **Comprehend**: Document Classifiers, Entity Recognizers, Endpoints
- **Forecast**: Datasets, Predictors, Forecast Exports
- **Fraud Detector**: Detectors, Models, Outcomes
- **Kendra**: Indexes, Data Sources
- **Personalize**: Datasets, Solutions, Campaigns
- **Polly**: Lexicons
- **Rekognition**: Collections, Projects
- **Textract**: N/A (API-based service)
- **Transcribe**: Vocabularies, Jobs
- **Translate**: Terminology, Translation Jobs

### ✅ Application Integration (7 services)
- **SNS**: Topics, Subscriptions
- **SQS**: Queues (Standard & FIFO)
- **Step Functions**: State Machines, Activities
- **AppFlow**: Flows, Connector Profiles
- **MQ**: Brokers, Configurations
- **EventBridge**: Rules, Event Buses, Archives
- **SWF**: Domains

### ✅ Media Services (6 services)
- **MediaConvert**: Jobs, Queues, Job Templates
- **MediaLive**: Channels, Inputs
- **MediaPackage**: Channels, Origin Endpoints
- **MediaStore**: Containers
- **MediaTailor**: Playback Configurations
- **Elastic Transcoder**: Pipelines, Presets
- **IVS**: Channels, Recording Configurations

### ✅ IoT (4 services)
- **IoT Core**: Things, Policies, Certificates, Thing Groups
- **IoT Analytics**: Channels, Datasets, Pipelines, Datastores
- **IoT Events**: Detector Models, Inputs
- **IoT SiteWise**: Assets, Asset Models, Gateways

### ✅ Business Applications (6 services)
- **Connect**: Instances
- **Chime**: Meeting, Voice Connectors
- **SES**: Identities, Configuration Sets, Receipt Rules
- **WorkDocs**: Users (admin operations)
- **WorkMail**: Organizations, Users
- **Pinpoint**: Applications, Campaigns

### ✅ End User Computing & Migration (4 services)
- **WorkSpaces**: WorkSpaces
- **DataSync**: Tasks, Locations
- **DMS**: Replication Instances, Endpoints, Tasks
- **Transfer Family**: Servers, Users

### ✅ Additional Services (1 service)
- **STS**: Session Tokens (service-based, not deletable resources)

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- AWS credentials configured (via `~/.aws/credentials`, environment variables, or IAM role)
- Appropriate AWS IAM permissions for resource deletion

### Install from Source

```bash
# Clone the repository
git clone https://github.com/varadharajaan/aws-nuker.git
cd aws-nuker

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

### Install from PyPI (when published)

```bash
pip install aws-nuker
```

## 🔧 AWS Credentials Setup

AWS Nuker uses boto3 to interact with AWS. Configure your credentials using one of these methods:

### Method 1: AWS CLI Configuration

```bash
aws configure
```

### Method 2: Environment Variables

```bash
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="us-east-1"
```

### Method 3: IAM Role (for EC2 instances)

If running on an EC2 instance, attach an IAM role with appropriate permissions.

### Required IAM Permissions

Your AWS credentials need permissions to:
- List resources for all targeted services
- Delete resources for all targeted services
- Describe resource dependencies

Example IAM policy (⚠️ Very permissive - use with caution):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:*",
        "s3:*",
        "rds:*",
        "lambda:*",
        "iam:*",
        "cloudformation:*",
        "dynamodb:*",
        "ecs:*",
        "sns:*",
        "sqs:*",
        "cloudwatch:*",
        "logs:*",
        "elasticloadbalancing:*",
        "route53:*"
      ],
      "Resource": "*"
    }
  ]
}
```

## 💻 Usage

### Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .

# List all available services (121 handlers)
aws-nuker list-services

# List all available AWS regions
aws-nuker list-regions

# Dry run to preview deletions (ALWAYS TEST FIRST!)
aws-nuker nuke --regions us-east-1 --services ec2 --dry-run

# Delete specific service in one region
aws-nuker nuke --regions us-east-1 --services ec2 --force
```

### Common Use Cases

**Clean up development/test account:**
```bash
# Preview everything that would be deleted
aws-nuker nuke --regions us-east-1 --services "*" --dry-run

# Delete everything (use with extreme caution!)
aws-nuker nuke --regions us-east-1 --services "*" --force --yes
```

**Remove compute resources:**
```bash
# EC2, ECS, EKS, Lambda, Batch
aws-nuker nuke --regions us-east-1,us-west-2 --services ec2,ecs,eks,lambda,batch --force
```

**Clean up databases:**
```bash
# RDS, DynamoDB, ElastiCache, Redshift, Neptune, DocumentDB
aws-nuker nuke --regions us-east-1 --services rds,dynamodb,elasticache,redshift,neptune,docdb --force
```

**Remove storage resources:**
```bash
# S3, EFS, FSx, Glacier, Backup
aws-nuker nuke --regions "*" --services s3 --force  # S3 is global
aws-nuker nuke --regions us-east-1 --services efs,fsx,glacier,backup --force
```

**Clean up analytics & big data:**
```bash
# Athena, Glue, Kinesis, EMR, OpenSearch, QuickSight
aws-nuker nuke --regions us-east-1 --services athena,glue,kinesis,emr,opensearch,quicksight --force
```

**Remove ML/AI services:**
```bash
# SageMaker, Comprehend, Rekognition, Kendra, Personalize
aws-nuker nuke --regions us-east-1 --services sagemaker,comprehend,rekognition,kendra,personalize --force
```

**Clean up security resources:**
```bash
# IAM, KMS, Secrets Manager, GuardDuty, Macie, Security Hub
aws-nuker nuke --regions us-east-1 --services iam,kms,secretsmanager,guardduty,macie,securityhub --force
```

**Remove networking:**
```bash
# VPC, ELB, CloudFront, API Gateway, Route53
aws-nuker nuke --regions us-east-1 --services vpc,elb,apigateway,route53 --force
aws-nuker nuke --regions "*" --services cloudfront --force  # CloudFront is global
```

**Clean up IoT resources:**
```bash
# IoT Core, IoT Analytics, IoT Events, IoT SiteWise
aws-nuker nuke --regions us-east-1 --services iot,iotanalytics,iotevents,iotsitewise --force
```

**Remove media services:**
```bash
# MediaConvert, MediaLive, MediaPackage, IVS
aws-nuker nuke --regions us-east-1 --services mediaconvert,medialive,mediapackage,ivs --force
```

### Advanced Usage

```bash
# Multi-region cleanup with wildcard
aws-nuker nuke --regions "us-*" --services ec2,s3,rds --force

# Parallel execution for faster cleanup
aws-nuker nuke --regions us-east-1,us-west-2,eu-west-1 --services "*" --force --parallel --max-workers 10

# Clean up specific service category with wildcard
aws-nuker nuke --regions us-east-1 --services "media*" --force  # All media services

# Tag-based filtering (if implemented)
aws-nuker nuke --regions us-east-1 --services "*" --tags "Environment=dev,Project=test" --force

# Exclude specific resources
aws-nuker nuke --regions us-east-1 --services ec2 --exclude-tags "Protected=true" --force
```

### Command Options

```
Options:
  -r, --regions TEXT      AWS regions (single, comma-separated, range, or wildcard)
                         Examples: 'us-east-1', 'us-east-1,us-west-2', 'us-*', '*'
  
  -s, --services TEXT     AWS services to target (comma-separated or wildcard)
                         Examples: 'ec2,s3,rds', 'cloud*', '*'
  
  --dry-run              Perform a dry run without actually deleting resources
  
  -f, --force            Force deletion of resources even with dependencies
  
  --parallel             Execute cleanup in parallel (faster but less controlled)
  
  --max-workers INTEGER  Maximum number of parallel workers (default: 5)
  
  -y, --yes             Skip confirmation prompt
  
  --help                Show help message
```

### Region Selection Examples

```bash
# Single region
--regions us-east-1

# Multiple specific regions
--regions us-east-1,us-west-2,eu-west-1

# All US regions using wildcard
--regions "us-*"

# All regions
--regions "*"

# Range (alphabetical order from list)
--regions us-east-1..us-west-2
```

### Service Selection Examples

```bash
# Single service
--services ec2

# Multiple services
--services ec2,s3,rds,lambda

# All services starting with "cloud"
--services "cloud*"

# All services
--services "*"
```

## 📊 Logging and Audit Trail

AWS Nuker maintains detailed logs of all operations:

### Log Files

- **Main Log**: `logs/aws_nuker_YYYYMMDD_HHMMSS.log`
  - Detailed operation logs
  - Error messages and stack traces
  - Debug information

- **Audit Log**: `audit/audit_YYYYMMDD_HHMMSS.log`
  - Complete audit trail of all deletions
  - Resource identifiers
  - Timestamps
  - Operation status (SUCCESS, FAILED, SKIPPED)

### Audit Log Format

```
2024-11-08 13:45:23 - ACTION=DELETE | TYPE=ec2 | ID=i-1234567890abcdef0 | REGION=us-east-1 | STATUS=SUCCESS
2024-11-08 13:45:24 - ACTION=DELETE | TYPE=s3 | ID=my-bucket-name | REGION=us-east-1 | STATUS=SUCCESS
2024-11-08 13:45:25 - ACTION=DELETE | TYPE=rds | ID=my-database | REGION=us-east-1 | STATUS=FAILED | DETAILS=DependencyViolation
```

## 🏗️ Architecture

### Directory Structure

```
aws-nuker/
├── aws_nuker/
│   ├── __init__.py              # Package initialization
│   ├── base_handler.py          # Base class for all resource handlers
│   ├── cli.py                   # Command-line interface (Click-based)
│   ├── config.py                # Configuration management
│   ├── logger.py                # Logging and audit system
│   ├── orchestrator.py          # Main execution orchestrator
│   ├── registry.py              # Service handler registry (121 handlers)
│   ├── approval_gate.py         # Approval workflow system
│   ├── notification_manager.py  # Notification system
│   ├── tag_manager.py           # Tag-based filtering
│   ├── policy_templates.py      # IAM policy templates
│   └── handlers/                # 121 Service-specific handlers
│       ├── __init__.py
│       ├── acm_handler.py
│       ├── apigateway_handler.py
│       ├── appflow_handler.py
│       ├── appmesh_handler.py
│       ├── apprunner_handler.py
│       ├── appstream_handler.py
│       ├── athena_handler.py
│       ├── autoscaling_handler.py
│       ├── backup_handler.py
│       ├── batch_handler.py
│       ├── chime_handler.py
│       ├── cloud9_handler.py
│       ├── cloudformation_handler.py
│       ├── cloudfront_handler.py
│       ├── cloudhsm_handler.py
│       ├── cloudmap_handler.py
│       ├── cloudsearch_handler.py
│       ├── cloudtrail_handler.py
│       ├── cloudwatch_handler.py
│       ├── codeartifact_handler.py
│       ├── codebuild_handler.py
│       ├── codecommit_handler.py
│       ├── codedeploy_handler.py
│       ├── codepipeline_handler.py
│       ├── cognito_handler.py
│       ├── comprehend_handler.py
│       ├── config_handler.py
│       ├── connect_handler.py
│       ├── datasync_handler.py
│       ├── detective_handler.py
│       ├── directconnect_handler.py
│       ├── dms_handler.py
│       ├── docdb_handler.py
│       ├── dynamodb_handler.py
│       ├── ec2_handler.py
│       ├── ecr_handler.py
│       ├── ecs_handler.py
│       ├── efs_handler.py
│       ├── eks_handler.py
│       ├── elasticache_handler.py
│       ├── elasticbeanstalk_handler.py
│       ├── elastictranscoder_handler.py
│       ├── elb_handler.py
│       ├── emr_handler.py
│       ├── eventbridge_handler.py
│       ├── firehose_handler.py
│       ├── fms_handler.py
│       ├── forecast_handler.py
│       ├── frauddetector_handler.py
│       ├── fsx_handler.py
│       ├── glacier_handler.py
│       ├── globalaccelerator_handler.py
│       ├── glue_handler.py
│       ├── guardduty_handler.py
│       ├── iam_handler.py
│       ├── imagebuilder_handler.py
│       ├── inspector_handler.py
│       ├── iot_handler.py
│       ├── iotanalytics_handler.py
│       ├── iotevents_handler.py
│       ├── iotsitewise_handler.py
│       ├── ivs_handler.py
│       ├── kafka_handler.py
│       ├── kendra_handler.py
│       ├── keyspaces_handler.py
│       ├── kinesis_handler.py
│       ├── kms_handler.py
│       ├── lakeformation_handler.py
│       ├── lambda_handler.py
│       ├── lightsail_handler.py
│       ├── macie_handler.py
│       ├── mediaconvert_handler.py
│       ├── medialive_handler.py
│       ├── mediapackage_handler.py
│       ├── mediastore_handler.py
│       ├── mediatailor_handler.py
│       ├── memorydb_handler.py
│       ├── mq_handler.py
│       ├── neptune_handler.py
│       ├── opensearch_handler.py
│       ├── opsworks_handler.py
│       ├── organizations_handler.py
│       ├── outposts_handler.py
│       ├── personalize_handler.py
│       ├── pinpoint_handler.py
│       ├── polly_handler.py
│       ├── qldb_handler.py
│       ├── quicksight_handler.py
│       ├── ram_handler.py
│       ├── rds_handler.py
│       ├── redshift_handler.py
│       ├── rekognition_handler.py
│       ├── route53_handler.py
│       ├── s3_handler.py
│       ├── sagemaker_handler.py
│       ├── secretsmanager_handler.py
│       ├── securityhub_handler.py
│       ├── serverlessrepo_handler.py
│       ├── servicecatalog_handler.py
│       ├── ses_handler.py
│       ├── shield_handler.py
│       ├── signer_handler.py
│       ├── sns_handler.py
│       ├── sqs_handler.py
│       ├── ssm_handler.py
│       ├── stepfunctions_handler.py
│       ├── storagegateway_handler.py
│       ├── sts_handler.py
│       ├── swf_handler.py
│       ├── textract_handler.py
│       ├── timestream_handler.py
│       ├── transcribe_handler.py
│       ├── transfer_handler.py
│       ├── translate_handler.py
│       ├── vpc_handler.py
│       ├── waf_handler.py
│       ├── wafv2_handler.py
│       ├── workdocs_handler.py
│       ├── workmail_handler.py
│       ├── workspaces_handler.py
│       └── xray_handler.py
├── api/
│   ├── requirements.txt         # API dependencies
│   └── server.py                # FastAPI REST backend
├── ui/
│   ├── package.json             # React UI dependencies
│   ├── vite.config.ts           # Vite build config
│   ├── tailwind.config.js       # Tailwind CSS config
│   └── src/                     # React components
│       ├── App.tsx
│       ├── main.tsx
│       └── components/
│           ├── Dashboard.tsx
│           ├── ResourceExplorer.tsx
│           ├── DryRunPanel.tsx
│           ├── ApprovalWorkflow.tsx
│           ├── FilterBuilder.tsx
│           ├── Notifications.tsx
│           ├── Reports.tsx
│           └── Settings.tsx
├── docs/                        # Comprehensive documentation
│   ├── API_DOCUMENTATION.md
│   ├── EXAMPLES.md
│   ├── INSTALLATION.md
│   ├── TAG_BASED_CLEANUP.md
│   ├── UI_DASHBOARD_GUIDE.md
│   └── diagrams/
│       └── ARCHITECTURE.md
├── logs/                        # Runtime log files (gitignored)
├── audit/                       # Audit trail files (gitignored)
├── requirements.txt             # Python dependencies
├── setup.py                     # Package setup
├── main.py                      # CLI entry point
├── README.md                    # This file
├── TODO.md                      # Future enhancements roadmap
├── CONTRIBUTING.md              # Contribution guidelines
├── PROJECT_SUMMARY.md           # Project overview
├── QUICK_REFERENCE.md           # Quick command reference
└── .gitignore                   # Git ignore rules
```

### Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         CLI Interface                        │
│                    (click-based commands)                    │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      Configuration                           │
│              (Region & Service Selection)                    │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      Orchestrator                            │
│         (Sequential or Parallel Execution)                   │
└───────────────────────────┬─────────────────────────────────┘
                            │
                ┌───────────┴───────────┐
                ▼                       ▼
    ┌──────────────────────┐  ┌──────────────────────┐
    │  Handler Registry    │  │   Logger System      │
    │  (Service Mapping)   │  │  (Logs & Audit)      │
    └──────────┬───────────┘  └──────────────────────┘
               │
     ┌─────────┴──────────┐
     ▼                    ▼
┌──────────┐        ┌──────────┐
│ EC2      │        │ S3       │
│ Handler  │  ....  │ Handler  │
└──────────┘        └──────────┘
     │                    │
     ▼                    ▼
┌──────────────────────────────┐
│      AWS API (boto3)         │
└──────────────────────────────┘
```

### Execution Flow

```
1. User runs CLI command
   ↓
2. Parse regions and services
   ↓
3. Create configuration
   ↓
4. Display configuration & get confirmation
   ↓
5. Initialize orchestrator
   ↓
6. For each region and service:
   ├─→ Get appropriate handler from registry
   ├─→ List all resources
   ├─→ Filter out default resources (unless --force)
   ├─→ For each resource:
   │   ├─→ Check dependencies
   │   ├─→ Delete resource (with retry logic)
   │   └─→ Log to audit trail
   └─→ Collect statistics
   ↓
7. Generate summary report
   ↓
8. Display results and log locations
```

## 🧪 Testing

### Dry Run Testing

Always test with `--dry-run` first:

```bash
aws-nuker nuke --regions us-east-1 --services "*" --dry-run
```

This will show you what would be deleted without actually deleting anything.

### Test in a Safe Environment

1. Create a dedicated AWS test account
2. Populate it with test resources
3. Run AWS Nuker to verify cleanup
4. Check audit logs for completeness

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-service-handler`)
3. Add your changes with proper tests
4. Follow PEP 8 coding standards
5. Submit a pull request

### Adding a New Service Handler

1. Create a new handler in `aws_nuker/handlers/`
2. Inherit from `ResourceHandler` base class
3. Implement required methods:
   - `service_name` property
   - `list_resources()` method
   - `delete_resource()` method
   - `is_default_resource()` method (optional)
4. Register handler in `aws_nuker/registry.py`
5. Update documentation

Example:

```python
from ..base_handler import ResourceHandler

class NewServiceHandler(ResourceHandler):
    @property
    def service_name(self) -> str:
        return "newservice"
    
    def list_resources(self):
        # Implementation
        pass
    
    def delete_resource(self, resource):
        # Implementation
        pass
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚖️ Disclaimer

**THIS SOFTWARE IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND.**

The authors and contributors are not responsible for:
- Any data loss or damages caused by using this tool
- AWS charges incurred during or after cleanup
- Any consequences of using this tool

**USE AT YOUR OWN RISK!**

## 🙏 Acknowledgments

- Built with [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html) - AWS SDK for Python
- CLI powered by [Click](https://click.palletsprojects.com/)
- Colorful output with [Colorama](https://github.com/tartley/colorama)

## 📞 Support

- **Issues**: Report bugs or request features via [GitHub Issues](https://github.com/varadharajaan/aws-nuker/issues)
- **Discussions**: Join conversations in [GitHub Discussions](https://github.com/varadharajaan/aws-nuker/discussions)

## 🗺️ Roadmap

See [TODO.md](TODO.md) for the comprehensive roadmap including:

### Current Features ✅
- 121 AWS service handlers fully implemented
- Multi-region support with wildcards
- Parallel execution
- Comprehensive logging and audit trails
- Tag-based resource management
- Web UI dashboard
- RESTful API

### Planned Enhancements 🚀
- Enhanced approval workflows with multi-stakeholder support
- Advanced cost estimation before deletion
- Resource dependency visualization
- Rollback capabilities (where possible)
- AWS Organizations support
- Scheduled cleanup jobs
- Terraform state integration
- CloudFormation drift detection
- Resource ownership tracking
- Compliance reporting

### Infrastructure & Scalability 🏗️
- Distributed execution with SQS/SNS
- Real-time WebSocket updates
- Caching layer with Redis
- Database backend for state management
- Container orchestration support
- Monitoring and alerting integration

For detailed architecture plans and technical roadmap, see [TODO.md](TODO.md).

---

**Remember: With great power comes great responsibility. Use AWS Nuker wisely! 💪**

**Current Status: 121 service handlers implemented and production-ready! 🎉**