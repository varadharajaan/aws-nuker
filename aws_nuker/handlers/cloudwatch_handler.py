"""CloudWatch resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class CloudWatchHandler(ResourceHandler):
    """Handler for CloudWatch alarms and log groups."""

    @property
    def service_name(self) -> str:
        return "cloudwatch"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all CloudWatch resources."""
        cw = self.session.client("cloudwatch")
        logs = self.session.client("logs")
        resources = []

        try:
            # List alarms
            alarms_paginator = cw.get_paginator("describe_alarms")
            for page in alarms_paginator.paginate():
                for alarm in page.get("MetricAlarms", []):
                    resources.append({
                        "id": alarm["AlarmArn"],
                        "name": alarm["AlarmName"],
                        "type": "alarm",
                    })

            # List log groups
            logs_paginator = logs.get_paginator("describe_log_groups")
            for page in logs_paginator.paginate():
                for log_group in page.get("logGroups", []):
                    resources.append({
                        "id": log_group["logGroupName"],
                        "name": log_group["logGroupName"],
                        "type": "log_group",
                    })

        except ClientError as e:
            self.logger.error(f"Error listing CloudWatch resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a CloudWatch resource."""
        resource_type = resource.get("type")
        resource_name = resource.get("name")

        try:
            if resource_type == "alarm":
                cw = self.session.client("cloudwatch")
                cw.delete_alarms(AlarmNames=[resource_name])
                return True

            elif resource_type == "log_group":
                logs = self.session.client("logs")
                logs.delete_log_group(logGroupName=resource_name)
                return True

            return False

        except ClientError as e:
            self.logger.error(
                f"Error deleting CloudWatch {resource_type} {resource_name}: {str(e)}"
            )
            return False
