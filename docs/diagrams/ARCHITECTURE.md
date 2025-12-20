# AWS Nuker Architecture Diagrams

## High-Level Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│                                                                        │
│                           AWS Nuker CLI                                │
│                                                                        │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐            │
│  │ list-services│  │ list-regions │  │  nuke (main)    │            │
│  └──────────────┘  └──────────────┘  └─────────────────┘            │
│                                              │                         │
└──────────────────────────────────────────────┼─────────────────────────┘
                                               │
                                               ▼
┌────────────────────────────────────────────────────────────────────────┐
│                      Configuration Layer                               │
│                                                                        │
│  ┌─────────────────────────────────────────────────────────────┐     │
│  │  NukerConfig                                                 │     │
│  │  • Parse regions (single, multiple, range, wildcard)         │     │
│  │  • Parse services (A-Z AWS services)                         │     │
│  │  • dry_run, force, parallel, max_workers                     │     │
│  └─────────────────────────────────────────────────────────────┘     │
└────────────────────────────────────────────┼───────────────────────────┘
                                             │
                                             ▼
┌────────────────────────────────────────────────────────────────────────┐
│                      Orchestration Layer                               │
│                                                                        │
│  ┌─────────────────────────────────────────────────────────────┐     │
│  │  AWSNuker Orchestrator                                       │     │
│  │  • Sequential or Parallel Execution                          │     │
│  │  • Multi-region, multi-service coordination                  │     │
│  │  • Results aggregation and reporting                         │     │
│  └─────────────────────────────────────────────────────────────┘     │
└────────────────────────────────────────────┼───────────────────────────┘
                                             │
                    ┌────────────────────────┼────────────────────────┐
                    │                        │                        │
                    ▼                        ▼                        ▼
┌─────────────────────────┐  ┌──────────────────────┐  ┌──────────────────────┐
│   Handler Registry      │  │   Logger System      │  │  Resource Handlers   │
│                         │  │                      │  │                      │
│ • Service→Handler Map   │  │ • Application Logs   │  │ • EC2Handler         │
│ • get_handler()         │  │ • Audit Trail        │  │ • S3Handler          │
│ • get_available_        │  │ • Timestamped Files  │  │ • RDSHandler         │
│   services()            │  │ • Multi-level        │  │ • LambdaHandler      │
└─────────────────────────┘  │   Logging            │  │ • IAMHandler         │
                             └──────────────────────┘  │ • VPCHandler         │
                                                       │ • ... (15+ handlers) │
                                                       └──────────┬───────────┘
                                                                  │
                                                                  ▼
                                               ┌──────────────────────────────┐
                                               │  Base Handler                │
                                               │  (ResourceHandler)           │
                                               │                              │
                                               │  • list_resources()          │
                                               │  • delete_resource()         │
                                               │  • nuke_all()                │
                                               │  • Retry logic               │
                                               │  • Dependency handling       │
                                               └──────────┬───────────────────┘
                                                          │
                                                          ▼
                                               ┌──────────────────────────────┐
                                               │     AWS SDK (boto3)          │
                                               │                              │
                                               │  • EC2, S3, RDS, Lambda...  │
                                               │  • Multi-region support      │
                                               │  • API calls with retry      │
                                               └──────────────────────────────┘
```

## Execution Flow Diagram

```
START
  │
  ▼
┌─────────────────────┐
│  Parse CLI Args     │
│  • regions          │
│  • services         │
│  • options          │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Build Config       │
│  NukerConfig()      │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Display Config     │
│  & Get Confirmation │
└──────┬──────────────┘
       │
       ▼
    ┌──┴──┐
    │ YES │
    └──┬──┘
       │
       ▼
┌─────────────────────┐
│  Initialize         │
│  AWSNuker           │
│  Orchestrator       │
└──────┬──────────────┘
       │
       ▼
    ┌──────────┐
    │ Parallel?│
    └─┬──────┬─┘
      │      │
   NO │      │ YES
      │      │
      ▼      ▼
  ┌─────────────────┐     ┌──────────────────┐
  │   Sequential    │     │   Parallel       │
  │   Execution     │     │   Execution      │
  └────────┬────────┘     └────────┬─────────┘
           │                       │
           └───────────┬───────────┘
                       │
                       ▼
              ┌────────────────────┐
              │  FOR EACH REGION   │
              └────────┬───────────┘
                       │
                       ▼
              ┌────────────────────┐
              │  FOR EACH SERVICE  │
              └────────┬───────────┘
                       │
                       ▼
              ┌────────────────────┐
              │  Get Handler       │
              │  from Registry     │
              └────────┬───────────┘
                       │
                       ▼
              ┌────────────────────┐
              │  List Resources    │
              │  (AWS API call)    │
              └────────┬───────────┘
                       │
                       ▼
              ┌────────────────────┐
              │  FOR EACH RESOURCE │
              └────────┬───────────┘
                       │
                       ▼
              ┌────────────────────┐
              │  Is Default?       │
              └────┬───────┬───────┘
                   │       │
                YES│       │NO
                   │       │
                   ▼       ▼
           ┌─────────┐  ┌──────────────────┐
           │  SKIP   │  │  Dry Run?        │
           └─────────┘  └────┬───────┬─────┘
                             │       │
                          YES│       │NO
                             │       │
                             ▼       ▼
                    ┌──────────┐  ┌────────────────┐
                    │ LOG ONLY │  │ DELETE RESOURCE│
                    └──────────┘  │ (with retry)   │
                                  └────────┬───────┘
                                           │
                                           ▼
                                  ┌────────────────┐
                                  │ Log to Audit   │
                                  │ Trail          │
                                  └────────────────┘
                                           │
                        ┌──────────────────┴────────┐
                        │                           │
                        ▼                           ▼
                ┌──────────────┐          ┌──────────────┐
                │  Success?    │          │  Failed?     │
                │  Count++     │          │  Error++     │
                └──────────────┘          └──────────────┘
                        │                           │
                        └──────────┬────────────────┘
                                   │
                                   ▼
                          ┌────────────────┐
                          │  Collect Stats │
                          └────────┬───────┘
                                   │
                        ┌──────────┴────────┐
                        │ All Done?         │
                        └──┬────────────┬───┘
                           │            │
                        NO │            │ YES
                           │            │
                           ▼            ▼
                    ┌──────────┐  ┌────────────────┐
                    │ Continue │  │ Generate       │
                    └──────────┘  │ Summary Report │
                                  └────────┬───────┘
                                           │
                                           ▼
                                  ┌────────────────┐
                                  │ Display Results│
                                  │ & Log Files    │
                                  └────────┬───────┘
                                           │
                                           ▼
                                         END
```

## Resource Handler Class Diagram

```
┌─────────────────────────────────────────────────────────┐
│              ResourceHandler (Abstract)                 │
├─────────────────────────────────────────────────────────┤
│ Attributes:                                             │
│  • region: str                                          │
│  • dry_run: bool                                        │
│  • force: bool                                          │
│  • logger: NukerLogger                                  │
│  • session: boto3.Session                               │
├─────────────────────────────────────────────────────────┤
│ Abstract Methods:                                       │
│  + service_name() -> str                                │
│  + list_resources() -> List[Dict]                       │
│  + delete_resource(resource) -> bool                    │
├─────────────────────────────────────────────────────────┤
│ Concrete Methods:                                       │
│  + nuke_all() -> Dict[str, Any]                         │
│  + is_default_resource(resource) -> bool                │
│  + _delete_with_retry(resource, max_retries) -> bool    │
└──────────────────────┬──────────────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │ Inheritance                 │
        │                             │
┌───────▼────────┐            ┌───────▼────────┐
│  EC2Handler    │            │  S3Handler     │
├────────────────┤            ├────────────────┤
│ service_name:  │            │ service_name:  │
│   "ec2"        │            │   "s3"         │
├────────────────┤            ├────────────────┤
│ Resources:     │            │ Resources:     │
│ • Instances    │            │ • Buckets      │
│ • Volumes      │            │                │
│ • Snapshots    │            │ Methods:       │
│ • AMIs         │            │ • _empty_bucket│
│ • SGs          │            │   (versioning) │
│ • Key Pairs    │            └────────────────┘
│ • Elastic IPs  │
└────────────────┘

┌────────────────┐            ┌────────────────┐
│  RDSHandler    │            │ VPCHandler     │
├────────────────┤            ├────────────────┤
│ service_name:  │            │ service_name:  │
│   "rds"        │            │   "vpc"        │
├────────────────┤            ├────────────────┤
│ Resources:     │            │ Resources:     │
│ • DB Instances │            │ • VPCs         │
│ • DB Clusters  │            │ • Subnets      │
│ • Snapshots    │            │ • IGWs         │
└────────────────┘            │ • NAT GWs      │
                              │                │
┌────────────────┐            │ Special:       │
│ LambdaHandler  │            │ • Excludes     │
├────────────────┤            │   default VPCs │
│ service_name:  │            └────────────────┘
│   "lambda"     │
├────────────────┤            ┌────────────────┐
│ Resources:     │            │  IAMHandler    │
│ • Functions    │            ├────────────────┤
│ • Layers       │            │ service_name:  │
└────────────────┘            │   "iam"        │
                              ├────────────────┤
        ... (11+ more         │ Resources:     │
         handlers)            │ • Users        │
                              │ • Roles        │
                              │ • Policies     │
                              │                │
                              │ Special:       │
                              │ • Cleanup      │
                              │   attachments  │
                              │ • Global only  │
                              └────────────────┘
```

## Data Flow Diagram

```
┌──────────────┐
│  User Input  │
│  (CLI Args)  │
└──────┬───────┘
       │
       ▼
┌────────────────────────────────┐
│  Configuration Parsing         │
│                                │
│  regions: "us-*"               │
│    ↓                           │
│  ["us-east-1", "us-east-2",    │
│   "us-west-1", "us-west-2"]    │
│                                │
│  services: "ec2,s3,rds"        │
│    ↓                           │
│  {"ec2", "s3", "rds"}          │
└──────┬─────────────────────────┘
       │
       ▼
┌────────────────────────────────┐
│  Orchestrator                  │
│  Matrix Generation:            │
│                                │
│  [                             │
│    (us-east-1, ec2),           │
│    (us-east-1, s3),            │
│    (us-east-1, rds),           │
│    (us-east-2, ec2),           │
│    (us-east-2, s3),            │
│    (us-east-2, rds),           │
│    ...                         │
│  ]                             │
└──────┬─────────────────────────┘
       │
       ▼
┌────────────────────────────────┐
│  For Each (region, service)    │
│                                │
│  Example: (us-east-1, ec2)     │
│                                │
│  1. Get EC2Handler             │
│  2. Call list_resources()      │
│     ↓                          │
│  [                             │
│    {id: "i-123", type: "inst"},│
│    {id: "vol-456", type: "vol"}│
│  ]                             │
│                                │
│  3. For each resource:         │
│     ├─ Check if default        │
│     ├─ Delete (or dry-run)     │
│     └─ Log to audit            │
│                                │
│  4. Return stats:              │
│  {                             │
│    total: 2,                   │
│    deleted: 2,                 │
│    failed: 0,                  │
│    skipped: 0                  │
│  }                             │
└──────┬─────────────────────────┘
       │
       ▼
┌────────────────────────────────┐
│  Results Aggregation           │
│                                │
│  Combine all stats:            │
│                                │
│  {                             │
│    total_resources: 247,       │
│    total_deleted: 240,         │
│    total_failed: 3,            │
│    total_skipped: 4,           │
│    elapsed_time: 145.3s,       │
│    services_processed: 12,     │
│    errors: [...]               │
│  }                             │
└──────┬─────────────────────────┘
       │
       ▼
┌────────────────────────────────┐
│  Output Generation             │
│                                │
│  • Console summary table       │
│  • Log file locations          │
│  • Audit trail path            │
└────────────────────────────────┘
```

## Parallel Execution Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                  ThreadPoolExecutor                         │
│                  (max_workers=5)                            │
└──────────────────┬──────────────────────────────────────────┘
                   │
    ┌──────────────┼──────────────┬──────────────┬────────────┐
    │              │              │              │            │
    ▼              ▼              ▼              ▼            ▼
┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐
│ Worker 1│   │ Worker 2│   │ Worker 3│   │ Worker 4│   │ Worker 5│
├─────────┤   ├─────────┤   ├─────────┤   ├─────────┤   ├─────────┤
│ Region: │   │ Region: │   │ Region: │   │ Region: │   │ Region: │
│ us-east │   │ us-east │   │ us-west │   │ us-west │   │ eu-west │
│ Service:│   │ Service:│   │ Service:│   │ Service:│   │ Service:│
│ EC2     │   │ S3      │   │ EC2     │   │ S3      │   │ EC2     │
└────┬────┘   └────┬────┘   └────┬────┘   └────┬────┘   └────┬────┘
     │             │             │             │             │
     ▼             ▼             ▼             ▼             ▼
  List → Delete   List → Delete  List → Delete  List → Delete  List → Delete
     │             │             │             │             │
     ▼             ▼             ▼             ▼             ▼
┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐
│ Stats 1 │   │ Stats 2 │   │ Stats 3 │   │ Stats 4 │   │ Stats 5 │
└────┬────┘   └────┬────┘   └────┬────┘   └────┬────┘   └────┬────┘
     │             │             │             │             │
     └─────────────┴─────────────┴─────────────┴─────────────┘
                                 │
                                 ▼
                         ┌───────────────┐
                         │   Aggregate   │
                         │   Results     │
                         └───────────────┘
```

## Logging Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                     NukerLogger                              │
└──────────────────┬───────────────────────────────────────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
        ▼                     ▼
┌──────────────────┐   ┌──────────────────┐
│  Main Logger     │   │  Audit Logger    │
├──────────────────┤   ├──────────────────┤
│ Level: DEBUG     │   │ Level: INFO      │
│                  │   │                  │
│ Handlers:        │   │ Handlers:        │
│ • File Handler   │   │ • File Handler   │
│ • Console        │   │   (audit only)   │
│   Handler        │   │                  │
└────────┬─────────┘   └────────┬─────────┘
         │                      │
         ▼                      ▼
┌──────────────────┐   ┌──────────────────┐
│ logs/            │   │ audit/           │
│ aws_nuker_       │   │ audit_           │
│ YYYYMMDD_        │   │ YYYYMMDD_        │
│ HHMMSS.log       │   │ HHMMSS.log       │
│                  │   │                  │
│ Contains:        │   │ Contains:        │
│ • INFO msgs      │   │ • All deletions  │
│ • DEBUG msgs     │   │ • Resource IDs   │
│ • ERROR msgs     │   │ • Timestamps     │
│ • Stack traces   │   │ • Status codes   │
└──────────────────┘   └──────────────────┘
```
