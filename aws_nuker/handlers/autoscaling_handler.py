"""AutoScaling resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class AutoScalingHandler(ResourceHandler):
    """Handler for Auto Scaling groups and configurations."""

    @property
    def service_name(self) -> str:
        return "autoscaling"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all Auto Scaling resources."""
        autoscaling = self.session.client("autoscaling")
        resources = []

        try:
            # List Auto Scaling groups
            paginator = autoscaling.get_paginator("describe_auto_scaling_groups")
            for page in paginator.paginate():
                for asg in page.get("AutoScalingGroups", []):
                    resources.append({
                        "id": asg["AutoScalingGroupARN"],
                        "name": asg["AutoScalingGroupName"],
                        "type": "auto_scaling_group",
                    })

        except ClientError as e:
            self.logger.error(f"Error listing Auto Scaling groups: {str(e)}")

        try:
            # List launch configurations
            paginator = autoscaling.get_paginator("describe_launch_configurations")
            for page in paginator.paginate():
                for lc in page.get("LaunchConfigurations", []):
                    resources.append({
                        "id": lc["LaunchConfigurationARN"],
                        "name": lc["LaunchConfigurationName"],
                        "type": "launch_configuration",
                    })

        except ClientError as e:
            self.logger.error(f"Error listing launch configurations: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete an Auto Scaling resource."""
        autoscaling = self.session.client("autoscaling")
        resource_type = resource.get("type")
        resource_name = resource.get("name")

        try:
            if resource_type == "auto_scaling_group":
                autoscaling.delete_auto_scaling_group(
                    AutoScalingGroupName=resource_name,
                    ForceDelete=self.force
                )
                return True

            elif resource_type == "launch_configuration":
                autoscaling.delete_launch_configuration(
                    LaunchConfigurationName=resource_name
                )
                return True

            return False

        except ClientError as e:
            self.logger.error(
                f"Error deleting Auto Scaling {resource_type} {resource_name}: {str(e)}"
            )
            return False
