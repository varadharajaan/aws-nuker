# AWS Nuker Web UI - Architecture Documentation

## Table of Contents
1. [System Architecture](#system-architecture)
2. [Component Architecture](#component-architecture)
3. [Data Flow](#data-flow)
4. [API Architecture](#api-architecture)
5. [Frontend Architecture](#frontend-architecture)
6. [Deployment Architecture](#deployment-architecture)

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         AWS Nuker System                         │
│                                                                  │
│  ┌──────────────┐         ┌──────────────┐      ┌────────────┐ │
│  │              │         │              │      │            │ │
│  │  Web Browser │◄───────►│  React SPA   │◄────►│  FastAPI   │ │
│  │  (User UI)   │         │  (Frontend)  │      │  (Backend) │ │
│  │              │         │              │      │            │ │
│  └──────────────┘         └──────────────┘      └─────┬──────┘ │
│                                                        │        │
│                           ┌────────────────────────────┘        │
│                           │                                     │
│                           ▼                                     │
│                  ┌─────────────────┐                           │
│                  │                 │                           │
│                  │  AWS SDK (boto3)│                           │
│                  │                 │                           │
│                  └────────┬────────┘                           │
│                           │                                     │
└───────────────────────────┼─────────────────────────────────────┘
                            │
                            ▼
         ┌──────────────────────────────────────────┐
         │          AWS Cloud Services               │
         │                                           │
         │  ┌────────┐  ┌────────┐  ┌────────┐     │
         │  │  EC2   │  │   S3   │  │  RDS   │     │
         │  └────────┘  └────────┘  └────────┘     │
         │                                           │
         │  ┌────────┐  ┌────────┐  ┌────────┐     │
         │  │Lambda  │  │  IAM   │  │  VPC   │     │
         │  └────────┘  └────────┘  └────────┘     │
         │                                           │
         │        ... 67+ services total             │
         └──────────────────────────────────────────┘
```

## Technology Stack

**Backend:**
- Python 3.9+ with FastAPI framework
- Uvicorn ASGI server
- boto3 AWS SDK
- Pydantic for data validation

**Frontend:**
- React 18 with TypeScript
- Vite build tool
- TailwindCSS for styling
- React Query for state management
- Recharts for data visualization
- Axios for HTTP client

See full documentation in this directory.
