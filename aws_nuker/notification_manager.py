"""
Notification manager for AWS Nuker.

Handles notifications via email, Slack, and other channels.
"""

import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import boto3
from botocore.exceptions import ClientError
import logging

logger = logging.getLogger(__name__)


@dataclass
class NotificationMessage:
    """Represents a notification message."""

    subject: str
    body: str
    severity: str = "info"  # info, warning, error, critical
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class NotificationManager:
    """Manages notifications for cleanup operations."""

    def __init__(
        self,
        email_addresses: Optional[List[str]] = None,
        slack_webhook_url: Optional[str] = None,
        sns_topic_arn: Optional[str] = None
    ):
        """
        Initialize notification manager.

        Args:
            email_addresses: List of email addresses for notifications
            slack_webhook_url: Slack webhook URL for notifications
            sns_topic_arn: SNS topic ARN for notifications
        """
        self.email_addresses = email_addresses or []
        self.slack_webhook_url = slack_webhook_url
        self.sns_topic_arn = sns_topic_arn
        
        self.ses_client = None
        self.sns_client = None
        
        if self.email_addresses:
            try:
                self.ses_client = boto3.client('ses', region_name='us-east-1')
            except Exception as e:
                logger.warning(f"Failed to initialize SES client: {e}")
        
        if self.sns_topic_arn:
            try:
                self.sns_client = boto3.client('sns')
            except Exception as e:
                logger.warning(f"Failed to initialize SNS client: {e}")
    
    def send_notification(
        self,
        message: NotificationMessage,
        channels: Optional[List[str]] = None
    ) -> Dict[str, bool]:
        """
        Send notification through specified channels.

        Args:
            message: NotificationMessage to send
            channels: List of channels ('email', 'slack', 'sns'). If None, uses all configured.

        Returns:
            Dictionary with channel names and success status
        """
        results = {}
        
        if channels is None:
            channels = []
            if self.email_addresses:
                channels.append('email')
            if self.slack_webhook_url:
                channels.append('slack')
            if self.sns_topic_arn:
                channels.append('sns')
        
        if 'email' in channels and self.email_addresses:
            results['email'] = self._send_email(message)
        
        if 'slack' in channels and self.slack_webhook_url:
            results['slack'] = self._send_slack(message)
        
        if 'sns' in channels and self.sns_topic_arn:
            results['sns'] = self._send_sns(message)
        
        return results
    
    def notify_cleanup_start(
        self,
        policy_name: str,
        resource_count: int,
        regions: List[str],
        services: List[str]
    ) -> Dict[str, bool]:
        """
        Send notification when cleanup starts.

        Args:
            policy_name: Name of cleanup policy
            resource_count: Number of resources to be deleted
            regions: AWS regions
            services: AWS services

        Returns:
            Notification send results
        """
        message = NotificationMessage(
            subject=f"AWS Nuker: Cleanup Started - {policy_name}",
            body=f"""
AWS Nuker Cleanup Operation Started

Policy: {policy_name}
Resources to delete: {resource_count}
Regions: {', '.join(regions)}
Services: {', '.join(services)}
Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

This is an automated notification from AWS Nuker.
            """.strip(),
            severity="warning",
            metadata={
                'policy_name': policy_name,
                'resource_count': resource_count,
                'regions': regions,
                'services': services
            }
        )
        
        return self.send_notification(message)
    
    def notify_cleanup_complete(
        self,
        policy_name: str,
        deleted_count: int,
        failed_count: int,
        duration_seconds: float
    ) -> Dict[str, bool]:
        """
        Send notification when cleanup completes.

        Args:
            policy_name: Name of cleanup policy
            deleted_count: Number of successfully deleted resources
            failed_count: Number of failed deletions
            duration_seconds: Duration of cleanup operation

        Returns:
            Notification send results
        """
        severity = "info" if failed_count == 0 else "warning"
        
        message = NotificationMessage(
            subject=f"AWS Nuker: Cleanup Completed - {policy_name}",
            body=f"""
AWS Nuker Cleanup Operation Completed

Policy: {policy_name}
Successfully deleted: {deleted_count}
Failed deletions: {failed_count}
Duration: {duration_seconds:.2f} seconds
Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

This is an automated notification from AWS Nuker.
            """.strip(),
            severity=severity,
            metadata={
                'policy_name': policy_name,
                'deleted_count': deleted_count,
                'failed_count': failed_count,
                'duration_seconds': duration_seconds
            }
        )
        
        return self.send_notification(message)
    
    def notify_approval_required(
        self,
        request_id: str,
        policy_name: str,
        resource_count: int,
        estimated_cost: float
    ) -> Dict[str, bool]:
        """
        Send notification when approval is required.

        Args:
            request_id: Approval request ID
            policy_name: Name of cleanup policy
            resource_count: Number of resources
            estimated_cost: Estimated cost in USD

        Returns:
            Notification send results
        """
        message = NotificationMessage(
            subject=f"AWS Nuker: Approval Required - {policy_name}",
            body=f"""
AWS Nuker Approval Request

Request ID: {request_id}
Policy: {policy_name}
Resources: {resource_count}
Estimated Cost: ${estimated_cost:.2f}

This deletion requires approval. Please review and approve/reject.

This is an automated notification from AWS Nuker.
            """.strip(),
            severity="warning",
            metadata={
                'request_id': request_id,
                'policy_name': policy_name,
                'resource_count': resource_count,
                'estimated_cost': estimated_cost
            }
        )
        
        return self.send_notification(message)
    
    def _send_email(self, message: NotificationMessage) -> bool:
        """Send email notification via SES."""
        if not self.ses_client or not self.email_addresses:
            return False
        
        try:
            # Use first email as sender (must be verified in SES)
            sender = self.email_addresses[0]
            
            response = self.ses_client.send_email(
                Source=sender,
                Destination={'ToAddresses': self.email_addresses},
                Message={
                    'Subject': {'Data': message.subject},
                    'Body': {'Text': {'Data': message.body}}
                }
            )
            
            logger.info(f"Email sent successfully: {response['MessageId']}")
            return True
            
        except ClientError as e:
            logger.error(f"Failed to send email: {e}")
            return False
    
    def _send_slack(self, message: NotificationMessage) -> bool:
        """Send Slack notification via webhook."""
        if not self.slack_webhook_url:
            return False
        
        try:
            import requests
            
            # Map severity to Slack color
            color_map = {
                'info': '#36a64f',
                'warning': '#ff9900',
                'error': '#ff0000',
                'critical': '#990000'
            }
            
            slack_payload = {
                'text': message.subject,
                'attachments': [{
                    'color': color_map.get(message.severity, '#36a64f'),
                    'text': message.body,
                    'footer': 'AWS Nuker',
                    'ts': int(datetime.now().timestamp())
                }]
            }
            
            response = requests.post(
                self.slack_webhook_url,
                json=slack_payload,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("Slack notification sent successfully")
                return True
            else:
                logger.error(f"Slack notification failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send Slack notification: {e}")
            return False
    
    def _send_sns(self, message: NotificationMessage) -> bool:
        """Send SNS notification."""
        if not self.sns_client or not self.sns_topic_arn:
            return False
        
        try:
            response = self.sns_client.publish(
                TopicArn=self.sns_topic_arn,
                Subject=message.subject,
                Message=message.body,
                MessageAttributes={
                    'severity': {
                        'DataType': 'String',
                        'StringValue': message.severity
                    }
                }
            )
            
            logger.info(f"SNS notification sent: {response['MessageId']}")
            return True
            
        except ClientError as e:
            logger.error(f"Failed to send SNS notification: {e}")
            return False
