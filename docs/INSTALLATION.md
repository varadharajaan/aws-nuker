# AWS Nuker - Installation and Quick Start Guide

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Quick Start (CLI)](#quick-start-cli)
5. [Quick Start (Web UI)](#quick-start-web-ui)
6. [Verification](#verification)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements
- **Python:** 3.9 or higher
- **Node.js:** 16.x or higher (for web UI)
- **npm:** 8.x or higher (for web UI)
- **Operating System:** Linux, macOS, or Windows (WSL recommended)
- **AWS Account:** With appropriate IAM permissions
- **Disk Space:** Minimum 500MB free space

### AWS Permissions Required

The AWS IAM user or role must have permissions to:
- List resources across all services
- Delete resources (for execution mode)
- Read tags from resources

**Recommended IAM Policy:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:Describe*",
        "ec2:DeleteVolume",
        "ec2:TerminateInstances",
        "ec2:DeleteSnapshot",
        "s3:ListAllMyBuckets",
        "s3:DeleteBucket",
        "rds:Describe*",
        "rds:DeleteDBInstance",
        "lambda:ListFunctions",
        "lambda:DeleteFunction",
        "iam:List*",
        "iam:DeleteUser",
        "iam:DeleteRole",
        "dynamodb:ListTables",
        "dynamodb:DeleteTable"
      ],
      "Resource": "*"
    }
  ]
}
```

**⚠️ Warning:** This is a powerful tool. For production use, create more restrictive policies based on your specific needs.

## Installation

### Option 1: CLI Only (Lightweight)

```bash
# Clone the repository
git clone https://github.com/varadharajaan/aws-nuker.git
cd aws-nuker

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Install the CLI tool
pip install -e .

# Verify installation
aws-nuker --help
```

### Option 2: Full Stack (CLI + Web UI)

```bash
# Clone the repository
git clone https://github.com/varadharajaan/aws-nuker.git
cd aws-nuker

# Backend Setup
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install fastapi uvicorn python-multipart

# Frontend Setup
cd web
npm install
cd ..

# Verify installations
python3 --version  # Should be 3.9+
node --version     # Should be 16+
aws-nuker --version
```

### Option 3: Docker (Coming Soon)

```bash
# Pull the Docker image
docker pull ghcr.io/varadharajaan/aws-nuker:latest

# Run with Docker Compose
docker-compose up -d
```

## Configuration

### AWS Credentials Setup

**Method 1: AWS CLI Configuration**
```bash
# Configure AWS CLI (recommended)
aws configure

# Enter when prompted:
AWS Access Key ID: YOUR_ACCESS_KEY
AWS Secret Access Key: YOUR_SECRET_KEY
Default region name: us-east-1
Default output format: json
```

**Method 2: Environment Variables**
```bash
# Set environment variables
export AWS_ACCESS_KEY_ID=your_access_key_id
export AWS_SECRET_ACCESS_KEY=your_secret_access_key
export AWS_DEFAULT_REGION=us-east-1

# For Windows PowerShell:
$env:AWS_ACCESS_KEY_ID="your_access_key_id"
$env:AWS_SECRET_ACCESS_KEY="your_secret_access_key"
$env:AWS_DEFAULT_REGION="us-east-1"
```

**Method 3: AWS Profile**
```bash
# Create/edit ~/.aws/credentials
[default]
aws_access_key_id = YOUR_ACCESS_KEY
aws_secret_access_key = YOUR_SECRET_KEY

[dev-account]
aws_access_key_id = DEV_ACCESS_KEY
aws_secret_access_key = DEV_SECRET_KEY

# Use specific profile
export AWS_PROFILE=dev-account
aws-nuker --regions us-east-1 --list-services
```

### Verify AWS Configuration

```bash
# Test AWS credentials
aws sts get-caller-identity

# Expected output:
{
    "UserId": "AIDACKCEVSQ6C2EXAMPLE",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::123456789012:user/DevAdmin"
}
```

## Quick Start (CLI)

### 1. List Available Services

```bash
# Show all 67+ supported services
aws-nuker --list-services
```

Output:
```
Available services:
- Compute & Containers (17 services)
  • ec2-instances, ec2-volumes, ec2-snapshots, ec2-amis...
- Networking (5 services)
  • vpcs, subnets, security-groups, elb, alb...
- Storage (5 services)
  • s3, efs, fsx, storage-gateway, glacier-vaults
...
```

### 2. Discover Resources (Dry Run)

```bash
# Discover all EC2 instances in us-east-1
aws-nuker --regions us-east-1 --services ec2-instances --dry-run

# Discover multiple services across regions
aws-nuker \
  --regions us-east-1,us-west-2 \
  --services ec2-instances,s3,rds-instances \
  --dry-run

# Discover with tag filtering
aws-nuker \
  --regions us-east-1 \
  --services all \
  --tags "env=dev,!protected" \
  --dry-run
```

### 3. Execute Deletion

```bash
# Delete dev environment EC2 instances
aws-nuker \
  --regions us-east-1 \
  --services ec2-instances \
  --tags "env=dev" \
  --yes  # Skip confirmation prompt

# Interactive deletion (will prompt for confirmation)
aws-nuker \
  --regions us-east-1 \
  --services ec2-instances,ec2-volumes \
  --tags "temporary=true"
```

### 4. Common CLI Patterns

```bash
# List all S3 buckets (no deletion)
aws-nuker --regions us-east-1 --services s3 --dry-run

# Delete old test resources
aws-nuker \
  --regions all \
  --services ec2-instances,ec2-volumes \
  --tags "env=test,temporary=true" \
  --yes

# Clean up specific region
aws-nuker \
  --regions eu-west-1 \
  --services all \
  --tags "project=archived" \
  --dry-run
```

## Quick Start (Web UI)

### 1. Start the Backend Server

```bash
# Activate virtual environment
source venv/bin/activate  # Windows: venv\Scripts\activate

# Start FastAPI server
python3 api_server.py
```

Expected output:
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 2. Start the Frontend Server

Open a new terminal:

```bash
# Navigate to web directory
cd web

# Start Vite dev server
npm run dev
```

Expected output:
```
  VITE v5.0.8  ready in 523 ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: use --host to expose
  ➜  press h to show help
```

### 3. Access the Web UI

1. Open your browser to **http://localhost:3000**
2. You should see the AWS Nuker Dashboard
3. Verify that services and regions are loaded

### 4. First Discovery via Web UI

**Step-by-Step:**

1. **Navigate to Dashboard**
   - Click on "Dashboard" in the navigation menu

2. **Select Filters**
   - Regions: Select `us-east-1` (hold Ctrl/Cmd for multiple)
   - Services: Select `ec2-instances`
   - Tags: Leave empty for now

3. **Discover Resources**
   - Click "Discover Resources" button
   - Wait for discovery to complete
   - Review the results:
     - Total resources found
     - Resources by service (bar chart)
     - Resources by region (pie chart)
     - Resource table with details

4. **Run Dry Run**
   - Navigate to "Dry Run & Delete"
   - Filters are automatically preserved
   - Click "Run Dry Run"
   - Review the preview of what would be deleted

5. **Execute Deletion (Optional)**
   - Review dry run results carefully
   - Click "Execute Deletion"
   - Confirm in the modal dialog
   - Monitor deletion progress and results

### 5. Web UI Workflow Example

**Scenario: Clean up dev environment**

```
1. Dashboard
   ├── Select Regions: us-east-1, us-west-2
   ├── Select Services: ec2-instances, s3, rds-instances
   ├── Tag Filter: env=dev,!protected
   └── Click "Discover Resources"

2. Review Results
   ├── Check total resource count
   ├── Review charts and distribution
   └── Verify resources in table

3. Dry Run & Delete
   ├── Navigate to "Dry Run & Delete" page
   ├── Click "Run Dry Run"
   ├── Review all resources to be deleted
   └── If correct, click "Execute Deletion"

4. Confirm
   ├── Read warning in modal
   ├── Verify count matches expectation
   └── Click "Delete Now"

5. Monitor
   ├── Watch deletion progress
   ├── Check success/failure counts
   └── Review any errors

6. Verify
   └── Run discovery again to confirm deletion
```

## Verification

### Verify CLI Installation

```bash
# Check version
aws-nuker --version

# List services
aws-nuker --list-services

# Test dry run
aws-nuker --regions us-east-1 --services cloudwatch-logs --dry-run
```

### Verify Web UI Installation

1. **Backend Health Check**
   ```bash
   curl http://localhost:8000/
   ```
   Expected: JSON response with status "healthy"

2. **Frontend Load**
   - Open http://localhost:3000
   - Check browser console for errors
   - Verify navigation works

3. **API Integration**
   - Go to Dashboard
   - Click "Discover Resources"
   - Check network tab for successful API calls

### Verify AWS Access

```bash
# Test AWS connectivity
aws ec2 describe-regions

# Test with aws-nuker
aws-nuker --regions us-east-1 --services ec2-instances --dry-run
```

## Troubleshooting

### Common Installation Issues

**Issue: `python3: command not found`**
```bash
# Solution: Install Python 3.9+
# macOS:
brew install python@3.9

# Ubuntu/Debian:
sudo apt-get update
sudo apt-get install python3.9

# Windows: Download from python.org
```

**Issue: `pip: command not found`**
```bash
# Solution: Install pip
python3 -m ensurepip --default-pip
```

**Issue: `npm: command not found`**
```bash
# Solution: Install Node.js and npm
# macOS:
brew install node

# Ubuntu/Debian:
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Windows: Download from nodejs.org
```

**Issue: `ModuleNotFoundError: No module named 'fastapi'`**
```bash
# Solution: Install backend dependencies
pip install fastapi uvicorn python-multipart
```

**Issue: Port 8000 or 3000 already in use**
```bash
# Solution: Use different ports
# Backend:
uvicorn api_server:app --port 8001

# Frontend: Edit vite.config.ts
server: {
  port: 3001
}
```

### Common Runtime Issues

**Issue: "Access Denied" errors**
```bash
# Solution: Check AWS permissions
aws sts get-caller-identity
aws ec2 describe-instances --max-items 1

# Verify IAM policy includes required permissions
```

**Issue: No resources discovered**
```bash
# Solution: Verify filters
# 1. Check region has resources
aws ec2 describe-instances --region us-east-1

# 2. Check tag filter syntax
aws-nuker --regions us-east-1 --services ec2-instances --tags "env=dev" --dry-run

# 3. Try without filters
aws-nuker --regions us-east-1 --services ec2-instances --dry-run
```

**Issue: Frontend can't connect to backend**
```bash
# Solution: Check backend is running
curl http://localhost:8000/

# Check CORS settings in api_server.py
# Verify proxy configuration in vite.config.ts
```

**Issue: Deletion fails with dependency errors**
```bash
# Solution: Delete dependencies first
# Example: Delete EC2 instances before deleting VPC

# Or use specific services in order:
1. ec2-instances
2. ec2-volumes
3. subnets
4. vpcs
```

### Debug Mode

**Enable verbose logging:**

```bash
# CLI
export AWS_NUKER_DEBUG=1
aws-nuker --regions us-east-1 --services ec2-instances --dry-run

# Backend
uvicorn api_server:app --log-level debug
```

### Getting Help

1. **Check Documentation**
   - README.md - Overview and features
   - docs/USE_CASES.md - Usage examples
   - docs/ARCHITECTURE.md - Technical details

2. **Review Examples**
   - examples.py - CLI usage examples

3. **Check Logs**
   - Backend: Console output from api_server.py
   - Frontend: Browser developer console
   - AWS: CloudTrail logs for API calls

4. **Report Issues**
   - GitHub Issues: https://github.com/varadharajaan/aws-nuker/issues
   - Include: Error messages, steps to reproduce, environment details

## Next Steps

After successful installation:

1. **Read the Documentation**
   - Review `docs/USE_CASES.md` for common scenarios
   - Check `docs/ARCHITECTURE.md` for technical details

2. **Test in Safe Environment**
   - Start with dev/test AWS account
   - Use dry-run mode extensively
   - Test with non-critical services first

3. **Implement Tagging Strategy**
   - Tag all resources appropriately
   - Use `protected=true` for critical resources
   - Document your tagging conventions

4. **Create Cleanup Policies**
   - Define regular cleanup schedules
   - Document tag filters for each use case
   - Set up monitoring and reporting

5. **Train Your Team**
   - Share this documentation
   - Run demo sessions
   - Establish approval workflows

## Production Deployment

For production use:

```bash
# Build frontend for production
cd web
npm run build

# Serve frontend with nginx or similar
# Configure backend with proper auth
# Set up monitoring and logging
# Implement approval workflows
# Schedule regular cleanups
```

See `docs/ARCHITECTURE.md` for production deployment architecture.
