# AWS Nuker Tag-Based Management Guide

## Overview

AWS Nuker now includes comprehensive tag-based resource management with intelligent cleanup policies, approval workflows, and notification systems.

## Key Features

### 1. Tag Discovery & Grouping

Discover and group resources by tags across your AWS environment:

```bash
# Discover all resources
aws-nuker discover-tags --region us-east-1

# Find resources with specific tags
aws-nuker discover-tags --tag-key env --tag-value dev

# Find untagged resources (compliance cleanup)
aws-nuker discover-tags --show-untagged

# Pattern matching with wildcards
aws-nuker discover-tags --tag-key "project" --tag-value "test-*"
```

**Features:**
- Automatic resource grouping by tag combinations
- Untagged resource detection
- Pattern matching (wildcards, regex)
- Multi-condition filtering (AND/OR logic)
- Cost and age analysis per tag group

### 2. Policy Templates

Pre-built cleanup policies for common scenarios:

```bash
# List all policy templates
aws-nuker list-policies

# View policy details
aws-nuker show-policy dev_cleanup
aws-nuker show-policy orphan_purge
aws-nuker show-policy cost_kill
aws-nuker show-policy storage_cleanup
```

#### Available Templates:

**Dev Cleanup Policy**
- Targets: `env=dev`, `env=test`, `env=staging`
- Age threshold: 7+ days unused
- Soft delete: Yes (7-day recovery)
- Snapshots: Databases/storage > 10GB
- Approval: Required for costs > $100

**Orphan Purge Policy**
- Targets: Untagged resources, no owner tag
- Age threshold: 30+ days
- Soft delete: Yes (7-day recovery)
- Snapshots: All volumes/databases
- Approval: Required for costs > $10
- Focus: Orphaned volumes, snapshots, elastic IPs

**Cost Kill Policy**
- Targets: High-cost unused resources
- Age threshold: 30+ days
- Cost threshold: $50+
- Soft delete: Yes (14-day recovery)
- Snapshots: Always
- Approval: Required for costs > $500
- Focus: Stopped instances, unused databases

**Storage Cleanup Policy**
- Targets: Large storage (> 100GB)
- Age threshold: 90+ days
- Snapshots: Large datasets (> 500GB)
- Approval: Required for costs > $50
- Focus: Old backups, snapshots, large buckets

### 3. Tag-Based Deletion

Delete resources by tag conditions:

```bash
# Preview deletion
aws-nuker nuke-by-tag --tag-key env --tag-value dev --dry-run

# Delete resources with confirmation
aws-nuker nuke-by-tag --tag-key env --tag-value dev

# Force delete without confirmation
aws-nuker nuke-by-tag --tag-key env --tag-value dev --yes

# Multiple regions
aws-nuker nuke-by-tag --region us-east-1 --tag-key project --tag-value temp-*
```

**Advanced Filtering:**

```python
# In Python code
from aws_nuker.tag_manager import TagManager, TagFilter

tag_manager = TagManager(region="us-east-1")

# AND logic - all conditions must match
resources = tag_manager.get_resources_by_tags(
    {"env": "dev", "region": "us-east-1"},
    match_all=True
)

# OR logic - any condition can match
resources = tag_manager.get_resources_by_tags(
    {"env": "dev", "env": "test"},
    match_all=False
)
```

### 4. Intelligent Cleanup Suggestions

Get AI-powered cleanup suggestions:

```bash
# Get cleanup suggestions
aws-nuker suggest-cleanup --region us-east-1

# Adjust minimum resource threshold
aws-nuker suggest-cleanup --min-resources 10
```

**Suggestion Criteria:**
- Dev/test environment detection
- Large resource groups
- Temporary tag detection
- Age analysis
- Cost optimization opportunities

### 5. Approval Workflow

Enterprise-grade approval system for controlled deletions:

```python
from aws_nuker.approval_gate import ApprovalGate
from aws_nuker.policy_templates import PolicyTemplates

# Initialize approval gate
approval_gate = ApprovalGate()

# Create approval request
policy = PolicyTemplates.dev_cleanup()
request = approval_gate.create_request(
    policy=policy,
    resources=resources_to_delete,
    estimated_cost_usd=250.0,
    requester="john.doe@company.com"
)

# Approve request
approval_gate.approve_request(
    request_id=request.request_id,
    approver="manager@company.com",
    comment="Approved for Q4 cleanup"
)

# Reject request
approval_gate.reject_request(
    request_id=request.request_id,
    approver="manager@company.com",
    reason="Still in use by QA team"
)
```

**Approval Features:**
- Auto-approval for low-cost resources
- Production environment protection
- Cost-based thresholds
- Custom approval rules
- Approval history tracking

### 6. Notifications

Multi-channel notification support:

```python
from aws_nuker.notification_manager import NotificationManager

# Initialize with channels
notifier = NotificationManager(
    email_addresses=["team@company.com"],
    slack_webhook_url="https://hooks.slack.com/...",
    sns_topic_arn="arn:aws:sns:us-east-1:123456789012:aws-nuker-alerts"
)

# Notify cleanup start
notifier.notify_cleanup_start(
    policy_name="Dev Cleanup",
    resource_count=150,
    regions=["us-east-1", "us-west-2"],
    services=["ec2", "s3", "rds"]
)

# Notify completion
notifier.notify_cleanup_complete(
    policy_name="Dev Cleanup",
    deleted_count=148,
    failed_count=2,
    duration_seconds=245.5
)

# Notify approval required
notifier.notify_approval_required(
    request_id="req_20250109_143022_0",
    policy_name="Cost Kill",
    resource_count=50,
    estimated_cost=1250.0
)
```

**Supported Channels:**
- Email (via Amazon SES)
- Slack (via webhooks)
- SNS (AWS Simple Notification Service)

## Advanced Use Cases

### 1. Delete All Dev Resources

```bash
# Step 1: Discover dev resources
aws-nuker discover-tags --tag-key env --tag-value dev

# Step 2: Preview deletion
aws-nuker nuke-by-tag --tag-key env --tag-value dev --dry-run

# Step 3: Execute with approval
aws-nuker nuke-by-tag --tag-key env --tag-value dev
```

### 2. Cleanup Orphaned Resources

```python
from aws_nuker.tag_manager import TagManager
from aws_nuker.policy_templates import PolicyTemplates

# Discover untagged resources
tag_manager = TagManager(region="us-east-1")
result = tag_manager.discover_resources()
untagged = tag_manager.filter_untagged_resources(result)

print(f"Found {len(untagged)} untagged resources")

# Apply orphan purge policy
policy = PolicyTemplates.orphan_purge()
# ... apply policy with approval workflow
```

### 3. Multi-Condition Tag Cleanup

```bash
# Resources with env=dev AND NOT protected=true
# (requires Python code for complex logic)
```

```python
from aws_nuker.tag_manager import TagManager, TagFilter

tag_manager = TagManager(region="us-east-1")

# Create complex filters
filters = [
    TagFilter(key="env", value="dev", operator="equals"),
    TagFilter(key="protected", operator="not_exists")
]

# Discover with filters
result = tag_manager.discover_resources(tag_filters=filters)
```

### 4. Bulk Tagging Before Deletion

```python
# Mark resources for deletion first (safety measure)
import boto3

ec2 = boto3.client('ec2', region_name='us-east-1')

# Tag resources
ec2.create_tags(
    Resources=resource_ids,
    Tags=[
        {'Key': 'marked_for_deletion', 'Value': 'true'},
        {'Key': 'deletion_date', 'Value': '2025-01-15'}
    ]
)

# Wait 7 days, then delete
aws-nuker nuke-by-tag --tag-key marked_for_deletion --tag-value true
```

## Configuration Examples

### JSON Policy Export

```bash
# Export policy to JSON
aws-nuker show-policy dev_cleanup > dev_cleanup_policy.json

# Modify and import (requires Python)
```

```python
from aws_nuker.policy_templates import CleanupPolicy

# Load custom policy
with open('custom_policy.json') as f:
    policy = CleanupPolicy.from_json(f.read())
```

### Custom Policy Creation

```python
from aws_nuker.policy_templates import PolicyTemplates

# Create custom policy
custom_policy = PolicyTemplates.create_custom_policy(
    name="Weekend Dev Cleanup",
    description="Clean dev resources on weekends",
    tag_filters={
        "AND": [
            {"env": "dev"},
            {"auto_cleanup": "true"}
        ]
    },
    age_threshold_days=3,
    require_approval=False,
    soft_delete=True,
    soft_delete_ttl_days=5,
    create_snapshot=True,
    snapshot_threshold_gb=50,
    included_services=["ec2", "rds", "dynamodb"],
    notification_channels=["slack"]
)
```

## Safety Features

### Soft Delete

Resources marked for deletion but recoverable for TTL period:

- **7-day TTL** (dev cleanup, orphan purge)
- **14-day TTL** (cost kill)
- Resources tagged with `deletion_scheduled=<date>`
- Final deletion via scheduled job

### Snapshot Before Delete

Automatic snapshots for critical data:

- **RDS databases**: All instances before deletion
- **EC2 volumes**: Volumes > threshold GB
- **DynamoDB tables**: Point-in-time recovery enabled
- **S3 buckets**: Versioning preserved

### Approval Gates

Require approval for:
- Production environment resources
- High-cost resources (> threshold)
- Large-scale deletions (> X resources)
- Custom rules via Python functions

## Monitoring & Audit

### Audit Logs

All operations logged to `audit/` directory:

```
audit/
├── audit_20250109_140000.log
├── tag_discovery_20250109_141500.log
└── approval_history.json
```

### Export Options

```bash
# Export discovery results
aws-nuker discover-tags --region us-east-1 > discovery_results.txt

# Export approval history (requires Python)
```

```python
from aws_nuker.approval_gate import ApprovalGate

approval_gate = ApprovalGate()
summary = approval_gate.generate_approval_summary()
print(json.dumps(summary, indent=2))
```

## Best Practices

1. **Always start with dry-run**
   ```bash
   aws-nuker discover-tags --show-untagged
   aws-nuker nuke-by-tag --tag-key env --tag-value dev --dry-run
   ```

2. **Use soft delete for safety**
   - Enable 7+ day TTL
   - Review before final deletion

3. **Create snapshots for critical data**
   - Set appropriate thresholds
   - Test restoration procedures

4. **Set up approval workflows**
   - Require approval for prod
   - Set cost thresholds
   - Multi-level approvals for large deletions

5. **Configure notifications**
   - Alert on deletion starts
   - Report completion status
   - Escalate failures

6. **Tag everything**
   - Consistent tagging strategy
   - Use automation for tagging
   - Regular tag compliance audits

## Troubleshooting

### No Resources Found

```bash
# Check tag discovery
aws-nuker discover-tags --region us-east-1

# Verify tag filters
aws-nuker discover-tags --tag-key env --tag-value dev
```

### Permissions Issues

Ensure IAM policy includes:
- `tag:GetResources`
- `tag:GetTagKeys`
- `tag:GetTagValues`
- `resource-groups:*`

### Notification Failures

- **Email**: Verify SES sender email is verified
- **Slack**: Check webhook URL is valid
- **SNS**: Confirm topic ARN and permissions

## API Reference

See Python modules:
- `aws_nuker.tag_manager` - Tag discovery and filtering
- `aws_nuker.policy_templates` - Pre-built cleanup policies
- `aws_nuker.approval_gate` - Approval workflow management
- `aws_nuker.notification_manager` - Multi-channel notifications

## Examples Repository

See `examples/` directory for:
- Custom policy templates
- Tag-based automation scripts
- Approval workflow integrations
- Notification configurations
