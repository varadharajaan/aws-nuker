# AWS Nuker - Usage Examples

This document provides comprehensive examples of using AWS Nuker in various scenarios.

## Table of Contents

1. [Basic Usage](#basic-usage)
2. [Testing & Dry Run](#testing--dry-run)
3. [Single Service Cleanup](#single-service-cleanup)
4. [Multi-Service Cleanup](#multi-service-cleanup)
5. [Multi-Region Operations](#multi-region-operations)
6. [Advanced Region Selection](#advanced-region-selection)
7. [Parallel Execution](#parallel-execution)
8. [Real-World Scenarios](#real-world-scenarios)

## Basic Usage

### List Available Services

```bash
aws-nuker list-services
```

Output:
```
Available AWS Services:

  acm, apigateway, apigatewayv2, appstream, athena
  autoscaling, backup, batch, cloudformation, cloudfront
  cloudtrail, cloudwatch, codecommit, codepipeline, cognito
  ...

Total: 60+ services
```

### List Available Regions

```bash
aws-nuker list-regions
```

Output:
```
Available AWS Regions:

  us-east-1, us-east-2, us-west-1, us-west-2
  ap-south-1, ap-southeast-1, ap-southeast-2, ap-northeast-1
  eu-central-1, eu-west-1, eu-west-2, eu-west-3
  ...

Total: 25+ regions
```

## Testing & Dry Run

### Dry Run - Preview Without Deleting

Always test with dry run first!

```bash
# Preview EC2 cleanup in us-east-1
aws-nuker nuke --regions us-east-1 --services ec2 --dry-run

# Preview all services in multiple regions
aws-nuker nuke --regions us-east-1,us-west-2 --services "*" --dry-run
```

Output:
```
==================================================================================
AWS NUKER - CONFIGURATION
==================================================================================

Regions:
  - us-east-1

Services (1):
  ec2

Options:
  Dry Run: True
  Force: False
  Parallel: False

==================================================================================
Starting cleanup operation
==================================================================================

INFO - Starting cleanup of ec2 in us-east-1
INFO - Found 5 ec2 resource(s)
INFO - [DRY RUN] Would delete ec2: i-1234567890abcdef0
INFO - [DRY RUN] Would delete ec2: vol-1234567890abcdef
INFO - [DRY RUN] Would delete ec2: snap-1234567890abcdef
...

NOTE: This was a DRY RUN - no actual deletions occurred
```

## Single Service Cleanup

### Clean Up EC2 Resources

```bash
# Clean all EC2 resources in us-east-1
aws-nuker nuke --regions us-east-1 --services ec2 --force

# With confirmation prompt
aws-nuker nuke --regions us-east-1 --services ec2 --force
# You'll be prompted to type 'DELETE' to confirm

# Skip confirmation
aws-nuker nuke --regions us-east-1 --services ec2 --force --yes
```

### Clean Up S3 Buckets

```bash
# Delete all S3 buckets (including versioned buckets)
aws-nuker nuke --regions us-east-1 --services s3 --force --yes

# S3 is global but region-aware for bucket location
# This will delete buckets in the specified region
```

### Clean Up Lambda Functions

```bash
# Delete all Lambda functions
aws-nuker nuke --regions us-east-1 --services lambda --force --yes
```

### Clean Up RDS Databases

```bash
# Delete all RDS instances and clusters
aws-nuker nuke --regions us-east-1 --services rds --force --yes

# This will:
# - Delete DB instances without final snapshots
# - Delete Aurora clusters
# - Delete manual snapshots
```

## Multi-Service Cleanup

### Clean Up Related Services Together

```bash
# Clean up compute resources
aws-nuker nuke \
  --regions us-east-1 \
  --services ec2,lambda,ecs \
  --force --yes

# Clean up databases
aws-nuker nuke \
  --regions us-east-1 \
  --services rds,dynamodb,elasticache \
  --force --yes

# Clean up storage
aws-nuker nuke \
  --regions us-east-1 \
  --services s3,efs,glacier \
  --force --yes

# Clean up networking
aws-nuker nuke \
  --regions us-east-1 \
  --services vpc,elb,route53 \
  --force --yes
```

### Clean Up CloudFormation and Dependencies

```bash
# Clean up CloudFormation stacks (will delete dependent resources)
aws-nuker nuke \
  --regions us-east-1 \
  --services cloudformation \
  --force --yes
```

## Multi-Region Operations

### Clean Up Across Multiple Specific Regions

```bash
# Comma-separated regions
aws-nuker nuke \
  --regions us-east-1,us-west-2,eu-west-1 \
  --services ec2,s3 \
  --force --yes
```

### Clean Up All US Regions

```bash
# Using wildcard for all US regions
aws-nuker nuke \
  --regions "us-*" \
  --services "*" \
  --force --yes

# This will target:
# - us-east-1
# - us-east-2
# - us-west-1
# - us-west-2
```

### Clean Up All EU Regions

```bash
# Using wildcard for all EU regions
aws-nuker nuke \
  --regions "eu-*" \
  --services "*" \
  --force --yes

# This will target:
# - eu-central-1
# - eu-west-1
# - eu-west-2
# - eu-west-3
# - eu-north-1
```

### Clean Up ALL Regions (Nuclear Option)

```bash
# ⚠️ EXTREMELY DANGEROUS - Use with extreme caution!
aws-nuker nuke \
  --regions "*" \
  --services "*" \
  --force --yes
```

## Advanced Region Selection

### Using Region Ranges

```bash
# Range notation (alphabetical order)
aws-nuker nuke \
  --regions us-east-1..us-west-2 \
  --services ec2 \
  --dry-run

# This includes all regions between us-east-1 and us-west-2 alphabetically
```

### Combining Multiple Patterns

While the CLI supports one pattern at a time, you can run multiple commands:

```bash
# Clean US regions
aws-nuker nuke --regions "us-*" --services ec2 --force --yes

# Then clean EU regions
aws-nuker nuke --regions "eu-*" --services ec2 --force --yes
```

## Parallel Execution

### Enable Parallel Processing for Faster Cleanup

```bash
# Default parallel workers (5)
aws-nuker nuke \
  --regions us-east-1,us-west-2 \
  --services "*" \
  --force --yes \
  --parallel

# Custom number of workers
aws-nuker nuke \
  --regions "us-*" \
  --services "*" \
  --force --yes \
  --parallel --max-workers 10
```

**Note**: Parallel execution is faster but:
- Uses more API calls simultaneously
- May hit rate limits
- Less controlled (harder to stop mid-operation)
- Best for cleanup of many resources across regions

## Real-World Scenarios

### Scenario 1: Clean Up Test Environment

You have a test AWS account with resources across multiple services.

```bash
# Step 1: Dry run to see what will be deleted
aws-nuker nuke \
  --regions us-east-1 \
  --services "*" \
  --dry-run

# Step 2: Review the output, then execute
aws-nuker nuke \
  --regions us-east-1 \
  --services "*" \
  --force --yes
```

### Scenario 2: Clean Up After Development Sprint

You created resources during development and want to clean them up.

```bash
# Clean up specific services used in development
aws-nuker nuke \
  --regions us-east-1 \
  --services ec2,lambda,dynamodb,s3,apigateway \
  --force --yes
```

### Scenario 3: Regional Cleanup

You're moving from one region to another and want to clean the old region.

```bash
# Clean up all resources in old region
aws-nuker nuke \
  --regions eu-west-1 \
  --services "*" \
  --force --yes
```

### Scenario 4: Decommissioning AWS Account

You're shutting down an entire AWS account.

```bash
# Step 1: Dry run to estimate scope
aws-nuker nuke \
  --regions "*" \
  --services "*" \
  --dry-run

# Step 2: Review logs and audit trail

# Step 3: Execute cleanup
aws-nuker nuke \
  --regions "*" \
  --services "*" \
  --force --yes \
  --parallel --max-workers 10

# Note: Some global services (IAM, Route53) are only processed in us-east-1
```

### Scenario 5: Clean Up Specific Resource Types

You want to clean up only certain types of resources.

```bash
# Delete only databases
aws-nuker nuke \
  --regions us-east-1,us-west-2 \
  --services rds,dynamodb \
  --force --yes

# Delete only compute resources
aws-nuker nuke \
  --regions us-east-1 \
  --services ec2,lambda,ecs \
  --force --yes

# Delete only monitoring/logging
aws-nuker nuke \
  --regions us-east-1 \
  --services cloudwatch,logs \
  --force --yes
```

### Scenario 6: Cleanup with Audit Trail

You need detailed logs for compliance.

```bash
# Run cleanup
aws-nuker nuke \
  --regions us-east-1 \
  --services "*" \
  --force --yes

# Check logs
cat logs/aws_nuker_*.log

# Check audit trail
cat audit/audit_*.log
```

Sample audit log output:
```
2024-11-08 13:45:23 - ACTION=DELETE | TYPE=ec2 | ID=i-123 | REGION=us-east-1 | STATUS=SUCCESS
2024-11-08 13:45:24 - ACTION=DELETE | TYPE=s3 | ID=my-bucket | REGION=us-east-1 | STATUS=SUCCESS
2024-11-08 13:45:25 - ACTION=DELETE | TYPE=rds | ID=my-db | REGION=us-east-1 | STATUS=FAILED | DETAILS=DependencyViolation
```

### Scenario 7: Gradual Cleanup

You want to clean up gradually to avoid overwhelming the AWS API.

```bash
# Day 1: Clean up compute
aws-nuker nuke --regions us-east-1 --services ec2,lambda,ecs --force --yes

# Day 2: Clean up storage
aws-nuker nuke --regions us-east-1 --services s3,efs --force --yes

# Day 3: Clean up databases
aws-nuker nuke --regions us-east-1 --services rds,dynamodb --force --yes

# Day 4: Clean up networking
aws-nuker nuke --regions us-east-1 --services vpc,elb --force --yes

# Day 5: Clean up everything else
aws-nuker nuke --regions us-east-1 --services "*" --force --yes
```

## Output Examples

### Successful Cleanup Output

```
==================================================================================
AWS NUKER - CONFIGURATION
==================================================================================

Regions:
  - us-east-1

Services (3):
  ec2, lambda, s3

Options:
  Dry Run: False
  Force: True
  Parallel: False

==================================================================================
WARNING: THIS WILL DELETE RESOURCES PERMANENTLY!
==================================================================================

Type 'DELETE' to proceed: DELETE

Starting cleanup operation...

==================================================================================
AWS Nuker - Starting cleanup operation
==================================================================================
Regions: us-east-1
Services: 3 selected
Dry Run: False
Force: True
==================================================================================

INFO - Starting cleanup of ec2 in us-east-1
INFO - Found 10 ec2 resource(s)
INFO - Deleted ec2: i-1234567890abcdef0
INFO - Deleted ec2: vol-1234567890abcdef
INFO - Skipping default resource: sg-default
INFO - Completed ec2 cleanup in 45.2s - Deleted: 9, Failed: 0, Skipped: 1

INFO - Starting cleanup of lambda in us-east-1
INFO - Found 5 lambda resource(s)
INFO - Deleted lambda: my-function-1
INFO - Deleted lambda: my-function-2
INFO - Completed lambda cleanup in 12.3s - Deleted: 5, Failed: 0, Skipped: 0

INFO - Starting cleanup of s3 in us-east-1
INFO - Found 3 s3 resource(s)
INFO - Deleted s3: my-bucket-1
INFO - Deleted s3: my-bucket-2
INFO - Deleted s3: my-bucket-3
INFO - Completed s3 cleanup in 23.8s - Deleted: 3, Failed: 0, Skipped: 0

==================================================================================
EXECUTION SUMMARY
==================================================================================

+-------------------------+----------+
| Total Execution Time    | 81.30s   |
| Regions Processed       | 1        |
| Services Processed      | 3        |
| Total Resources Found   | 18       |
| Resources Deleted       | 17       |
| Resources Failed        | 0        |
| Resources Skipped       | 1        |
+-------------------------+----------+

Log Files:
  Main Log: logs/aws_nuker_20241108_134523.log
  Audit Log: audit/audit_20241108_134523.log
```

## Best Practices

1. **Always dry-run first**: Test with `--dry-run` before actual deletion
2. **Start small**: Begin with a single service in a single region
3. **Check logs**: Review audit logs after cleanup
4. **Backup important data**: Export any data you might need before cleanup
5. **Use version control**: Keep AWS Nuker configs in git if automating
6. **Monitor costs**: Watch for unexpected charges during/after cleanup
7. **Gradual deletion**: For large environments, clean up service by service
8. **Parallel with caution**: Use parallel execution only when needed
9. **Document actions**: Keep records of what was cleaned and when
10. **Test in dev first**: Always test the cleanup process in a dev environment

## Troubleshooting

### Resources Not Deleting

If resources aren't deleting, try:
```bash
# Use force flag to handle dependencies
aws-nuker nuke --regions us-east-1 --services ec2 --force --yes
```

### Rate Limiting

If you hit AWS API rate limits:
```bash
# Reduce parallel workers
aws-nuker nuke --regions us-east-1 --services "*" --parallel --max-workers 3

# Or use sequential execution (default)
aws-nuker nuke --regions us-east-1 --services "*" --force --yes
```

### Check What Failed

Review the audit log for failed deletions:
```bash
# Filter for failures
grep "FAILED" audit/audit_*.log

# Get details
cat audit/audit_*.log | grep -A 1 "FAILED"
```
