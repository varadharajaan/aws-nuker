# AWS Nuker UI Dashboard - Complete Usage Guide

This comprehensive guide covers all features of the AWS Nuker UI Dashboard, providing step-by-step instructions, screenshots descriptions, and best practices.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Dashboard Overview](#dashboard-overview)
3. [Resource Explorer](#resource-explorer)
4. [Smart Filter Builder](#smart-filter-builder)
5. [Dry-Run Panel](#dry-run-panel)
6. [Deletion Operations](#deletion-operations)
7. [Approval Workflow](#approval-workflow)
8. [Reports & Analytics](#reports--analytics)
9. [Tag Management](#tag-management)
10. [Settings & Configuration](#settings--configuration)
11. [Keyboard Shortcuts](#keyboard-shortcuts)
12. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Python 3.9+
- AWS credentials configured
- Modern web browser (Chrome, Firefox, Safari, Edge)

### Installation

```bash
# Clone repository
git clone https://github.com/varadharajaan/aws-nuker.git
cd aws-nuker

# Install backend dependencies
cd api
pip install -r requirements.txt

# Install frontend dependencies
cd ../ui
npm install
```

### Starting the Application

**Terminal 1 - Backend API:**
```bash
cd api
python server.py
# API server starts on http://localhost:8000
# Swagger docs available at http://localhost:8000/docs
```

**Terminal 2 - Frontend UI:**
```bash
cd ui
npm run dev
# UI dashboard starts on http://localhost:5173
```

### First Login

1. Open browser to `http://localhost:5173`
2. You'll see the Dashboard Overview (no login required in development mode)
3. For production, configure authentication in Settings

---

## Dashboard Overview

The main dashboard provides a comprehensive view of your AWS infrastructure and cleanup status.

### Key Components

**1. Statistics Cards (Top Row)**
- **Total Resources**: Count of all discovered resources across regions
- **Estimated Cost**: Monthly cost estimate for all resources
- **Cleanup Candidates**: Resources matching cleanup policies
- **Pending Approvals**: Deletions awaiting manual approval

**2. Cost Distribution Chart**
- Pie chart showing cost breakdown by service
- Interactive - click slices to filter by service
- Hover for detailed cost information

**3. Top Services Table**
- Lists top 5 services by resource count
- Shows service name, count, and estimated cost
- Click to navigate to Resource Explorer filtered by service

**4. Recent Activity Timeline**
- Last 10 cleanup operations
- Shows timestamp, action, service, and result
- Color-coded: Green (success), Red (failed), Yellow (pending)

**5. Quick Actions**
- **Discover Resources**: Launch resource discovery
- **Dry Run**: Quick dry-run simulation
- **View Reports**: Navigate to reports section
- **Settings**: Open configuration

### Screenshot Description
```
┌─────────────────────────────────────────────────────────────┐
│  AWS Nuker Dashboard                    🔍 Search  🔔 🌙 ⚙️ │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │  12,453  │ │ $1,234.56│ │   342    │ │    5     │       │
│  │Resources │ │   Cost   │ │Candidates│ │ Approvals│       │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
│                                                               │
│  ┌─────────────────┐  ┌──────────────────────────────┐     │
│  │  Cost by Service│  │  Top 5 Services             │     │
│  │   ╱─────╲       │  │  1. EC2      1,234  $456.78  │     │
│  │  ╱       ╲      │  │  2. S3         892  $234.56  │     │
│  │ │  EC2    │     │  │  3. RDS        456  $345.67  │     │
│  │  ╲       ╱      │  │  4. Lambda     234  $45.67   │     │
│  │   ╲─────╱       │  │  5. DynamoDB   123  $23.45   │     │
│  └─────────────────┘  └──────────────────────────────┘     │
│                                                               │
│  Recent Activity:                                             │
│  • 2 mins ago - Deleted 5 EC2 instances in us-east-1 ✓      │
│  • 15 mins ago - Dry-run: 12 S3 buckets identified          │
│  • 1 hour ago - Approval pending for RDS cleanup            │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## Resource Explorer

Discover and manage AWS resources across all regions and services.

### Features

**1. Multi-Region Selection**
- Dropdown to select one or more regions
- Options: Single region, Multiple regions, All US regions, All regions
- Real-time resource count per region

**2. Service Filter**
- Searchable dropdown with all 28 supported services
- Wildcard support (e.g., "cloud*" matches CloudFormation, CloudWatch)
- Multi-select capability

**3. Resource Table**
- Columns: Resource ID, Name, Type, Region, Tags, Age, Cost, Status
- Sortable by any column
- Pagination (25/50/100 per page)
- Bulk selection checkboxes

**4. Smart Search Bar**
- Natural language queries supported
- Examples:
  - "EC2 instances older than 30 days"
  - "S3 buckets in us-east-1 with cost > $100"
  - "Untagged resources in production"

**5. Action Buttons**
- **Refresh**: Reload resource list
- **Export**: Download as CSV/JSON
- **Dry Run**: Simulate deletion of selected
- **Delete**: Delete selected resources

### Usage Steps

1. **Select Region(s)**
   - Click region dropdown
   - Choose one or more regions
   - Or use "All Regions" for comprehensive scan

2. **Filter by Service**
   - Click service dropdown
   - Search or scroll to desired service
   - Select one or multiple services

3. **Apply Additional Filters**
   - Use filter builder (sidebar)
   - Set tag filters, age, cost thresholds
   - Click "Apply Filters"

4. **Review Results**
   - Browse resource table
   - Sort by columns as needed
   - Select resources for action

5. **Take Action**
   - Select checkboxes for target resources
   - Click "Dry Run" to preview
   - Or click "Delete" to execute

### Screenshot Description
```
┌─────────────────────────────────────────────────────────────┐
│  Resource Explorer                                            │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Regions: [us-east-1 ▼]  Services: [All Services ▼]         │
│                                                               │
│  🔍 Search: "EC2 in us-east-1 older than 30d"               │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │☐ Resource ID    │Type │Region    │Tags │Age │Cost   │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │☐ i-1234abcd     │EC2  │us-east-1 │env: │45d │$12.34 │   │
│  │☐ i-5678efgh     │EC2  │us-east-1 │env: │52d │$15.67 │   │
│  │☐ i-9012ijkl     │EC2  │us-west-2 │prod│38d │$18.90 │   │
│  │☐ vol-abc123     │EBS  │us-east-1 │none│60d │$5.00  │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  [Refresh] [Export] [Dry Run] [Delete Selected]             │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## Smart Filter Builder

Build complex filters using an intuitive visual interface.

### Filter Types

**1. Tag Filters**
- Key-value pairs
- Operators: equals, contains, starts_with, regex
- Negation support

**2. Age Filters**
- Greater than X days
- Less than X days
- Between date range

**3. Cost Filters**
- Greater than $X
- Less than $X
- Between cost range

**4. State Filters**
- Running, Stopped, Terminated
- Available, In-use
- Active, Inactive

**5. Owner Filters**
- By AWS account ID
- By IAM user
- By tag owner value

### Building Filters

1. **Add Filter Row**
   - Click "+ Add Filter"
   - Select filter type from dropdown
   - Set operator and value

2. **Combine Filters**
   - AND: All conditions must match
   - OR: Any condition can match
   - Toggle between AND/OR with button

3. **Save Filter Preset**
   - Name your filter combination
   - Save for future use
   - Share with team

4. **Apply Filters**
   - Click "Apply"
   - Results update in real-time
   - Filter summary shown above table

### Example Filter Combinations

**Dev Environment Cleanup:**
```
Tag: env = dev
AND Age > 7 days
AND State = stopped
```

**High-Cost Unused Resources:**
```
Cost > $100/month
AND State = available
AND Age > 30 days
```

**Compliance: Untagged Resources:**
```
Tag: env NOT EXISTS
OR Tag: owner NOT EXISTS
```

---

## Dry-Run Panel

Preview deletion impact before executing.

### Features

**1. Simulation Results**
- List of resources to be deleted
- Dependency graph visualization
- Impact analysis summary

**2. Dependency Graph**
- Visual representation of resource relationships
- Shows which resources depend on others
- Deletion order calculated automatically

**3. Impact Analysis**
- Total resources affected
- Estimated cost savings
- Services impacted
- Warnings for critical resources

**4. Export Options**
- Export simulation results as JSON
- Download dependency graph as SVG
- Save impact report as PDF

### Running a Dry-Run

1. **Select Resources**
   - Use Resource Explorer
   - Or apply policy template
   - Or filter by tags

2. **Click "Dry Run"**
   - Button in Resource Explorer
   - Or from Dashboard Quick Actions

3. **Review Results**
   - Check resources list
   - Examine dependencies
   - Review warnings

4. **Analyze Impact**
   - Cost savings estimate
   - Service disruption warnings
   - Dependency resolution order

5. **Export or Proceed**
   - Export for documentation
   - Or proceed to deletion
   - Or cancel and adjust filters

### Screenshot Description
```
┌─────────────────────────────────────────────────────────────┐
│  Dry-Run Simulation Results                                  │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Summary:                                                     │
│  • Resources to delete: 24                                   │
│  • Estimated savings: $234.56/month                          │
│  • Services affected: EC2, EBS, S3                           │
│  • ⚠ 2 warnings                                              │
│                                                               │
│  Dependency Graph:                                            │
│  ┌─────────────────────────────────────────────┐            │
│  │   EC2 Instance                               │            │
│  │   i-1234abcd ──→ EBS Volume                 │            │
│  │              │   vol-abc123                  │            │
│  │              │                                │            │
│  │              └──→ Security Group             │            │
│  │                  sg-xyz789                   │            │
│  └─────────────────────────────────────────────┘            │
│                                                               │
│  Warnings:                                                    │
│  • Security group sg-xyz789 is used by 3 other instances    │
│  • S3 bucket has 1,234 versioned objects                    │
│                                                               │
│  [Export Results] [Cancel] [Proceed to Delete]              │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## Deletion Operations

Execute safe, controlled resource deletion.

### Deletion Flow

1. **Confirmation Modal**
   - Lists resources to delete
   - Shows warnings
   - Requires typing "DELETE" to confirm

2. **Soft Delete (Optional)**
   - Tag resources for deletion
   - 7-14 day retention period
   - Can be undone before final deletion

3. **Progress Tracking**
   - Real-time progress bar
   - Current resource being deleted
   - Success/failure indicators

4. **Completion Summary**
   - Total deleted
   - Failed deletions with reasons
   - Cost savings achieved

### Safety Features

**1. Confirmation Prompts**
- Type "DELETE" to confirm
- Cannot proceed without confirmation
- Shows total count and cost impact

**2. Soft Delete Option**
- Tag resources instead of immediate deletion
- Configurable TTL (7, 14, 30 days)
- Recovery window

**3. Snapshot Automation**
- Auto-snapshot for databases
- Configurable size threshold
- EBS, RDS, DynamoDB supported

**4. Approval Required**
- Production resources
- High-cost resources (> threshold)
- Manual approval workflow

**5. Undo Capability**
- Within retention window
- Restore soft-deleted resources
- Full audit trail

### Deletion Steps

1. **Select Resources**
   - From Resource Explorer
   - Or from Dry-Run results

2. **Click "Delete"**
   - Opens confirmation modal
   - Shows resources and warnings

3. **Review & Confirm**
   - Read all warnings
   - Type "DELETE" in text box
   - Click "Confirm Deletion"

4. **Monitor Progress**
   - Progress bar shows status
   - Logs displayed in real-time
   - Can cancel during execution

5. **Review Results**
   - Summary shows successes/failures
   - Failed deletions with error messages
   - Cost savings calculated

---

## Approval Workflow

Manage approval requests for resource deletions.

### Approval Types

**1. Auto-Approved**
- Cost below threshold (e.g., < $100)
- Development environment
- Age > configured threshold

**2. Manual Approval Required**
- Production environment
- Cost above threshold
- Protected tags present

### Approvals Page

**Pending Approvals List:**
- Request ID
- Submitted by
- Policy applied
- Resource count
- Estimated cost
- Submitted time

**Approval Actions:**
- **Approve**: Execute deletion
- **Reject**: Cancel request
- **Request Info**: Ask for more details

**Approval History:**
- All past approvals/rejections
- Approver name and timestamp
- Comments/notes

### Approval Process

**For Requesters:**
1. Submit deletion request
2. Wait for approval notification
3. Monitor approval status
4. Receive decision notification

**For Approvers:**
1. Receive approval request notification
2. Review request details
3. Check resource list and impact
4. Approve or reject with comment
5. Notification sent to requester

### Configuration

**Approval Rules (Settings):**
- Cost threshold for auto-approval
- Protected tag list
- Approver list (email/username)
- Notification channels

### Screenshot Description
```
┌─────────────────────────────────────────────────────────────┐
│  Approval Workflow                                            │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Pending Approvals (3)                                        │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ ID: APR-001                                           │   │
│  │ Policy: Dev Cleanup                                   │   │
│  │ Resources: 24 EC2 instances                           │   │
│  │ Cost Impact: $234.56/month savings                    │   │
│  │ Submitted: 2 hours ago by john@company.com           │   │
│  │ [View Details] [Approve] [Reject]                     │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ ID: APR-002                                           │   │
│  │ Policy: Cost Kill                                     │   │
│  │ Resources: 8 RDS instances                            │   │
│  │ Cost Impact: $1,234.56/month savings                  │   │
│  │ Submitted: 1 day ago by sarah@company.com            │   │
│  │ [View Details] [Approve] [Reject]                     │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## Reports & Analytics

View cleanup history and analyze cost savings.

### Report Types

**1. Cleanup Logs**
- Complete history of all deletions
- Filterable by date, service, region
- Export to CSV/JSON

**2. Cost Savings Report**
- Monthly savings chart
- Breakdown by service
- Cumulative savings

**3. Resource Trends**
- Resource count over time
- Service distribution changes
- Growth/cleanup patterns

**4. Audit Trail**
- Who deleted what and when
- Approval history
- Configuration changes

### Viewing Reports

**Cleanup History:**
- Date range picker
- Service filter
- Region filter
- Status filter (success/failed)
- Search by resource ID

**Cost Analytics:**
- Pie chart: Savings by service
- Line chart: Savings over time
- Bar chart: Top cost-saving operations

**Export Options:**
- CSV: Tabular data
- JSON: API-compatible format
- PDF: Formatted report with charts

### Screenshot Description
```
┌─────────────────────────────────────────────────────────────┐
│  Reports & Analytics                                          │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Date Range: [Last 30 Days ▼]                               │
│                                                               │
│  Cost Savings: $12,345.67 (Last 30 Days)                    │
│  ┌────────────────────────────────────────┐                 │
│  │ $                                       │                 │
│  │ 5k ─                          ╱─────    │                 │
│  │    │                    ╱────╱          │                 │
│  │ 2.5k─              ╱───╱                │                 │
│  │    │        ╱─────╱                     │                 │
│  │ 0  └──────────────────────────────────  │                 │
│  │     Week 1  Week 2  Week 3  Week 4      │                 │
│  └────────────────────────────────────────┘                 │
│                                                               │
│  Recent Cleanup Operations:                                   │
│  • 2024-01-15: Deleted 50 EC2 instances - $567.89/month     │
│  • 2024-01-14: Deleted 20 S3 buckets - $234.56/month        │
│  • 2024-01-13: Deleted 10 RDS instances - $1,234.56/month   │
│                                                               │
│  [Export CSV] [Export JSON] [Export PDF]                    │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## Tag Management

Discover, analyze, and manage resource tags.

### Features

**1. Tag Discovery**
- Scan all resources for tags
- Group by tag key-value pairs
- Show untagged resources

**2. Tag Analysis**
- Most common tags
- Tag coverage percentage
- Compliance metrics

**3. Bulk Tagging**
- Add tags to multiple resources
- Update existing tags
- Remove tags in bulk

**4. Tag-Based Cleanup**
- Filter resources by tags
- One-click cleanup by tag
- Tag pattern matching

### Tag Discovery

1. **Click "Discover Tags"**
   - Scans all regions
   - Lists all tag keys and values
   - Shows resource count per tag

2. **View Tag Groups**
   - Resources grouped by tag combination
   - Example: env=dev AND owner=john
   - Click to see resources

3. **Identify Untagged**
   - Filter for resources with no tags
   - Compliance violation reporting
   - Bulk tag assignment option

### Tag Operations

**Add Tags:**
- Select resources
- Click "Add Tags"
- Enter key-value pairs
- Confirm and apply

**Update Tags:**
- Select resources
- Click "Update Tags"
- Modify values
- Confirm changes

**Remove Tags:**
- Select resources with tag
- Click "Remove Tags"
- Select keys to remove
- Confirm deletion

---

## Settings & Configuration

Configure the AWS Nuker dashboard to match your requirements.

### Settings Categories

**1. AWS Configuration**
- Default region
- AWS profile
- API endpoint
- Timeout settings

**2. Notification Preferences**
- Email notifications
- Slack webhook URL
- SNS topic ARN
- Notification events

**3. Approval Thresholds**
- Auto-approval cost limit
- Production approval required
- Protected tags list
- Approver emails

**4. Soft Delete Settings**
- Enable/disable soft delete
- Retention period (7/14/30 days)
- Auto-cleanup after TTL
- Snapshot thresholds

**5. UI Preferences**
- Dark/light mode
- Table page size
- Default filters
- Dashboard refresh interval

**6. API Keys**
- Generate API keys
- Revoke access
- View usage
- Rate limits

### Configuring Settings

1. **Click Settings Icon** (top right)
2. **Select Category** from sidebar
3. **Modify Values** as needed
4. **Click "Save Changes"**
5. **Confirmation** message displayed

---

## Keyboard Shortcuts

Increase productivity with keyboard shortcuts.

### Global Shortcuts

- `Ctrl/Cmd + K`: Open search
- `Ctrl/Cmd + D`: Toggle dark mode
- `Ctrl/Cmd + ,`: Open settings
- `Esc`: Close modal/dialog
- `?`: Show keyboard shortcuts

### Resource Explorer

- `Ctrl/Cmd + R`: Refresh resources
- `Ctrl/Cmd + A`: Select all
- `Ctrl/Cmd + E`: Export selection
- `Space`: Toggle selection
- `Enter`: Open resource details

### Navigation

- `G then D`: Go to Dashboard
- `G then E`: Go to Explorer
- `G then A`: Go to Approvals
- `G then R`: Go to Reports
- `G then S`: Go to Settings

---

## Troubleshooting

### Common Issues

**1. API Connection Error**
- **Symptom**: "Cannot connect to API server"
- **Solution**: 
  - Check backend is running (`python server.py`)
  - Verify URL in browser: `http://localhost:8000/docs`
  - Check firewall/proxy settings

**2. No Resources Displayed**
- **Symptom**: Empty resource table
- **Solution**:
  - Verify AWS credentials configured
  - Check selected regions have resources
  - Review filter settings (may be too restrictive)
  - Check browser console for errors

**3. Slow Performance**
- **Symptom**: Dashboard loads slowly
- **Solution**:
  - Reduce number of regions scanned
  - Use service filters to narrow scope
  - Increase pagination page size
  - Clear browser cache

**4. Deletion Fails**
- **Symptom**: Resources not deleted
- **Solution**:
  - Check IAM permissions
  - Review error message in logs
  - Verify no dependency blocking
  - Try force delete mode

**5. Dark Mode Not Working**
- **Symptom**: Theme doesn't change
- **Solution**:
  - Clear browser cache
  - Check browser compatibility
  - Try Ctrl+Shift+R to hard refresh

### Getting Help

- **Documentation**: Check this guide and API docs
- **GitHub Issues**: Report bugs and feature requests
- **Community**: Discussion forum for questions
- **Email**: support@aws-nuker.com (if configured)

---

## Best Practices

### Resource Discovery

- Start with single region for testing
- Use filters to narrow scope
- Export results for documentation
- Regular scans (weekly/monthly)

### Deletions

- Always dry-run first
- Review dependencies carefully
- Start with small batches
- Enable soft delete for safety
- Monitor cost savings

### Approvals

- Set appropriate thresholds
- Define protected tags clearly
- Review requests promptly
- Document approval decisions
- Audit regularly

### Compliance

- Tag all resources consistently
- Scan for untagged resources monthly
- Set tagging policies
- Generate compliance reports
- Review with team quarterly

---

**End of UI Dashboard Guide**

For API documentation, see `API_DOCUMENTATION.md`  
For deployment guide, see `DEPLOYMENT_GUIDE.md`  
For architecture diagrams, see `ARCHITECTURE_DIAGRAMS.md`
