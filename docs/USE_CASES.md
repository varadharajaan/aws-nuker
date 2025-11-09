# AWS Nuker - Use Cases and User Guide

## Table of Contents
1. [Common Use Cases](#common-use-cases)
2. [User Stories](#user-stories)
3. [Step-by-Step Workflows](#step-by-step-workflows)
4. [Best Practices](#best-practices)
5. [Safety Guidelines](#safety-guidelines)

## Common Use Cases

### 1. Development Environment Cleanup
**Scenario:** Clean up all development resources at the end of a sprint

**Steps:**
1. Navigate to Dashboard
2. Select regions: `us-east-1`, `us-west-2`
3. Select services: `all`
4. Enter tag filter: `env=dev`
5. Click "Discover Resources"
6. Review the 42 resources found
7. Navigate to "Dry Run & Delete"
8. Run dry run to preview deletion
9. Confirm and execute deletion

**Result:** All dev-tagged resources deleted, saving ~$500/month

### 2. Orphaned Resource Cleanup
**Scenario:** Find and remove resources without proper tagging

**Steps:**
1. Navigate to Dashboard
2. Select all regions
3. Select services: `ec2-instances`, `ec2-volumes`, `rds-instances`
4. Enter tag filter: `!owner` (resources without owner tag)
5. Discover resources
6. Review orphaned resources
7. Use dry run to verify
8. Delete orphaned resources

**Result:** Identified 127 untagged resources, deleted after verification

### 3. Large Storage Cleanup
**Scenario:** Remove old S3 buckets and EBS snapshots

**Steps:**
1. Select regions where storage exists
2. Select services: `s3`, `ec2-snapshots`, `ec2-volumes`
3. Optional: Use tag filter for specific projects: `project=archived-*`
4. Discover and review storage resources
5. Check total size and cost in dashboard
6. Run dry run
7. Execute deletion after confirmation

**Result:** Freed 5TB of storage, saving $250/month

### 4. Multi-Account Cleanup
**Scenario:** Clean up resources across multiple AWS accounts

**Steps:**
1. Configure AWS credentials for first account
2. Run discovery and cleanup
3. Switch AWS credentials to second account
4. Repeat discovery and cleanup
5. Review consolidated reports

**Result:** Cleaned up 3 AWS accounts systematically

### 5. Compliance Cleanup
**Scenario:** Ensure all resources comply with tagging policy

**Steps:**
1. Use tag filter: `!compliance` or `!cost-center`
2. Discover non-compliant resources
3. Export list for review
4. Either add tags or delete resources
5. Run periodic audits

**Result:** 100% tagging compliance achieved

## User Stories

### As a DevOps Engineer
"I want to quickly clean up all resources in my development environment so I can reduce AWS costs when features are not actively being developed."

**Solution:** Use tag-based filtering with `env=dev` to identify and delete all development resources in one operation.

### As a Cloud Architect
"I need to identify orphaned resources that are no longer attached to any project so I can eliminate waste and improve resource management."

**Solution:** Use the `!project` tag filter to find resources without project tags, review them, and clean up.

### As a Cost Optimization Specialist
"I want to generate reports showing how much money we've saved by cleaning up unused resources so I can demonstrate ROI."

**Solution:** Use the Reports page to track deletions and estimated cost savings over time.

### As a Security Engineer
"I need to ensure that all temporary testing resources are removed promptly to minimize security exposure."

**Solution:** Schedule regular cleanups using tag filters like `temporary=true` or `ttl=*` to automatically remove temporary resources.

### As a Team Lead
"I want to safely test resource deletion before executing it so I don't accidentally delete production resources."

**Solution:** Always use the dry run feature first to preview exactly what will be deleted, then confirm deletion after review.

## Step-by-Step Workflows

### Workflow 1: First-Time Setup and Discovery

1. **Install and Setup**
   ```bash
   # Clone repository
   git clone https://github.com/varadharajaan/aws-nuker.git
   cd aws-nuker
   
   # Install backend dependencies
   pip install -r requirements.txt
   
   # Install frontend dependencies
   cd web
   npm install
   ```

2. **Configure AWS Credentials**
   ```bash
   # Configure AWS CLI
   aws configure
   
   # Or set environment variables
   export AWS_ACCESS_KEY_ID=your_access_key
   export AWS_SECRET_ACCESS_KEY=your_secret_key
   export AWS_DEFAULT_REGION=us-east-1
   ```

3. **Start the Application**
   ```bash
   # Terminal 1: Start backend
   python3 api_server.py
   
   # Terminal 2: Start frontend
   cd web
   npm run dev
   ```

4. **Access the Dashboard**
   - Open browser to `http://localhost:3000`
   - View the dashboard overview
   - Check that services and regions are loaded

5. **Run First Discovery**
   - Select 1-2 regions to start
   - Select a few safe services (e.g., CloudWatch Logs)
   - Add tag filter if needed
   - Click "Discover Resources"
   - Review results

### Workflow 2: Safe Resource Deletion

1. **Configure Filters**
   - Select target regions
   - Select specific services
   - Enter tag filters (e.g., `env=dev,!protected`)

2. **Discover Resources**
   - Click "Discover Resources" on Dashboard
   - Review total count and breakdown
   - Check charts for distribution
   - Examine resource table for details

3. **Navigate to Dry Run**
   - Click "Dry Run & Delete" in navigation
   - Filters are preserved from dashboard

4. **Run Dry Run**
   - Click "Run Dry Run" button
   - Wait for simulation to complete
   - Review dry run results table
   - Check resource count matches expectations

5. **Review Before Deletion**
   - Verify each resource in the list
   - Check tags to ensure correct targeting
   - Confirm regions are correct
   - Double-check no production resources are included

6. **Execute Deletion**
   - Click "Execute Deletion" button
   - Read warning in confirmation modal
   - Confirm resource count is expected
   - Click "Delete Now" to proceed

7. **Monitor Results**
   - Watch deletion progress
   - Check success/failure counts
   - Review any errors
   - Note any resources that couldn't be deleted

8. **Verify Deletion**
   - Run discovery again with same filters
   - Confirm resources are gone
   - Check AWS Console if needed

### Workflow 3: Scheduled Cleanup Automation

1. **Create Policy Template** (Future Feature)
   ```json
   {
     "name": "weekly-dev-cleanup",
     "schedule": "0 0 * * 0",
     "filters": {
       "regions": ["us-east-1", "us-west-2"],
       "services": ["all"],
       "tags": "env=dev,temporary=true"
     },
     "dry_run": true,
     "notifications": {
       "slack": "https://hooks.slack.com/...",
       "email": "team@example.com"
     }
   }
   ```

2. **Review and Approve**
   - Automated dry run results sent to team
   - Team reviews scheduled deletion
   - Approver confirms or rejects

3. **Execution**
   - Approved deletions execute automatically
   - Results logged and reported
   - Cost savings calculated

## Best Practices

### 1. Always Use Dry Run First
- **Never** execute deletion without running dry run
- Review every resource in the dry run results
- Verify tag filters are working as expected
- Check that protected resources are excluded

### 2. Use Descriptive Tags
```
Good:
- env=production
- env=development
- owner=team-platform
- project=website-redesign
- temporary=true
- protected=true

Bad:
- env=prod
- e=p
- test (ambiguous)
```

### 3. Implement Tag Protection Strategy
- Always tag production resources with `protected=true`
- Use `!protected` filter for safe cleanup
- Require tags like `env`, `owner`, `project` on all resources

### 4. Start Small
- Begin with single region
- Test with non-critical services first
- Gradually expand to more regions/services
- Build confidence before large operations

### 5. Regular Audits
- Run weekly discovery to identify orphaned resources
- Review untagged resources monthly
- Generate cost reports quarterly
- Update tagging policies based on findings

### 6. Document Your Filters
```markdown
# Common Filters

## Development Cleanup
`env=dev,!protected`

## Temporary Resources
`temporary=true`

## Orphaned Resources
`!owner,!project`

## Old Test Resources
`env=test,created_before=2024-01-01`
```

## Safety Guidelines

### ⚠️ Critical Safety Rules

1. **NEVER run in production without extensive testing**
   - Always test in dev/test environments first
   - Use separate AWS accounts for testing

2. **NEVER delete without dry run**
   - Dry run shows exactly what will be deleted
   - Review every single resource

3. **NEVER ignore tag filters**
   - Double-check tag syntax
   - Test filters with discovery first

4. **NEVER delete default resources**
   - Tool protects default VPCs/subnets
   - Additional protection via tags recommended

5. **ALWAYS have backups**
   - Ensure critical data is backed up
   - Test backup restoration process
   - Document recovery procedures

### 🛡️ Protection Strategies

**Tag-Based Protection:**
```
env=production → NEVER delete
protected=true → NEVER delete
critical=true → NEVER delete
```

**Service-Based Protection:**
- Avoid running `all` services in production
- Selectively choose non-critical services
- Exclude databases and storage initially

**Region-Based Protection:**
- Start with non-production regions
- Use region-specific AWS accounts
- Limit cross-region operations

**Time-Based Protection:**
- Run cleanups during off-peak hours
- Schedule maintenance windows
- Allow time for verification

### 📋 Pre-Deletion Checklist

Before executing any deletion:

- [ ] Dry run completed and reviewed
- [ ] All resources in list are expected
- [ ] No production resources included
- [ ] Tags verified as correct
- [ ] Backups confirmed (if applicable)
- [ ] Team notified (for shared resources)
- [ ] Rollback plan documented
- [ ] Monitoring in place for verification

### 🚨 Emergency Procedures

**If you accidentally deleted critical resources:**

1. **Stop immediately** - Don't delete more
2. **Document what was deleted** - Save dry run results
3. **Check backups** - Identify what can be restored
4. **Notify team** - Alert relevant stakeholders
5. **Begin recovery** - Restore from backups
6. **Post-mortem** - Document lessons learned

**Recovery Options:**
- EBS Volume Snapshots → Restore volumes
- RDS Snapshots → Restore databases
- S3 Versioning → Restore objects
- AMIs → Recreate EC2 instances
- CloudFormation → Redeploy stacks

## Advanced Scenarios

### Scenario: Multi-Environment Tag Strategy

```
Production:
- env=production
- protected=true
- critical=true
- compliance=required

Staging:
- env=staging
- protected=true (if needed)
- temporary=false

Development:
- env=development
- temporary=false
- owner=<team-name>

Temporary/Test:
- env=test
- temporary=true
- ttl=7d
- owner=<developer>
```

**Cleanup Filters:**
```
# Safe dev cleanup
env=development,!protected,temporary=false

# Remove old test resources
env=test,temporary=true

# Never touch production
!env=production,!protected,!critical
```

### Scenario: Cost-Optimized Cleanup

1. **Identify High-Cost Resources**
   - Large EC2 instances
   - Unused EBS volumes
   - Old S3 buckets
   - Idle RDS databases

2. **Tag for Cleanup**
   - Add `cost-review=true` tag
   - Add `cleanup-candidate=true` tag

3. **Review and Delete**
   - Use filter: `cleanup-candidate=true`
   - Review estimated savings
   - Execute deletion
   - Track cost reduction

### Scenario: Compliance Enforcement

1. **Define Tagging Policy**
   ```
   Required tags:
   - owner
   - project
   - cost-center
   - compliance
   ```

2. **Find Non-Compliant Resources**
   ```
   !owner OR !project OR !cost-center
   ```

3. **Remediate or Remove**
   - Contact owners to add tags
   - Set deadline for compliance
   - Delete unclaimed resources

## Troubleshooting

### Common Issues

**Issue: "No resources found"**
- Check AWS credentials are valid
- Verify regions have resources
- Check tag filters aren't too restrictive
- Ensure services are selected

**Issue: "Deletion failed"**
- Check resource dependencies
- Verify IAM permissions
- Review error messages in results
- Try deleting dependencies first

**Issue: "Access Denied"**
- Verify AWS IAM permissions
- Check service-specific policies
- Ensure credentials have delete permissions

**Issue: "Too many resources"**
- Narrow down regions
- Use more specific service selection
- Add more restrictive tag filters
- Process in smaller batches

## Support and Resources

- **Documentation:** See `/docs` directory
- **Examples:** See `examples.py`
- **Issues:** GitHub Issues
- **Contributing:** See `CONTRIBUTING.md`
- **Security:** See `SECURITY.md`
