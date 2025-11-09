"""
Approval gate system for AWS Nuker.

Handles approval workflows for resource deletion with cost and environment checks.
"""

from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import logging

from .policy_templates import CleanupPolicy

logger = logging.getLogger(__name__)


class ApprovalStatus(Enum):
    """Status of an approval request."""
    
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    AUTO_APPROVED = "auto_approved"
    EXPIRED = "expired"


@dataclass
class ApprovalRequest:
    """Represents an approval request for resource deletion."""

    request_id: str
    policy: CleanupPolicy
    resources: List[Dict[str, Any]]
    estimated_cost_usd: float
    requester: str
    created_at: datetime = field(default_factory=datetime.now)
    status: ApprovalStatus = ApprovalStatus.PENDING
    approver: Optional[str] = None
    approved_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def resource_count(self) -> int:
        """Get number of resources in this request."""
        return len(self.resources)
    
    @property
    def requires_approval(self) -> bool:
        """Check if this request requires approval."""
        return (
            self.policy.require_approval and
            self.estimated_cost_usd >= self.policy.approval_threshold_usd
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert request to dictionary."""
        return {
            'request_id': self.request_id,
            'policy_name': self.policy.name,
            'resource_count': self.resource_count,
            'estimated_cost_usd': self.estimated_cost_usd,
            'requester': self.requester,
            'created_at': self.created_at.isoformat(),
            'status': self.status.value,
            'approver': self.approver,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'rejection_reason': self.rejection_reason,
            'metadata': self.metadata
        }
    
    def to_json(self) -> str:
        """Convert request to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


class ApprovalGate:
    """Manages approval workflow for resource deletions."""

    def __init__(self):
        """Initialize approval gate."""
        self.pending_requests: Dict[str, ApprovalRequest] = {}
        self.approval_history: List[ApprovalRequest] = []
        self.auto_approval_rules: List[Callable] = []
    
    def create_request(
        self,
        policy: CleanupPolicy,
        resources: List[Dict[str, Any]],
        estimated_cost_usd: float,
        requester: str = "system"
    ) -> ApprovalRequest:
        """
        Create a new approval request.

        Args:
            policy: Cleanup policy being applied
            resources: List of resources to be deleted
            estimated_cost_usd: Estimated cost of resources
            requester: User or system requesting the deletion

        Returns:
            ApprovalRequest object
        """
        request_id = f"req_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.pending_requests)}"
        
        request = ApprovalRequest(
            request_id=request_id,
            policy=policy,
            resources=resources,
            estimated_cost_usd=estimated_cost_usd,
            requester=requester,
            metadata={
                'environment_tags': self._extract_environment_tags(resources),
                'resource_types': list(set(r.get('ResourceType', 'Unknown') for r in resources)),
                'regions': list(set(r.get('Region', 'Unknown') for r in resources))
            }
        )
        
        # Check for auto-approval
        if self._should_auto_approve(request):
            request.status = ApprovalStatus.AUTO_APPROVED
            request.approved_at = datetime.now()
            request.approver = "system"
            logger.info(f"Request {request_id} auto-approved")
        else:
            self.pending_requests[request_id] = request
            logger.info(f"Created approval request {request_id} for {len(resources)} resources "
                       f"(est. cost: ${estimated_cost_usd:.2f})")
        
        return request
    
    def approve_request(
        self,
        request_id: str,
        approver: str,
        comment: Optional[str] = None
    ) -> bool:
        """
        Approve a pending request.

        Args:
            request_id: ID of the request to approve
            approver: User approving the request
            comment: Optional approval comment

        Returns:
            True if approved successfully
        """
        if request_id not in self.pending_requests:
            logger.error(f"Request {request_id} not found in pending requests")
            return False
        
        request = self.pending_requests[request_id]
        request.status = ApprovalStatus.APPROVED
        request.approver = approver
        request.approved_at = datetime.now()
        
        if comment:
            request.metadata['approval_comment'] = comment
        
        # Move to history
        self.approval_history.append(request)
        del self.pending_requests[request_id]
        
        logger.info(f"Request {request_id} approved by {approver}")
        return True
    
    def reject_request(
        self,
        request_id: str,
        approver: str,
        reason: str
    ) -> bool:
        """
        Reject a pending request.

        Args:
            request_id: ID of the request to reject
            approver: User rejecting the request
            reason: Reason for rejection

        Returns:
            True if rejected successfully
        """
        if request_id not in self.pending_requests:
            logger.error(f"Request {request_id} not found in pending requests")
            return False
        
        request = self.pending_requests[request_id]
        request.status = ApprovalStatus.REJECTED
        request.approver = approver
        request.approved_at = datetime.now()
        request.rejection_reason = reason
        
        # Move to history
        self.approval_history.append(request)
        del self.pending_requests[request_id]
        
        logger.info(f"Request {request_id} rejected by {approver}: {reason}")
        return True
    
    def get_pending_requests(self) -> List[ApprovalRequest]:
        """Get all pending approval requests."""
        return list(self.pending_requests.values())
    
    def get_request(self, request_id: str) -> Optional[ApprovalRequest]:
        """Get a specific request by ID."""
        # Check pending first
        if request_id in self.pending_requests:
            return self.pending_requests[request_id]
        
        # Check history
        for request in self.approval_history:
            if request.request_id == request_id:
                return request
        
        return None
    
    def add_auto_approval_rule(self, rule: Callable[[ApprovalRequest], bool]) -> None:
        """
        Add a custom auto-approval rule.

        Args:
            rule: Callable that takes ApprovalRequest and returns True if should auto-approve
        """
        self.auto_approval_rules.append(rule)
    
    def _should_auto_approve(self, request: ApprovalRequest) -> bool:
        """Check if request should be auto-approved."""
        # Don't auto-approve if policy requires approval and cost exceeds threshold
        if request.requires_approval:
            return False
        
        # Check production environment
        env_tags = request.metadata.get('environment_tags', [])
        if any(tag.lower() in ['prod', 'production'] for tag in env_tags):
            logger.info(f"Request {request.request_id} requires approval: production environment")
            return False
        
        # Apply custom rules
        for rule in self.auto_approval_rules:
            try:
                if not rule(request):
                    return False
            except Exception as e:
                logger.error(f"Error applying auto-approval rule: {e}")
                return False
        
        return True
    
    def _extract_environment_tags(self, resources: List[Dict[str, Any]]) -> List[str]:
        """Extract environment tags from resources."""
        env_tags = set()
        
        for resource in resources:
            tags = resource.get('Tags', {})
            for key in ['env', 'environment', 'Environment', 'Env']:
                if key in tags:
                    env_tags.add(tags[key])
        
        return list(env_tags)
    
    def generate_approval_summary(self) -> Dict[str, Any]:
        """Generate summary of approval requests."""
        return {
            'pending_count': len(self.pending_requests),
            'total_pending_cost': sum(r.estimated_cost_usd for r in self.pending_requests.values()),
            'total_pending_resources': sum(r.resource_count for r in self.pending_requests.values()),
            'history_count': len(self.approval_history),
            'approved_count': sum(1 for r in self.approval_history if r.status == ApprovalStatus.APPROVED),
            'rejected_count': sum(1 for r in self.approval_history if r.status == ApprovalStatus.REJECTED),
            'auto_approved_count': sum(1 for r in self.approval_history if r.status == ApprovalStatus.AUTO_APPROVED)
        }
