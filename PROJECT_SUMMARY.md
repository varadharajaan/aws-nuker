# AWS Nuker - Project Summary

## Overview

AWS Nuker is a comprehensive AWS resource cleanup and destroyer tool that ruthlessly deletes AWS resources across 40+ services while preserving default AWS resources.

## Key Features

### 1. Comprehensive Service Coverage (40+ Services)

#### Compute & Containers
- EC2 Instances
- EBS Volumes & Snapshots
- AMIs (Amazon Machine Images)
- Elastic IPs
- Key Pairs
- Lambda Functions & Layers
- Auto Scaling Groups
- Launch Templates
- ECS Clusters & Task Definitions
- EKS Clusters
- ECR Repositories

#### Networking & Load Balancing
- VPCs (non-default)
- Subnets (non-default)
- Security Groups (non-default)
- Classic Load Balancers (ELB)
- Application/Network Load Balancers (ALB/NLB)

#### Storage
- S3 Buckets (with force empty)

#### Databases
- RDS Instances, Clusters & Snapshots
- DynamoDB Tables
- ElastiCache Clusters

#### Application Services
- API Gateway (REST & HTTP/WebSocket)
- SNS Topics
- SQS Queues
- Kinesis Streams

#### Management & Governance
- CloudFormation Stacks
- CloudWatch Log Groups & Alarms
- Route53 Hosted Zones
- AWS Backup Vaults

#### Security & Identity
- IAM Users, Roles, Policies & Groups
- Secrets Manager Secrets

### 2. Powerful Features

- **Multi-Region Support**: Clean resources in single, multiple, or all AWS regions
- **Selective Cleanup**: Choose specific services to clean
- **Dry-Run Mode**: Preview what would be deleted without making changes
- **Forceful Deletion**: Automatically handles dependencies and deletion protection
- **Default Resource Protection**: Preserves AWS default resources (default VPCs, etc.)
- **Comprehensive Error Handling**: Continues operation even if some resources fail
- **Rich CLI Output**: Colorized output with progress tracking

### 3. Safety Mechanisms

- **Confirmation Required**: Users must type "DELETE" to proceed (unless --yes flag)
- **Dry-Run First**: Strongly encouraged to preview changes
- **Default VPC Protection**: Never deletes default VPCs and their resources
- **Detailed Logging**: Shows exactly what's being deleted
- **Error Recovery**: Continues cleanup even if individual resources fail

## Architecture

### Project Structure
```
aws-nuker/
├── aws_nuker/
│   ├── __init__.py           # Package initialization
│   ├── cli.py                # Main CLI interface
│   ├── utils.py              # Utility functions
│   └── services/
│       ├── __init__.py
│       ├── base.py           # Base service class
│       ├── ec2.py            # EC2-related services
│       ├── vpc.py            # VPC-related services
│       ├── s3.py             # S3 service
│       ├── rds.py            # RDS services
│       ├── lambda_service.py # Lambda services
│       ├── iam.py            # IAM services
│       ├── containers.py     # ECS/EKS services
│       ├── cloudformation.py # CloudFormation service
│       ├── additional.py     # Additional services
│       └── extended.py       # Extended services
├── requirements.txt          # Python dependencies
├── setup.py                  # Package setup
├── .gitignore               # Git ignore rules
├── README.md                # User documentation
├── LICENSE                  # MIT License
├── CONTRIBUTING.md          # Contribution guide
├── SECURITY.md              # Security analysis
├── examples.py              # Usage examples
└── PROJECT_SUMMARY.md       # This file
```

### Design Patterns

1. **Service-Based Architecture**: Each AWS service has its own class
2. **Base Class Pattern**: All services inherit from `BaseService`
3. **Dependency Injection**: Region and dry-run mode injected at instantiation
4. **Template Method**: Base class defines cleanup flow, subclasses implement details

### Core Components

#### BaseService Class
- Defines standard interface for all services
- Implements main cleanup workflow
- Handles error logging and statistics
- Provides consistent output formatting

#### Service Classes
- Implement `get_service_name()`: Return service name
- Implement `list_resources()`: List all resources
- Implement `delete_resource()`: Delete a single resource
- Handle service-specific dependencies

#### CLI Interface
- Built with Click framework
- Supports region and service selection
- Implements dry-run and confirmation modes
- Provides rich, colorized output

## Usage Examples

### List Available Services
```bash
aws-nuker --list-services
```

### Dry Run (Preview)
```bash
aws-nuker --regions us-east-1 --services ec2 --dry-run
```

### Delete EC2 Resources
```bash
aws-nuker --regions us-east-1 --services ec2,ebs,ebs-snapshots
```

### Multi-Region Cleanup
```bash
aws-nuker --regions us-east-1,us-west-2,eu-west-1 --services lambda
```

### Full Cleanup (DANGEROUS!)
```bash
aws-nuker --regions all --services all
```

## Installation

### From Source
```bash
git clone https://github.com/varadharajaan/aws-nuker.git
cd aws-nuker
pip install -r requirements.txt
pip install -e .
```

### Quick Test
```bash
aws-nuker --list-services
```

## Dependencies

- **boto3**: AWS SDK for Python
- **click**: CLI framework
- **colorama**: Terminal color support
- **tabulate**: Table formatting (optional)

## Security Analysis

### CodeQL Results
- 7 alerts flagged: All are false positives
- Alerts relate to logging AWS resource IDs (not secrets)
- Detailed analysis in SECURITY.md

### What's NOT Logged
- AWS credentials or access keys
- IAM passwords
- Secret Manager secret values
- Database passwords
- Any actual sensitive data

### What IS Logged
- Resource IDs (e.g., i-1234567890abcdef0)
- Resource names (user-defined)
- Service names (e.g., "EC2", "S3")
- Region names (e.g., "us-east-1")
- Operation results (deleted, failed, skipped)

## Best Practices

### For Users
1. **Always use --dry-run first**
2. **Never use in production accounts**
3. **Create backups before running**
4. **Use least-privilege IAM permissions**
5. **Enable MFA on accounts with delete permissions**

### For Contributors
1. Follow the service class pattern
2. Add comprehensive error handling
3. Document all new services in README
4. Test in sandbox AWS accounts only
5. Add usage examples for new features

## Future Enhancements

Potential areas for expansion:
- Additional AWS services (Redshift, EMR, etc.)
- Filtering by tags or naming patterns
- Parallel execution for faster cleanup
- Export audit log to file
- Interactive mode for resource selection
- Cost estimation before deletion
- Integration with AWS Organizations

## Contributing

See CONTRIBUTING.md for detailed contribution guidelines.

## License

MIT License - See LICENSE file for details

## Disclaimer

⚠️ **USE AT YOUR OWN RISK**

This tool is designed for development and testing environments. Never use in production accounts. The authors are not responsible for any data loss or AWS charges incurred from using this tool.

Always:
- Test with --dry-run first
- Verify you're in the correct account
- Keep backups of important resources
- Understand what you're deleting

## Contact & Support

- Issues: GitHub Issues
- Contributions: Pull Requests welcome
- Documentation: See README.md

---

**Built with ❤️ for AWS developers who need to clean up their dev environments**
