"""
Policy templates for AWS Nuker cleanup operations.

Provides predefined policies for common cleanup scenarios.
"""

import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class PolicyType(Enum):
    """Types of cleanup policies."""
    
    DEV_CLEANUP = "dev_cleanup"
    ORPHAN_PURGE = "orphan_purge"
    COST_KILL = "cost_kill"
    STORAGE_CLEANUP = "storage_cleanup"
    CUSTOM = "custom"


@dataclass
class CleanupPolicy:
    """Represents a cleanup policy with filters and actions."""

    name: str
    description: str
    policy_type: PolicyType
    tag_filters: Dict[str, Any] = field(default_factory=dict)
    resource_filters: Dict[str, Any] = field(default_factory=dict)
    age_threshold_days: int = 0
    cost_threshold_usd: float = 0.0
    require_approval: bool = False
    approval_threshold_usd: float = 100.0
    soft_delete: bool = False
    soft_delete_ttl_days: int = 7
    create_snapshot: bool = False
    snapshot_threshold_gb: int = 100
    excluded_resources: List[str] = field(default_factory=list)
    included_services: List[str] = field(default_factory=list)
    notification_channels: List[str] = field(default_factory=list)

    def to_json(self) -> str:
        """Convert policy to JSON string."""
        policy_dict = {
            'name': self.name,
            'description': self.description,
            'policy_type': self.policy_type.value,
            'tag_filters': self.tag_filters,
            'resource_filters': self.resource_filters,
            'age_threshold_days': self.age_threshold_days,
            'cost_threshold_usd': self.cost_threshold_usd,
            'require_approval': self.require_approval,
            'approval_threshold_usd': self.approval_threshold_usd,
            'soft_delete': self.soft_delete,
            'soft_delete_ttl_days': self.soft_delete_ttl_days,
            'create_snapshot': self.create_snapshot,
            'snapshot_threshold_gb': self.snapshot_threshold_gb,
            'excluded_resources': self.excluded_resources,
            'included_services': self.included_services,
            'notification_channels': self.notification_channels
        }
        return json.dumps(policy_dict, indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'CleanupPolicy':
        """Create policy from JSON string."""
        data = json.loads(json_str)
        data['policy_type'] = PolicyType(data['policy_type'])
        return cls(**data)


class PolicyTemplates:
    """Provides predefined cleanup policy templates."""

    @staticmethod
    def dev_cleanup() -> CleanupPolicy:
        """
        Policy for cleaning up development/test environments.
        
        - Targets resources with env=dev, env=test, env=staging
        - Includes resources unused for 7+ days
        - No approval required for resources under $100
        - Soft delete with 7-day recovery window
        - Creates snapshots for databases and storage > 10GB
        """
        return CleanupPolicy(
            name="Development Environment Cleanup",
            description="Removes resources from dev, test, and staging environments",
            policy_type=PolicyType.DEV_CLEANUP,
            tag_filters={
                "OR": [
                    {"env": "dev"},
                    {"env": "development"},
                    {"env": "test"},
                    {"env": "testing"},
                    {"env": "staging"},
                    {"environment": "dev"},
                    {"environment": "development"},
                    {"environment": "test"},
                    {"environment": "testing"},
                    {"environment": "staging"}
                ]
            },
            age_threshold_days=7,
            require_approval=True,
            approval_threshold_usd=100.0,
            soft_delete=True,
            soft_delete_ttl_days=7,
            create_snapshot=True,
            snapshot_threshold_gb=10,
            excluded_resources=[
                "arn:aws:ec2:*:*:vpc/*default*",
                "arn:aws:ec2:*:*:security-group/*default*"
            ],
            included_services=[
                "ec2", "rds", "dynamodb", "s3", "lambda",
                "ecs", "eks", "elasticache", "redshift"
            ],
            notification_channels=["email", "slack"]
        )
    
    @staticmethod
    def orphan_purge() -> CleanupPolicy:
        """
        Policy for removing orphaned resources.
        
        - Targets untagged resources
        - Targets resources with no owner tag
        - Includes orphaned volumes, snapshots, IPs
        - Requires approval for all deletions
        - Creates snapshots for volumes and databases
        """
        return CleanupPolicy(
            name="Orphaned Resources Purge",
            description="Removes untagged and orphaned resources",
            policy_type=PolicyType.ORPHAN_PURGE,
            tag_filters={
                "OR": [
                    {"UNTAGGED": True},
                    {"NOT": {"owner": "*"}},
                    {"NOT": {"managed-by": "*"}}
                ]
            },
            age_threshold_days=30,
            require_approval=True,
            approval_threshold_usd=10.0,
            soft_delete=True,
            soft_delete_ttl_days=7,
            create_snapshot=True,
            snapshot_threshold_gb=1,
            included_services=[
                "ec2",  # Orphaned volumes, snapshots, AMIs, elastic IPs
                "rds",  # Orphaned snapshots
                "s3",   # Buckets with no tags
                "elasticache"
            ],
            notification_channels=["email", "slack"]
        )
    
    @staticmethod
    def cost_kill() -> CleanupPolicy:
        """
        Policy for aggressive cost reduction.
        
        - Targets high-cost resources unused for 30+ days
        - Focuses on compute, database, and storage
        - Requires approval for resources over $500
        - Always creates snapshots before deletion
        """
        return CleanupPolicy(
            name="High Cost Resource Cleanup",
            description="Aggressively removes expensive unused resources",
            policy_type=PolicyType.COST_KILL,
            resource_filters={
                "OR": [
                    {"instance_state": "stopped"},
                    {"status": "available"},
                    {"last_accessed_days": {"gt": 30}}
                ]
            },
            age_threshold_days=30,
            cost_threshold_usd=50.0,
            require_approval=True,
            approval_threshold_usd=500.0,
            soft_delete=True,
            soft_delete_ttl_days=14,
            create_snapshot=True,
            snapshot_threshold_gb=1,
            included_services=[
                "ec2", "rds", "redshift", "elasticache",
                "eks", "emr", "sagemaker"
            ],
            notification_channels=["email", "slack"]
        )
    
    @staticmethod
    def storage_cleanup() -> CleanupPolicy:
        """
        Policy for large storage cleanup.
        
        - Targets S3 buckets, EBS volumes, snapshots > 100GB
        - Removes old backups and snapshots
        - Creates final snapshots before deletion
        - Requires approval for large datasets
        """
        return CleanupPolicy(
            name="Large Storage Cleanup",
            description="Removes old backups, snapshots, and large unused storage",
            policy_type=PolicyType.STORAGE_CLEANUP,
            resource_filters={
                "OR": [
                    {"size_gb": {"gt": 100}},
                    {"type": "snapshot"},
                    {"type": "backup"}
                ]
            },
            age_threshold_days=90,
            require_approval=True,
            approval_threshold_usd=50.0,
            soft_delete=False,  # Direct deletion for old backups
            create_snapshot=True,
            snapshot_threshold_gb=500,
            included_services=[
                "s3", "ec2", "rds", "dynamodb",
                "efs", "fsx", "glacier", "backup"
            ],
            notification_channels=["email", "slack"]
        )
    
    @staticmethod
    def get_all_templates() -> List[CleanupPolicy]:
        """Get all predefined policy templates."""
        return [
            PolicyTemplates.dev_cleanup(),
            PolicyTemplates.orphan_purge(),
            PolicyTemplates.cost_kill(),
            PolicyTemplates.storage_cleanup()
        ]
    
    @staticmethod
    def get_template_by_type(policy_type: PolicyType) -> Optional[CleanupPolicy]:
        """Get a specific policy template by type."""
        templates = {
            PolicyType.DEV_CLEANUP: PolicyTemplates.dev_cleanup(),
            PolicyType.ORPHAN_PURGE: PolicyTemplates.orphan_purge(),
            PolicyType.COST_KILL: PolicyTemplates.cost_kill(),
            PolicyType.STORAGE_CLEANUP: PolicyTemplates.storage_cleanup()
        }
        return templates.get(policy_type)
    
    @staticmethod
    def create_custom_policy(
        name: str,
        description: str,
        **kwargs
    ) -> CleanupPolicy:
        """
        Create a custom cleanup policy.

        Args:
            name: Policy name
            description: Policy description
            **kwargs: Additional policy parameters

        Returns:
            Custom CleanupPolicy
        """
        return CleanupPolicy(
            name=name,
            description=description,
            policy_type=PolicyType.CUSTOM,
            **kwargs
        )
