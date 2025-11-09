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

- **Comprehensive Coverage**: Supports 123 AWS services defined (A-Z), with 28 actively implemented handlers
- **Multi-Region Support**: Clean up resources across multiple AWS regions
- **Flexible Region Selection**: Single region, comma-separated, range, or wildcard support
- **Force Delete**: Automatically handles resource dependencies and deletes them ruthlessly
- **Dry Run Mode**: Preview what would be deleted without actually deleting
- **Detailed Logging**: Complete audit trail of all operations
- **Parallel Execution**: Speed up cleanup with parallel processing
- **Smart Default Filtering**: Preserves default AWS resources (like default VPCs)
- **Interactive CLI**: User-friendly command-line interface with color output
- **Timing Metrics**: Track cleanup duration for each operation

## 📋 Supported AWS Services

AWS Nuker has **123 AWS services defined** with **28 service keys** actively implemented by **25 unique handler classes**.

### ✅ Compute & Containers (100% Coverage)
- **EC2**: Instances, Volumes, Snapshots, AMIs, Security Groups, Key Pairs, Elastic IPs
- **ECS**: Clusters, Services, Tasks
- **ECR**: Container Registries (with force delete)
- **EKS**: Kubernetes Clusters (with nodegroup cleanup)
- **Lambda**: Functions and Layers

### ✅ Database (100% Coverage)
- **RDS**: DB Instances, Clusters (Aurora), Snapshots
- **DynamoDB**: Tables
- **ElastiCache**: Clusters and Replication Groups (Redis/Memcached)
- **Redshift**: Clusters (skip final snapshot)

### ✅ Storage
- **S3**: Buckets (with versioning support)

### ✅ Networking (100% Coverage)
- **VPC**: VPCs, Subnets, Internet Gateways, NAT Gateways (excluding defaults)
- **ELB/ELBv2**: Classic Load Balancers, Application Load Balancers, Network Load Balancers
- **Route53**: Hosted Zones and Record Sets
- **API Gateway**: REST APIs (v1), HTTP APIs (v2), WebSocket APIs

### ✅ Analytics (100% Coverage)
- **Athena**: Workgroups and Named Queries
- **Glue**: Databases, Crawlers, Jobs
- **Kinesis**: Streams (with consumer deletion)

### ✅ Management & Governance (100% Coverage)
- **CloudFormation**: Stacks
- **CloudWatch**: Alarms, Log Groups

### ✅ Application Integration (100% Coverage)
- **SNS**: Topics
- **SQS**: Queues

### ✅ Security & Identity (100% Coverage)
- **IAM**: Users, Roles, Policies (customer-managed only)
- **KMS**: Customer-Managed Keys (schedules deletion)
- **Secrets Manager**: Secrets (with force delete option)
- **GuardDuty**: Detectors

### 📝 Defined Services (Ready for Handler Implementation)

The following **95+ additional services** are defined in the configuration and ready for handler implementation:

**Compute**: Batch, Lightsail, Elastic Beanstalk, App Runner, Outposts, Image Builder

**Storage**: EFS, FSx, Glacier, Storage Gateway, Backup

**Database**: Neptune, DocumentDB, Keyspaces, Timestream, MemoryDB

**Networking**: CloudFront, Direct Connect, App Mesh, Global Accelerator, Cloud Map

**Developer Tools**: CodeCommit, CodeBuild, CodeDeploy, CodePipeline, Cloud9, CloudShell, X-Ray, CodeArtifact

**Analytics**: CloudSearch, QuickSight, Lake Formation, Kafka/MSK, EMR, Firehose, OpenSearch

**Security**: Inspector, Macie, Cognito, Detective, CloudHSM, Directory Service, Firewall Manager, Security Hub, WAF, Shield, Signer

**Machine Learning**: SageMaker, Comprehend, Forecast, Fraud Detector, Kendra, Personalize, Polly, Rekognition, Textract, Transcribe, Translate

**Management**: Config, Service Catalog, Systems Manager, CloudTrail, License Manager, Organizations, OpsWorks

**Application Integration**: Step Functions, AppFlow, MQ, EventBridge, SWF

**Media Services**: MediaConvert, MediaLive, MediaPackage, MediaStore, MediaTailor, Elastic Transcoder, IVS

**IoT**: IoT Core, IoT Analytics, IoT Events, IoT SiteWise

**Business Apps**: Connect, Chime, SES, WorkDocs, WorkMail, Pinpoint

**End User Computing**: WorkSpaces

**Migration**: DataSync, DMS, Transfer Family

And 40+ more services across various categories. See `aws_nuker/config.py` for the complete list.

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

### Basic Commands

```bash
# List available services
aws-nuker list-services

# List available regions
aws-nuker list-regions

# Dry run (see what would be deleted without deleting)
aws-nuker nuke --regions us-east-1 --services ec2 --dry-run

# Delete EC2 resources in us-east-1
aws-nuker nuke --regions us-east-1 --services ec2 --force

# Delete S3 and RDS in multiple regions
aws-nuker nuke --regions us-east-1,us-west-2 --services s3,rds --force

# Delete new container services
aws-nuker nuke --regions us-east-1 --services ecr,ecs,eks --force

# Delete analytics stack
aws-nuker nuke --regions us-east-1 --services athena,glue,kinesis,redshift --force

# Delete security services
aws-nuker nuke --regions us-east-1 --services kms,secretsmanager,guardduty --force

# Delete all resources in all US regions (DANGEROUS!)
aws-nuker nuke --regions "us-*" --services "*" --force --yes

# Delete all resources in specific regions with parallel execution
aws-nuker nuke --regions us-east-1,us-west-2 --services "*" --force --parallel --max-workers 10
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
│   ├── __init__.py           # Package initialization
│   ├── base_handler.py       # Base class for resource handlers
│   ├── cli.py               # Command-line interface
│   ├── config.py            # Configuration management
│   ├── logger.py            # Logging and audit system
│   ├── orchestrator.py      # Main execution orchestrator
│   ├── registry.py          # Handler registry
│   └── handlers/            # Service-specific handlers
│       ├── __init__.py
│       ├── ec2_handler.py
│       ├── s3_handler.py
│       ├── rds_handler.py
│       ├── lambda_handler.py
│       ├── iam_handler.py
│       ├── dynamodb_handler.py
│       ├── cloudformation_handler.py
│       ├── ecs_handler.py
│       ├── sns_handler.py
│       ├── sqs_handler.py
│       ├── cloudwatch_handler.py
│       ├── apigateway_handler.py
│       ├── elb_handler.py
│       ├── route53_handler.py
│       └── vpc_handler.py
├── logs/                    # Log files (gitignored)
├── audit/                   # Audit trail files (gitignored)
├── requirements.txt         # Python dependencies
├── setup.py                # Package setup
├── main.py                 # Entry point
├── README.md               # This file
└── .gitignore             # Git ignore rules
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

- [ ] Add support for more AWS services
- [ ] Implement resource tagging for selective deletion
- [ ] Add cost estimation before deletion
- [ ] Create web UI for easier interaction
- [ ] Add support for AWS Organizations
- [ ] Implement rollback capabilities (where possible)
- [ ] Add support for resource filters (by tags, creation date, etc.)

---

**Remember: With great power comes great responsibility. Use AWS Nuker wisely! 💪**