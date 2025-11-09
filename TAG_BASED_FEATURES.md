# AWS Nuker Tag-Based Features - Implementation Summary

## Overview

This update adds comprehensive tag-based resource management capabilities to AWS Nuker, including intelligent cleanup policies, approval workflows, notification systems, and advanced tag filtering.

## New Features Implemented

### 1. Tag Discovery & Management (`tag_manager.py`)

**Core Functionality:**
- **Tag Discovery**: Discover all AWS resources and their tags using Resource Groups Tagging API
- **Tag Grouping**: Automatically group resources by tag combinations
- **Pattern Matching**: Support for wildcards, regex, and complex tag filters
- **Untagged Detection**: Identify resources without tags for compliance cleanup
- **Intelligent Suggestions**: AI-powered cleanup recommendations based on tags, age, and usage patterns

**Tag Filters Support:**
- `equals` - Exact tag value match
- `starts_with` - Prefix matching
- `contains` - Substring matching  
- `regex` - Regular expression matching
- `exists` - Check if tag key exists
- `not_exists` - Check if tag key doesn't exist

**Key Classes:**
- `TagFilter` - Represents a tag-based filter condition
- `TagGroup` - Groups resources with similar tags
- `TagDiscoveryResult` - Results from tag discovery operations
- `TagManager` - Main class for tag operations

**Usage Examples:**
```python
from aws_nuker.tag_manager import TagManager

# Discover all resources
tag_manager = TagManager(region="us-east-1")
result = tag_manager.discover_resources()

# Filter by tag pattern
resources = tag_manager.get_resources_by_tags({"env": "dev"})

# Get cleanup suggestions
suggestions = tag_manager.suggest_cleanup_targets(min_resource_count=5)
```

### 2. Policy Templates (`policy_templates.py`)

**Pre-built Policies:**

1. **Dev Cleanup Policy**
   - Targets: `env=dev|test|staging`
   - Age: 7+ days
   - Soft delete: 7-day TTL
   - Snapshots: Databases/storage > 10GB
   - Approval: > $100

2. **Orphan Purge Policy**
   - Targets: Untagged resources, no owner
   - Age: 30+ days
   - Soft delete: 7-day TTL
   - Snapshots: All volumes/databases
   - Approval: > $10

3. **Cost Kill Policy**
   - Targets: High-cost unused resources
   - Age: 30+ days, Cost: $50+
   - Soft delete: 14-day TTL
   - Snapshots: Always
   - Approval: > $500

4. **Storage Cleanup Policy**
   - Targets: Large storage (> 100GB)
   - Age: 90+ days
   - Snapshots: > 500GB datasets
   - Approval: > $50

**Policy Features:**
- JSON export/import
- Custom policy creation
- Tag-based filtering (AND/OR logic)
- Age and cost thresholds
- Soft delete with TTL
- Snapshot automation
- Approval gates
- Notification configuration

**Key Classes:**
- `PolicyType` - Enum for policy types
- `CleanupPolicy` - Represents a cleanup policy
- `PolicyTemplates` - Factory for predefined policies

### 3. Approval Workflow (`approval_gate.py`)

**Approval System Features:**
- **Request Management**: Create, approve, reject approval requests
- **Auto-Approval**: Configurable rules for automatic approval
- **Cost Thresholds**: Approval required above cost limits
- **Environment Protection**: Block prod deletions without approval
- **Approval History**: Complete audit trail
- **Custom Rules**: Extensible approval logic

**Approval Flow:**
1. Create request with policy + resources + cost
2. Check auto-approval rules
3. If manual approval needed: pending state
4. Approver reviews and approves/rejects
5. History maintained for audit

**Key Classes:**
- `ApprovalStatus` - Enum for request status
- `ApprovalRequest` - Represents an approval request
- `ApprovalGate` - Manages approval workflow

**Usage:**
```python
from aws_nuker.approval_gate import ApprovalGate

approval_gate = ApprovalGate()

# Create request
request = approval_gate.create_request(
    policy=policy,
    resources=resources,
    estimated_cost_usd=250.0,
    requester="user@company.com"
)

# Approve
approval_gate.approve_request(
    request_id=request.request_id,
    approver="manager@company.com"
)
```

### 4. Notification System (`notification_manager.py`)

**Multi-Channel Support:**
- **Email** - via Amazon SES
- **Slack** - via webhooks
- **SNS** - AWS Simple Notification Service

**Notification Types:**
- Cleanup start
- Cleanup completion (with results)
- Approval required
- Custom messages

**Features:**
- Severity levels (info, warning, error, critical)
- Channel selection per notification
- Metadata attachment
- Color-coded Slack messages
- HTML/plain text email support

**Key Classes:**
- `NotificationMessage` - Represents a notification
- `NotificationManager` - Manages multi-channel notifications

**Usage:**
```python
from aws_nuker.notification_manager import NotificationManager

notifier = NotificationManager(
    email_addresses=["team@company.com"],
    slack_webhook_url="https://hooks.slack.com/...",
    sns_topic_arn="arn:aws:sns:..."
)

notifier.notify_cleanup_start(
    policy_name="Dev Cleanup",
    resource_count=150,
    regions=["us-east-1"],
    services=["ec2", "s3"]
)
```

### 5. Enhanced CLI Commands (`cli.py`)

**New Commands:**

1. **`discover-tags`** - Discover and group resources by tags
   ```bash
   aws-nuker discover-tags --region us-east-1
   aws-nuker discover-tags --tag-key env --tag-value dev
   aws-nuker discover-tags --show-untagged
   ```

2. **`list-policies`** - List available policy templates
   ```bash
   aws-nuker list-policies
   ```

3. **`show-policy`** - Show policy details
   ```bash
   aws-nuker show-policy dev_cleanup
   aws-nuker show-policy orphan_purge
   ```

4. **`suggest-cleanup`** - Get intelligent cleanup suggestions
   ```bash
   aws-nuker suggest-cleanup --region us-east-1
   aws-nuker suggest-cleanup --min-resources 10
   ```

5. **`nuke-by-tag`** - Delete resources by tag
   ```bash
   aws-nuker nuke-by-tag --tag-key env --tag-value dev --dry-run
   aws-nuker nuke-by-tag --tag-key env --tag-value dev --yes
   ```

## Implementation Statistics

### Files Created:
- `aws_nuker/tag_manager.py` - 380 lines
- `aws_nuker/policy_templates.py` - 245 lines
- `aws_nuker/approval_gate.py` - 245 lines
- `aws_nuker/notification_manager.py` - 290 lines
- `docs/TAG_BASED_CLEANUP.md` - 390 lines

### Files Modified:
- `aws_nuker/cli.py` - Added 270 lines (new commands)
- `requirements.txt` - Added `requests` dependency

### Total New Code:
- **Python Code**: ~1,160 lines
- **Documentation**: ~390 lines
- **Total**: ~1,550 lines

## Architecture

### Component Diagram:

```
┌─────────────────┐
│   CLI (click)   │
└────────┬────────┘
         │
    ┌────┴─────┐
    │          │
┌───▼────┐ ┌──▼──────────┐
│ Policy │ │ Tag Manager │
│Template│ │             │
└───┬────┘ └──┬──────────┘
    │         │
    │    ┌────▼─────────┐
    │    │  Discovery   │
    │    │  & Grouping  │
    │    └──────────────┘
    │
┌───▼───────────┐
│ Approval Gate │
└───┬───────────┘
    │
┌───▼────────────┐
│  Notification  │
│    Manager     │
└────────────────┘
```

### Data Flow:

```
1. Tag Discovery
   ├─> Resource Groups Tagging API
   ├─> Group by tags
   └─> Filter & analyze

2. Policy Selection
   ├─> Choose template or custom
   ├─> Apply tag filters
   └─> Identify target resources

3. Approval Workflow
   ├─> Create request
   ├─> Check auto-approval rules
   ├─> Manual approval if needed
   └─> Record decision

4. Execution
   ├─> Soft delete (if enabled)
   ├─> Create snapshots (if threshold met)
   ├─> Delete resources
   └─> Send notifications

5. Audit
   ├─> Log all operations
   ├─> Track approvals
   └─> Export results
```

## Use Cases

### 1. Development Environment Cleanup

**Scenario**: Cleanup dev/test resources every weekend

```bash
# Discover dev resources
aws-nuker discover-tags --tag-key env --tag-value dev

# Preview with dev policy
aws-nuker show-policy dev_cleanup

# Execute cleanup
aws-nuker nuke-by-tag --tag-key env --tag-value dev --dry-run
aws-nuker nuke-by-tag --tag-key env --tag-value dev --yes
```

**Benefits:**
- Automated identification of dev resources
- Soft delete with 7-day recovery
- Snapshots for databases
- Approval for high-cost resources

### 2. Orphaned Resource Cleanup

**Scenario**: Find and remove untagged/orphaned resources

```bash
# Find untagged resources
aws-nuker discover-tags --show-untagged

# Apply orphan purge policy (via Python)
```

**Benefits:**
- Compliance enforcement (all resources must be tagged)
- Cost reduction (remove forgotten resources)
- Complete audit trail

### 3. Cost Optimization

**Scenario**: Remove expensive unused resources

```bash
# Get cleanup suggestions
aws-nuker suggest-cleanup --min-resources 5

# Apply cost kill policy
# (requires Python integration)
```

**Benefits:**
- Identifies high-cost resources
- Focuses on stopped/unused instances
- Requires approval for large deletions
- Creates snapshots before deletion

### 4. Multi-Tag Cleanup

**Scenario**: Delete resources matching complex conditions

```python
# env=dev AND project=test-* AND NOT protected=true
from aws_nuker.tag_manager import TagManager, TagFilter

tag_manager = TagManager(region="us-east-1")
filters = [
    TagFilter(key="env", value="dev", operator="equals"),
    TagFilter(key="project", value="test-.*", operator="regex"),
    TagFilter(key="protected", operator="not_exists")
]

result = tag_manager.discover_resources(tag_filters=filters)
```

**Benefits:**
- Surgical precision in resource selection
- Complex business logic support
- Prevents accidental deletion of protected resources

## Safety Features

### 1. Dry Run Mode
- Preview all operations
- No actual deletions
- Full report of what would be deleted

### 2. Soft Delete
- Resources tagged for deletion first
- Configurable TTL (7/14 days)
- Recovery window before permanent deletion
- Scheduled final cleanup

### 3. Snapshot Automation
- Pre-deletion snapshots for critical data
- Configurable size thresholds
- Automated naming with timestamps
- Retention policy support

### 4. Approval Gates
- Cost-based approval thresholds
- Environment protection (prod requires approval)
- Multi-level approval support
- Complete audit history

### 5. Notifications
- Alert on operation start
- Report completion status
- Escalate failures
- Approval request notifications

## Integration Points

### AWS Services Used:
- **Resource Groups Tagging API** - Tag discovery
- **Amazon SES** - Email notifications
- **Amazon SNS** - Push notifications
- **AWS SDK (boto3)** - Resource operations

### External Integrations:
- **Slack** - Webhook notifications
- **Custom approval systems** - Extensible approval rules
- **ITSM tools** - Via notification webhooks

## Configuration

### Required IAM Permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "tag:GetResources",
        "tag:GetTagKeys",
        "tag:GetTagValues",
        "resource-groups:*"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "ses:SendEmail",
        "sns:Publish"
      ],
      "Resource": "*"
    }
  ]
}
```

### Environment Variables:

```bash
# Notification configuration
export AWS_NUKER_EMAIL="team@company.com"
export AWS_NUKER_SLACK_WEBHOOK="https://hooks.slack.com/..."
export AWS_NUKER_SNS_TOPIC="arn:aws:sns:..."

# Approval configuration
export AWS_NUKER_APPROVAL_THRESHOLD=100
export AWS_NUKER_AUTO_APPROVE_DEV=true
```

## Testing

### Unit Tests (to be implemented):
- Tag filter matching logic
- Policy template validation
- Approval workflow state machine
- Notification delivery

### Integration Tests (to be implemented):
- Tag discovery against test account
- Policy execution with dry-run
- Approval gate end-to-end
- Multi-channel notifications

## Performance Considerations

### Tag Discovery:
- Uses pagination for large result sets
- Caches tag groups during session
- Parallel discovery across regions (future)

### Resource Deletion:
- Batch operations where supported
- Rate limiting to avoid throttling
- Retry logic with exponential backoff

### Notifications:
- Async delivery (doesn't block operations)
- Batch notifications for large-scale operations
- Fallback channels on primary failure

## Future Enhancements

### Planned Features:
1. **Cost Analysis Integration** - AWS Cost Explorer integration for accurate cost estimates
2. **Scheduled Policies** - Cron-based policy execution
3. **Tag Recommendations** - ML-based tag suggestions for untagged resources
4. **Resource Relationships** - Dependency graph visualization
5. **Undo Functionality** - Restore from soft delete
6. **Policy Marketplace** - Community-contributed policies
7. **Dashboard** - Web UI for monitoring and management
8. **Terraform Integration** - Sync with IaC state

### Nice-to-Have:
- Slack bot for approvals
- Microsoft Teams integration
- PagerDuty escalations
- JIRA ticket integration
- Cost savings reporting
- Compliance reporting

## Migration Guide

### For Existing Users:

1. **Update dependencies**:
   ```bash
   pip install -r requirements.txt --upgrade
   ```

2. **No breaking changes** - All existing commands work as before

3. **New features are opt-in**:
   ```bash
   # Old way still works
   aws-nuker nuke --regions us-east-1 --services ec2
   
   # New tag-based way
   aws-nuker nuke-by-tag --tag-key env --tag-value dev
   ```

4. **IAM permissions** - Add tag: and resource-groups: permissions

## Conclusion

This implementation provides enterprise-grade tag-based resource management for AWS Nuker, enabling:

- **Intelligent cleanup** through policy templates
- **Safe operations** via approval workflows and soft delete
- **Visibility** through comprehensive notifications
- **Flexibility** with custom policies and tag filters
- **Compliance** through complete audit trails

The modular architecture allows easy extension and integration with existing workflows, making AWS Nuker a complete solution for AWS resource lifecycle management.
