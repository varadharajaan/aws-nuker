# AWS Nuker ☠️

**AWS Resource Cleanup and Destroyer Tool** - Ruthlessly delete all AWS resources without mercy!

Multi-region resource cleanup tool with **67+ AWS services support**, **tag-based filtering**, and **web dashboard**.

## ⚠️ WARNING

This tool is **EXTREMELY DANGEROUS** and will **PERMANENTLY DELETE** AWS resources. Use with caution!

- Deletes resources **FORCEFULLY** even if they have dependencies
- Empties and deletes S3 buckets
- Terminates EC2 instances with termination protection disabled
- Deletes RDS instances without final snapshots
- **Default VPCs, subnets, and security groups are PRESERVED**
- All other resources are **RUTHLESSLY DESTROYED**

## Features

✅ **Comprehensive Coverage** - Supports 67+ AWS services (A-Z)  
✅ **Multi-Region Support** - Clean resources across multiple regions or all regions  
✅ **Selective Cleanup** - Choose specific services to clean  
✅ **Tag-Based Filtering** - Filter resources by tags with wildcard patterns  
✅ **Web Dashboard** - React + TypeScript UI with visualizations and charts  
✅ **REST API** - FastAPI backend for programmatic access  
✅ **Dry Run Mode** - Preview what would be deleted before actual deletion  
✅ **Dependency Handling** - Forcefully deletes dependent resources  
✅ **Default Resource Protection** - Preserves AWS default resources (default VPC, etc.)  

## Quick Start

### CLI Mode
```bash
# Install
git clone https://github.com/varadharajaan/aws-nuker.git
cd aws-nuker
pip install -r requirements.txt
pip install -e .

# Configure AWS credentials
aws configure

# Dry run to preview deletion
aws-nuker --regions us-east-1 --services ec2-instances --tags "env=dev" --dry-run

# Execute deletion
aws-nuker --regions us-east-1 --services ec2-instances --tags "env=dev" --yes
```

### Web UI Mode
```bash
# Start backend server
python3 api_server.py

# In another terminal, start frontend
cd web
npm install
npm run dev

# Open browser to http://localhost:3000
```

## Screenshots

### Dashboard
The main dashboard shows resource discovery with filters, charts, and detailed tables.

### Dry Run & Delete
Preview resources before deletion with safety confirmations and real-time results.

### Reports
View audit logs, cost savings, and cleanup history.

## Interfaces

### 1. Command Line Interface (CLI)
Traditional terminal-based interface for automation and scripts.

### 2. Web Dashboard (NEW!)
Modern React + TypeScript web interface with:
- **Interactive Filters** - Multi-select regions, services, and tag patterns
- **Resource Discovery** - Real-time discovery with visualizations
- **Dry Run Preview** - See exactly what will be deleted
- **Safe Deletion** - Confirmation modals and progress tracking
- **Charts & Analytics** - Resource distribution by service and region
- **Reports** - Audit logs and cost savings tracking

### 3. REST API
FastAPI-powered backend for custom integrations:
- `GET /api/services` - List supported services
- `GET /api/regions` - List available regions  
- `POST /api/discover` - Discover resources
- `POST /api/dryrun` - Simulate deletion
- `POST /api/delete` - Execute deletion
- `GET /api/reports` - Fetch audit logs

## Supported AWS Services

The tool supports the following AWS services (67+ services):

### Compute & Containers
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
- **Batch** - Job Queues & Compute Environments
- **Elastic Beanstalk** - Applications
- **App Runner** - Services
- **Lightsail** - Instances
- **ECS** - Clusters & Task Definitions
- **EKS** - Clusters
- **ECR** - Container Registries

### Networking & Load Balancing
- **VPCs** (non-default)
- **Subnets** (non-default)
- **Security Groups** (non-default)
- **ELB** - Classic Load Balancers
- **ALB/NLB** - Application/Network Load Balancers

### Storage & File Systems
- **S3** - Buckets (with force empty)
- **EFS** - File Systems
- **FSx** - File Systems
- **Storage Gateway**
- **S3 Glacier** - Vaults

### Database
- **RDS** - Instances, Clusters & Snapshots
- **DynamoDB** - Tables
- **ElastiCache** - Clusters
- **Redshift** - Clusters

### Analytics
- **Athena** - Workgroups
- **EMR** - Clusters
- **Glue** - Databases & Crawlers
- **OpenSearch** - Domains
- **Data Pipeline** - Pipelines

### Application Services
- **API Gateway** - REST APIs
- **API Gateway V2** - HTTP/WebSocket APIs
- **SNS** - Topics
- **SQS** - Queues
- **Kinesis** - Streams

### Management & Governance
- **CloudFormation** - Stacks
- **CloudWatch** - Log Groups & Alarms
- **Route53** - Hosted Zones
- **AWS Backup** - Backup Vaults

### Developer Tools
- **CodeCommit** - Repositories
- **CodeBuild** - Projects
- **CodeDeploy** - Applications
- **CodePipeline** - Pipelines
- **CodeArtifact** - Repositories
- **Cloud9** - Environments

### Machine Learning
- **SageMaker** - Notebooks, Endpoints, Models
- **Comprehend** - Entity Recognizers
- **Rekognition** - Collections

### Security & Identity
- **IAM** - Users, Roles, Policies, Groups
- **Secrets Manager** - Secrets

## Installation

### Prerequisites

**For CLI:**
- Python 3.9 or higher
- AWS credentials configured (via AWS CLI, environment variables, or IAM role)

**For Web UI:**
- Python 3.9+
- Node.js 16+ and npm 8+
- AWS credentials configured

### Install CLI Only

```bash
# Clone the repository
git clone https://github.com/varadharajaan/aws-nuker.git
cd aws-nuker

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

### Install Full Stack (CLI + Web UI)

```bash
# Clone the repository
git clone https://github.com/varadharajaan/aws-nuker.git
cd aws-nuker

# Backend setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .

# Frontend setup
cd web
npm install
cd ..
```

**Start the Web UI:**

```bash
# Terminal 1: Start backend API
python3 api_server.py

# Terminal 2: Start frontend
cd web
npm run dev

# Open browser to http://localhost:3000
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

- `--tags, -t` : Filter resources by tags (NEW!)
  - Exact match: `env=dev`
  - Wildcard prefix: `owner=john*`
  - Wildcard suffix: `project=*test`
  - Wildcard contains: `name=*temp*`
  - Tag exists: `environment`
  - Tag not exists: `!protected`
  - Multiple filters (AND logic): `env=dev,owner=john*,!protected`

- `--dry-run, -d` : Preview mode (no actual deletion)

- `--list-services, -l` : Show all available services

- `--yes, -y` : Skip confirmation prompt (use with caution!)

### Tag Filtering Examples

#### Filter by environment tag
```bash
# Delete all EC2 instances with env=dev tag
aws-nuker --regions us-east-1 --services ec2 --tags "env=dev" --dry-run
```

#### Filter by multiple tags (AND logic)
```bash
# Delete resources that match ALL conditions
aws-nuker --regions us-east-1 --services ec2,s3 --tags "env=dev,owner=john*"
```

#### Delete resources without protection tag
```bash
# Delete resources that don't have a 'protected' tag
aws-nuker --regions us-east-1 --services ec2 --tags "!protected"
```

#### Complex tag filtering
```bash
# Delete dev resources owned by specific team, not protected
aws-nuker --regions us-east-1 --services all --tags "env=dev,team=backend,!protected"
```

#### Wildcard pattern matching
```bash
# Delete all test/staging environments
aws-nuker --regions us-east-1 --services ec2 --tags "env=*test*"

# Delete resources owned by contractors
aws-nuker --regions us-east-1 --services ec2 --tags "owner=contractor-*"
```

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

### Web UI Usage

#### Getting Started with Web Dashboard

1. **Start the Services**
   ```bash
   # Terminal 1
   python3 api_server.py
   
   # Terminal 2
   cd web && npm run dev
   ```

2. **Access Dashboard**
   - Open http://localhost:3000
   - Navigate using the top menu

#### Dashboard Page Workflow

**Purpose:** Discover and visualize resources across your AWS account

**Steps:**
1. **Select Regions**
   - Hold Ctrl/Cmd to select multiple regions
   - Choose one or more regions to scan

2. **Select Services**
   - Browse by category (Compute, Storage, Database, etc.)
   - Select specific services or choose multiple

3. **Add Tag Filters (Optional)**
   - Enter tag patterns: `env=dev,!protected`
   - Use wildcards: `owner=john*`

4. **Discover Resources**
   - Click "Discover Resources" button
   - View results in:
     - **Stats Cards** - Total count, services, regions
     - **Bar Chart** - Resources by service
     - **Pie Chart** - Resources by region
     - **Table** - Detailed resource list

**Example Use Case:**
```
Scenario: Find all dev resources in us-east-1

Filters:
- Regions: us-east-1
- Services: ec2-instances, s3, rds-instances
- Tags: env=dev

Result: Discovered 42 resources ready for cleanup
```

#### Dry Run & Delete Page Workflow

**Purpose:** Safely preview and execute resource deletion

**Steps:**
1. **Configure Deletion**
   - Filters are pre-filled from Dashboard
   - Adjust regions, services, or tags if needed

2. **Run Dry Run** (Required)
   - Click "Run Dry Run" button
   - Review the simulation results:
     - Total resources to be deleted
     - Services and regions affected
     - Complete resource list with IDs

3. **Review Carefully**
   - Verify each resource in the table
   - Check that no production resources are included
   - Confirm resource count matches expectations

4. **Execute Deletion**
   - Click "Execute Deletion" button
   - Read the warning modal carefully
   - Confirm the deletion

5. **Monitor Progress**
   - View real-time deletion status
   - Check success/failure counts
   - Review any error messages

6. **Verify Results**
   - Return to Dashboard
   - Run discovery again to confirm deletion

**Safety Features:**
- ⚠️ Red warning banner on page
- 🔒 Dry run required before deletion enabled
- ✅ Confirmation modal with resource count
- 📊 Real-time status updates

#### Reports Page

**Purpose:** View audit logs and cost savings

**Features:**
- Cleanup history
- Cost savings estimates
- Recent activity log
- Export to CSV/JSON (coming soon)

**Current Status:** Basic reporting (full audit logs in development)

#### Web UI vs CLI Comparison

| Feature | Web UI | CLI |
|---------|--------|-----|
| Visual Discovery | ✅ Charts & graphs | ❌ Text only |
| Resource Table | ✅ Sortable, filterable | ❌ List format |
| Dry Run Preview | ✅ Interactive table | ✅ Text output |
| Deletion Safety | ✅ Modal confirmation | ⚠️ Prompt only |
| Multi-region View | ✅ Visual breakdown | ❌ Combined output |
| Automation | ❌ Interactive only | ✅ Scriptable |
| Remote Access | ✅ Browser-based | ❌ Server SSH needed |

**When to use Web UI:**
- Visual resource discovery
- Team collaboration
- Learning the tool
- Complex filtering
- Dry run review

**When to use CLI:**
- Automation scripts
- CI/CD pipelines
- Scheduled cleanups
- SSH-only access
- Fast execution

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

### Full Stack Structure

```
aws-nuker/
├── api_server.py           # FastAPI backend server
├── aws_nuker/              # Core Python package
│   ├── cli.py             # CLI interface
│   ├── utils.py           # Utilities & tag parsing
│   └── services/          # Service implementations (67+)
├── web/                    # React frontend
│   ├── src/
│   │   ├── App.tsx        # Main app component
│   │   ├── pages/         # Dashboard, DryRun, Reports
│   │   ├── components/    # Reusable UI components
│   │   ├── utils/         # API client
│   │   └── types/         # TypeScript definitions
│   ├── package.json
│   └── vite.config.ts
└── docs/                   # Documentation
    ├── ARCHITECTURE.md     # System architecture
    ├── USE_CASES.md        # Use cases & workflows
    └── INSTALLATION.md     # Setup guide
```

## Architecture

### System Overview

```
┌────────────┐     ┌─────────────┐     ┌───────────┐     ┌─────────┐
│  Web UI    │────►│  FastAPI    │────►│  AWS SDK  │────►│   AWS   │
│  (React)   │     │  Backend    │     │  (boto3)  │     │  Cloud  │
└────────────┘     └─────────────┘     └───────────┘     └─────────┘
     │                     │
     │ REST API            │ Python
     │ (HTTP/JSON)         │ Service Classes
     │                     │
     └─────────────────────┘
```

### Components

**Backend (Python)**
- FastAPI REST API server
- Service-based architecture with `BaseService` pattern
- 67+ AWS service implementations
- Tag filtering and validation
- Dependency resolution

**Frontend (React + TypeScript)**
- Modern SPA with React 18
- TailwindCSS for styling
- React Query for state management
- Recharts for data visualization
- Responsive design

**CLI (Python)**
- Click-based command interface
- Direct service class usage
- Same backend logic as web UI
- Scriptable and automatable

## REST API Documentation

Base URL: `http://localhost:8000`

### Endpoints

#### GET /
Health check and API information
```json
{
  "status": "healthy",
  "service": "AWS Nuker API",
  "version": "1.0.0"
}
```

#### GET /api/services
List all supported AWS services
```json
[
  {
    "name": "ec2-instances",
    "display_name": "Ec2 Instances",
    "category": "Compute & Containers",
    "resource_types": ["ec2-instances"]
  }
]
```

#### GET /api/regions
List all available AWS regions
```json
["us-east-1", "us-east-2", "us-west-1", ...]
```

#### POST /api/discover
Discover AWS resources with filters
```json
Request:
{
  "regions": ["us-east-1", "us-west-2"],
  "services": ["ec2-instances", "s3"],
  "tags": "env=dev,!protected"  // optional
}

Response:
{
  "total_resources": 42,
  "resources_by_service": {"ec2-instances": 25, "s3": 17},
  "resources_by_region": {"us-east-1": 30, "us-west-2": 12},
  "resources": [
    {
      "id": "i-1234567890abcdef0",
      "type": "ec2-instances",
      "region": "us-east-1",
      "service": "ec2",
      "name": "web-server",
      "tags": {"env": "dev"},
      "state": "running"
    }
  ],
  "dependencies": []
}
```

#### POST /api/dryrun
Simulate resource deletion (same as /api/discover)

#### POST /api/delete
Execute resource deletion
```json
Request:
{
  "regions": ["us-east-1"],
  "services": ["ec2-instances"],
  "tags": "env=dev",
  "confirm": true  // required
}

Response:
{
  "status": "completed",
  "deleted_count": 25,
  "failed_count": 0,
  "results": [
    {
      "service": "ec2-instances",
      "region": "us-east-1",
      "status": "completed"
    }
  ]
}
```

#### GET /api/reports
Get audit logs and cleanup reports
```json
[]  // Returns array of report objects
```

### API Error Responses

```json
{
  "detail": "Error message here"
}
```

HTTP Status Codes:
- 200: Success
- 400: Bad request (invalid parameters)
- 500: Server error (AWS API error, etc.)

## Documentation

Comprehensive documentation available in the `/docs` directory:

- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - System architecture, component diagrams, data flows
- **[USE_CASES.md](docs/USE_CASES.md)** - Common scenarios, workflows, best practices
- **[INSTALLATION.md](docs/INSTALLATION.md)** - Detailed setup guide, troubleshooting

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