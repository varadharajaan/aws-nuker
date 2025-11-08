# AWS Nuker ☠️

**AWS Resource Cleanup and Destroyer Tool** - Ruthlessly delete all AWS resources without mercy!

## ⚠️ WARNING

This tool is **EXTREMELY DANGEROUS** and will **PERMANENTLY DELETE** AWS resources. Use with caution!

- Deletes resources **FORCEFULLY** even if they have dependencies
- Empties and deletes S3 buckets
- Terminates EC2 instances with termination protection disabled
- Deletes RDS instances without final snapshots
- **Default VPCs, subnets, and security groups are PRESERVED**
- All other resources are **RUTHLESSLY DESTROYED**

## Features

✅ **Comprehensive Coverage** - Supports 30+ AWS services (A-Z)
✅ **Multi-Region Support** - Clean resources across multiple regions or all regions
✅ **Selective Cleanup** - Choose specific services to clean
✅ **Dry Run Mode** - Preview what would be deleted before actual deletion
✅ **Dependency Handling** - Forcefully deletes dependent resources
✅ **Default Resource Protection** - Preserves AWS default resources (default VPC, etc.)

## Supported AWS Services

The tool supports the following AWS services (40+ services):

### Compute
- **EC2** - Instances
- **EBS** - Volumes
- **EBS Snapshots**
- **AMI** - Amazon Machine Images
- **Elastic IPs**
- **Key Pairs**
- **Lambda** - Functions
- **Lambda Layers**
- **Auto Scaling Groups**
- **Launch Templates**

### Networking & Load Balancing
- **VPCs** (non-default)
- **Subnets** (non-default)
- **Security Groups** (non-default)
- **ELB** - Classic Load Balancers
- **ALB/NLB** - Application/Network Load Balancers

### Storage
- **S3** - Buckets (with force empty)

### Database
- **RDS Instances**
- **RDS Clusters**
- **RDS Snapshots**
- **DynamoDB** - Tables
- **ElastiCache** - Clusters

### Containers & Registries
- **ECS** - Clusters
- **ECS** - Task Definitions
- **EKS** - Clusters
- **ECR** - Container Registries

### Application Services
- **API Gateway** - REST APIs
- **API Gateway V2** - HTTP/WebSocket APIs
- **SNS** - Topics
- **SQS** - Queues
- **Kinesis** - Streams

### Management & Governance
- **CloudFormation** - Stacks
- **CloudWatch** - Log Groups
- **CloudWatch** - Alarms
- **Route53** - Hosted Zones
- **AWS Backup** - Backup Vaults

### Security & Identity
- **IAM** - Users
- **IAM** - Roles
- **IAM** - Policies (customer managed)
- **IAM** - Groups
- **Secrets Manager** - Secrets

## Installation

### Prerequisites
- Python 3.7 or higher
- AWS credentials configured (via AWS CLI, environment variables, or IAM role)

### Install from source

```bash
# Clone the repository
git clone https://github.com/varadharajaan/aws-nuker.git
cd aws-nuker

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

## Configuration

### AWS Credentials

Configure AWS credentials using one of these methods:

1. **AWS CLI** (recommended):
   ```bash
   aws configure
   ```

2. **Environment Variables**:
   ```bash
   export AWS_ACCESS_KEY_ID="your-access-key"
   export AWS_SECRET_ACCESS_KEY="your-secret-key"
   export AWS_DEFAULT_REGION="us-east-1"
   ```

3. **IAM Role** (if running on EC2/ECS/Lambda)

### Required IAM Permissions

The tool requires broad permissions to delete resources. Here's a minimal IAM policy:

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
        "ecs:*",
        "eks:*",
        "cloudformation:*",
        "dynamodb:*",
        "sns:*",
        "sqs:*",
        "apigateway:*",
        "elasticache:*",
        "logs:*",
        "route53:*"
      ],
      "Resource": "*"
    }
  ]
}
```

⚠️ **Security Note**: Use this policy only in development/testing accounts. Never use in production!

## Usage

### Basic Commands

```bash
# List all available services
aws-nuker --list-services

# Dry run to see what would be deleted (recommended first step)
aws-nuker --regions us-east-1 --services ec2 --dry-run

# Delete all EC2 instances in us-east-1
aws-nuker --regions us-east-1 --services ec2

# Delete multiple services in multiple regions
aws-nuker --regions us-east-1,us-west-2 --services ec2,s3,rds-instances

# Delete all resources in all regions (EXTREME CAUTION!)
aws-nuker --regions all --services all --yes
```

### Command Options

- `--regions, -r` : AWS regions to clean
  - Single region: `us-east-1`
  - Multiple regions: `us-east-1,us-west-2,eu-west-1`
  - All regions: `all`

- `--services, -s` : Services to clean
  - Single service: `ec2`
  - Multiple services: `ec2,s3,rds-instances`
  - All services: `all`

- `--dry-run, -d` : Preview mode (no actual deletion)

- `--list-services, -l` : Show all available services

- `--yes, -y` : Skip confirmation prompt (use with caution!)

### Examples

#### Example 1: Clean EC2 resources in a single region
```bash
aws-nuker --regions us-east-1 --services ec2,ebs,ebs-snapshots
```

#### Example 2: Clean all Lambda functions across multiple regions
```bash
aws-nuker --regions us-east-1,us-west-2,eu-west-1 --services lambda,lambda-layers
```

#### Example 3: Full cleanup in dev account (dry run first)
```bash
# Dry run to preview
aws-nuker --regions all --services all --dry-run

# Execute cleanup
aws-nuker --regions all --services all
```

#### Example 4: Clean specific database resources
```bash
aws-nuker --regions us-east-1 --services rds-instances,rds-clusters,rds-snapshots,dynamodb
```

#### Example 5: Clean networking resources (preserves default VPC)
```bash
aws-nuker --regions us-east-1 --services vpcs,subnets,security-groups
```

## How It Works

1. **Resource Discovery**: Lists all resources for selected services in specified regions
2. **Default Resource Protection**: Filters out AWS default resources (default VPCs, etc.)
3. **Dependency Resolution**: Handles dependencies automatically (e.g., empties S3 buckets before deletion)
4. **Forceful Deletion**: Disables deletion protection and forces resource removal
5. **Parallel Processing**: Processes multiple regions and services efficiently

## Safety Features

- ✅ **Default Resource Protection**: Default VPCs and their resources are never deleted
- ✅ **Dry Run Mode**: Preview changes before execution
- ✅ **Confirmation Prompt**: Requires typing "DELETE" to confirm (unless --yes is used)
- ✅ **Detailed Logging**: Shows what's being deleted in real-time
- ✅ **Error Handling**: Continues cleanup even if some resources fail

## Limitations

- IAM is global (not region-specific) - IAM resources will be processed once
- Some resources may have deletion delays (e.g., RDS snapshots)
- Resources with AWS-managed dependencies may fail to delete
- Rate limiting may occur with large numbers of resources

## Troubleshooting

### Issue: "Access Denied" errors
**Solution**: Ensure your AWS credentials have sufficient permissions (see IAM policy above)

### Issue: "Resource has dependencies" errors
**Solution**: The tool attempts to handle dependencies automatically. If it fails, run the tool again.

### Issue: Resources not deleted
**Solution**: Some resources (like ECS services) may take time to drain. Wait a few minutes and run again.

### Issue: "Region not found" errors
**Solution**: Ensure the region names are correct (e.g., `us-east-1`, not `us-east1`)

## Development

### Running Tests

```bash
# Install development dependencies
pip install -r requirements.txt

# Run tests (if available)
python -m pytest tests/
```

### Project Structure

```
aws-nuker/
├── aws_nuker/
│   ├── __init__.py
│   ├── cli.py              # Main CLI interface
│   ├── utils.py            # Utility functions
│   └── services/
│       ├── __init__.py
│       ├── base.py         # Base service class
│       ├── ec2.py          # EC2 resources
│       ├── vpc.py          # VPC resources
│       ├── s3.py           # S3 buckets
│       ├── rds.py          # RDS resources
│       ├── lambda_service.py # Lambda functions
│       ├── iam.py          # IAM resources
│       ├── containers.py   # ECS/EKS
│       ├── cloudformation.py # CloudFormation
│       └── additional.py   # Other services
├── requirements.txt
├── setup.py
└── README.md
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new services
4. Submit a pull request

## License

MIT License - Use at your own risk!

## Disclaimer

⚠️ **THIS TOOL IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND**

- Use only in development/testing environments
- **NEVER** use in production accounts
- The authors are not responsible for any data loss or AWS charges
- Always run with `--dry-run` first
- Keep backups of important resources
- Understand what you're deleting before running

## Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Submit a pull request
- Check the documentation

---

**Remember**: With great power comes great responsibility. Use AWS Nuker wisely! ☠️