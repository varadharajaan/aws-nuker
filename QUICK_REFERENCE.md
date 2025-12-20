# AWS Nuker Tag-Based Features - Quick Reference

## CLI Commands Quick Reference

### Tag Discovery
```bash
# Discover all resources
aws-nuker discover-tags --region us-east-1

# Find resources with specific tags
aws-nuker discover-tags --tag-key env --tag-value dev

# Find untagged resources
aws-nuker discover-tags --show-untagged
```

### Policy Management
```bash
# List all policies
aws-nuker list-policies

# Show policy details
aws-nuker show-policy dev_cleanup
aws-nuker show-policy orphan_purge
aws-nuker show-policy cost_kill
aws-nuker show-policy storage_cleanup
```

### Cleanup Operations
```bash
# Get cleanup suggestions
aws-nuker suggest-cleanup --region us-east-1

# Delete by tag (dry run)
aws-nuker nuke-by-tag --tag-key env --tag-value dev --dry-run

# Delete by tag (execute)
aws-nuker nuke-by-tag --tag-key env --tag-value dev --yes
```

## Policy Templates

| Policy | Targets | Age | Cost Approval | Soft Delete | Snapshots |
|--------|---------|-----|---------------|-------------|-----------|
| **Dev Cleanup** | env=dev/test/staging | 7+ days | > $100 | 7 days | > 10GB |
| **Orphan Purge** | Untagged, no owner | 30+ days | > $10 | 7 days | All |
| **Cost Kill** | High-cost unused | 30+ days | > $500 | 14 days | Always |
| **Storage Cleanup** | Large storage (>100GB) | 90+ days | > $50 | No | > 500GB |

## Python API Quick Reference

### Tag Manager
```python
from aws_nuker.tag_manager import TagManager, TagFilter

# Initialize
tm = TagManager(region="us-east-1")

# Discover
result = tm.discover_resources()

# Filter by tags
resources = tm.get_resources_by_tags({"env": "dev"})

# Get untagged
untagged = tm.filter_untagged_resources(result)

# Get suggestions
suggestions = tm.suggest_cleanup_targets()
```

### Policy Templates
```python
from aws_nuker.policy_templates import PolicyTemplates, PolicyType

# Get predefined policy
policy = PolicyTemplates.dev_cleanup()
policy = PolicyTemplates.orphan_purge()
policy = PolicyTemplates.cost_kill()
policy = PolicyTemplates.storage_cleanup()

# Create custom policy
custom = PolicyTemplates.create_custom_policy(
    name="Custom Policy",
    description="My policy",
    tag_filters={"env": "dev"},
    age_threshold_days=7
)

# Export to JSON
json_str = policy.to_json()
```

### Approval Gate
```python
from aws_nuker.approval_gate import ApprovalGate

# Initialize
ag = ApprovalGate()

# Create request
request = ag.create_request(
    policy=policy,
    resources=resources,
    estimated_cost_usd=250.0,
    requester="user@company.com"
)

# Approve
ag.approve_request(
    request_id=request.request_id,
    approver="manager@company.com"
)

# Reject
ag.reject_request(
    request_id=request.request_id,
    approver="manager@company.com",
    reason="Not approved"
)

# Get pending
pending = ag.get_pending_requests()

# Get summary
summary = ag.generate_approval_summary()
```

### Notification Manager
```python
from aws_nuker.notification_manager import NotificationManager

# Initialize
nm = NotificationManager(
    email_addresses=["team@company.com"],
    slack_webhook_url="https://hooks.slack.com/...",
    sns_topic_arn="arn:aws:sns:..."
)

# Cleanup start
nm.notify_cleanup_start(
    policy_name="Dev Cleanup",
    resource_count=150,
    regions=["us-east-1"],
    services=["ec2", "s3"]
)

# Cleanup complete
nm.notify_cleanup_complete(
    policy_name="Dev Cleanup",
    deleted_count=148,
    failed_count=2,
    duration_seconds=245.5
)

# Approval required
nm.notify_approval_required(
    request_id="req_123",
    policy_name="Cost Kill",
    resource_count=50,
    estimated_cost=1250.0
)
```

## Tag Filter Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `equals` | Exact match | `env=dev` |
| `starts_with` | Prefix match | `project=test-*` |
| `contains` | Substring match | `*dev*` |
| `regex` | Regular expression | `env=.*dev.*` |
| `exists` | Tag key exists | Has `owner` tag |
| `not_exists` | Tag key missing | No `owner` tag |

## Common Workflows

### 1. Weekly Dev Cleanup
```bash
# 1. Discover
aws-nuker discover-tags --tag-key env --tag-value dev

# 2. Preview
aws-nuker nuke-by-tag --tag-key env --tag-value dev --dry-run

# 3. Execute
aws-nuker nuke-by-tag --tag-key env --tag-value dev --yes
```

### 2. Orphan Resource Audit
```bash
# Find untagged
aws-nuker discover-tags --show-untagged

# Get suggestions
aws-nuker suggest-cleanup
```

### 3. Cost Optimization
```bash
# Suggestions
aws-nuker suggest-cleanup --min-resources 10

# Review policy
aws-nuker show-policy cost_kill

# Execute (requires Python integration)
```

## IAM Permissions Required

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

## Safety Checklist

- [ ] Start with `--dry-run`
- [ ] Review preview output
- [ ] Check estimated costs
- [ ] Verify tag filters are correct
- [ ] Enable soft delete for safety
- [ ] Configure snapshots for critical data
- [ ] Set up approval gates for prod
- [ ] Enable notifications
- [ ] Test in non-prod first
- [ ] Review audit logs after execution

## Troubleshooting

| Issue | Solution |
|-------|----------|
| No resources found | Check tag filters and region |
| Permission denied | Add required IAM permissions |
| Email not sending | Verify SES sender email |
| Slack webhook failed | Check webhook URL |
| Approval not working | Review cost thresholds |

## Support & Documentation

- Full Guide: `docs/TAG_BASED_CLEANUP.md`
- Feature Summary: `TAG_BASED_FEATURES.md`
- API Reference: Python docstrings
- Examples: `examples/` directory

## Version

Tag-based features added in **v2.0.0** (2025-01-09)
