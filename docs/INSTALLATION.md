# AWS Nuker Installation Guide

This guide provides detailed installation instructions for AWS Nuker.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Installation Methods](#installation-methods)
3. [AWS Credentials Setup](#aws-credentials-setup)
4. [Verification](#verification)
5. [Troubleshooting](#troubleshooting)

## System Requirements

### Software Requirements
- **Python**: 3.8 or higher
- **pip**: Latest version recommended
- **Operating System**: Linux, macOS, or Windows
- **AWS Account**: With appropriate permissions

### Python Dependencies
All dependencies are listed in `requirements.txt`:
- boto3 >= 1.34.0
- botocore >= 1.34.0
- colorama >= 0.4.6
- python-dateutil >= 2.8.2
- PyYAML >= 6.0.1
- tabulate >= 0.9.0
- tqdm >= 4.66.0
- click >= 8.1.7

## Installation Methods

### Method 1: Install from Source (Recommended)

```bash
# Clone the repository
git clone https://github.com/varadharajaan/aws-nuker.git
cd aws-nuker

# Create a virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .

# Verify installation
aws-nuker --version
```

### Method 2: Direct Installation

```bash
# Clone and install in one go
git clone https://github.com/varadharajaan/aws-nuker.git
cd aws-nuker
pip install -e .
```

### Method 3: Using setup.py

```bash
# Clone the repository
git clone https://github.com/varadharajaan/aws-nuker.git
cd aws-nuker

# Install using setup.py
python setup.py install
```

### Method 4: PyPI (When Available)

```bash
# Once published to PyPI
pip install aws-nuker
```

## AWS Credentials Setup

AWS Nuker requires AWS credentials to access and delete resources. Configure credentials using one of these methods:

### Option 1: AWS CLI Configuration (Recommended)

```bash
# Install AWS CLI if not already installed
pip install awscli

# Configure credentials
aws configure
```

You'll be prompted for:
- AWS Access Key ID
- AWS Secret Access Key
- Default region
- Output format

This creates `~/.aws/credentials` and `~/.aws/config` files.

### Option 2: Environment Variables

```bash
# Linux/macOS
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="us-east-1"

# Windows (PowerShell)
$env:AWS_ACCESS_KEY_ID="your-access-key"
$env:AWS_SECRET_ACCESS_KEY="your-secret-key"
$env:AWS_DEFAULT_REGION="us-east-1"

# Windows (Command Prompt)
set AWS_ACCESS_KEY_ID=your-access-key
set AWS_SECRET_ACCESS_KEY=your-secret-key
set AWS_DEFAULT_REGION=us-east-1
```

### Option 3: IAM Role (EC2 Instances)

If running on an EC2 instance:

1. Create an IAM role with necessary permissions
2. Attach the role to your EC2 instance
3. No credential configuration needed

### Option 4: AWS SSO

```bash
# Configure SSO
aws configure sso

# Login
aws sso login --profile your-profile

# Use the profile
export AWS_PROFILE=your-profile
```

## Required IAM Permissions

Create an IAM policy with appropriate permissions. Here's a comprehensive policy (⚠️ Very permissive):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:Describe*",
        "ec2:Delete*",
        "ec2:Terminate*",
        "ec2:Deregister*",
        "ec2:Release*",
        "s3:List*",
        "s3:Delete*",
        "s3:GetBucket*",
        "rds:Describe*",
        "rds:Delete*",
        "lambda:List*",
        "lambda:Delete*",
        "iam:List*",
        "iam:Delete*",
        "iam:Detach*",
        "iam:Remove*",
        "dynamodb:List*",
        "dynamodb:Describe*",
        "dynamodb:Delete*",
        "cloudformation:List*",
        "cloudformation:Describe*",
        "cloudformation:Delete*",
        "ecs:List*",
        "ecs:Describe*",
        "ecs:Delete*",
        "sns:List*",
        "sns:Delete*",
        "sqs:List*",
        "sqs:Delete*",
        "sqs:Purge*",
        "cloudwatch:Describe*",
        "cloudwatch:Delete*",
        "logs:Describe*",
        "logs:Delete*",
        "apigateway:GET",
        "apigateway:DELETE",
        "elasticloadbalancing:Describe*",
        "elasticloadbalancing:Delete*",
        "route53:List*",
        "route53:Get*",
        "route53:Delete*",
        "route53:Change*"
      ],
      "Resource": "*"
    }
  ]
}
```

**For production use**, create a more restrictive policy based on your specific needs.

## Verification

### Verify Installation

```bash
# Check version
aws-nuker --version

# View help
aws-nuker --help

# List available services
aws-nuker list-services

# List available regions
aws-nuker list-regions
```

Expected output for `aws-nuker --version`:
```
python -m aws_nuker.cli, version 1.0.0
```

### Verify AWS Credentials

```bash
# Test AWS connectivity
aws sts get-caller-identity

# Or test with AWS Nuker dry run
aws-nuker nuke --regions us-east-1 --services ec2 --dry-run
```

If credentials are configured correctly, you should see your account information or a dry-run report.

### Run a Safe Test

```bash
# Dry run to test without deleting
aws-nuker nuke --regions us-east-1 --services ec2 --dry-run

# This will show what would be deleted without actually deleting anything
```

## Troubleshooting

### Issue: Command Not Found

**Problem**: `aws-nuker: command not found`

**Solutions**:
```bash
# Option 1: Use python module directly
python3 -m aws_nuker.cli --help

# Option 2: Add to PATH
export PATH="$HOME/.local/bin:$PATH"

# Option 3: Reinstall with user flag
pip install --user -e .

# Option 4: Use absolute path
~/.local/bin/aws-nuker --help
```

### Issue: Import Errors

**Problem**: `ModuleNotFoundError: No module named 'boto3'`

**Solutions**:
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Or install specific missing package
pip install boto3
```

### Issue: AWS Credentials Not Found

**Problem**: `Unable to locate credentials`

**Solutions**:
```bash
# Configure AWS credentials
aws configure

# Or set environment variables
export AWS_ACCESS_KEY_ID="your-key"
export AWS_SECRET_ACCESS_KEY="your-secret"

# Verify credentials
aws sts get-caller-identity
```

### Issue: Permission Denied

**Problem**: `An error occurred (AccessDenied)`

**Solutions**:
1. Verify IAM permissions
2. Check if MFA is required
3. Ensure credentials are for the correct account
4. Verify you have permissions for the specific service

### Issue: Python Version

**Problem**: `python: command not found` or wrong version

**Solutions**:
```bash
# Use python3 explicitly
python3 --version

# Or create alias
alias python=python3

# Install correct Python version
# (varies by OS - check your package manager)
```

### Issue: Rate Limiting

**Problem**: `Rate exceeded` or similar errors

**Solutions**:
```bash
# Use sequential execution (default)
aws-nuker nuke --regions us-east-1 --services ec2

# Reduce parallel workers
aws-nuker nuke --regions us-east-1 --services "*" --parallel --max-workers 3

# Process services one at a time
aws-nuker nuke --regions us-east-1 --services ec2
aws-nuker nuke --regions us-east-1 --services s3
```

### Issue: Virtual Environment

**Problem**: Dependencies conflict with system packages

**Solution**: Always use a virtual environment:
```bash
# Create virtual environment
python3 -m venv aws-nuker-env

# Activate (Linux/macOS)
source aws-nuker-env/bin/activate

# Activate (Windows)
aws-nuker-env\Scripts\activate

# Install
pip install -e .

# When done
deactivate
```

## Post-Installation

### Create an Alias (Optional)

```bash
# Add to ~/.bashrc or ~/.zshrc
alias nuker="aws-nuker"

# Reload shell
source ~/.bashrc

# Now you can use
nuker --help
```

### Set Up Shell Completion (Optional)

```bash
# For bash
_AWS_NUKER_COMPLETE=bash_source aws-nuker > ~/.aws-nuker-complete.bash
echo "source ~/.aws-nuker-complete.bash" >> ~/.bashrc

# For zsh
_AWS_NUKER_COMPLETE=zsh_source aws-nuker > ~/.aws-nuker-complete.zsh
echo "source ~/.aws-nuker-complete.zsh" >> ~/.zshrc
```

## Upgrading

### Upgrade from Source

```bash
cd aws-nuker
git pull origin main
pip install --upgrade -r requirements.txt
pip install --upgrade -e .
```

### Upgrade from PyPI (When Available)

```bash
pip install --upgrade aws-nuker
```

## Uninstallation

```bash
# Uninstall package
pip uninstall aws-nuker

# Remove cloned repository
rm -rf aws-nuker

# Remove virtual environment (if created)
rm -rf venv  # or your venv name
```

## Next Steps

After installation:

1. Review the [README.md](README.md) for usage instructions
2. Check [EXAMPLES.md](docs/EXAMPLES.md) for usage examples
3. Read [CONTRIBUTING.md](CONTRIBUTING.md) if you want to contribute
4. **Always test with `--dry-run` first!**

## Getting Help

- **Documentation**: Check the [docs](docs/) folder
- **Issues**: Report problems on [GitHub Issues](https://github.com/varadharajaan/aws-nuker/issues)
- **Discussions**: Ask questions in [GitHub Discussions](https://github.com/varadharajaan/aws-nuker/discussions)
