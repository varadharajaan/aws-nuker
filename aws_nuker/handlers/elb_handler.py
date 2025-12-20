"""ELB resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class ELBHandler(ResourceHandler):
    """Handler for Elastic Load Balancers (classic, ALB, NLB)."""

    @property
    def service_name(self) -> str:
        return "elb"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all load balancers."""
        elb = self.session.client("elb")
        elbv2 = self.session.client("elbv2")
        resources = []

        try:
            # List classic load balancers
            classic_lbs = elb.describe_load_balancers()
            for lb in classic_lbs.get("LoadBalancerDescriptions", []):
                resources.append({
                    "id": lb["LoadBalancerName"],
                    "name": lb["LoadBalancerName"],
                    "type": "classic",
                })

            # List ALBs and NLBs
            modern_lbs = elbv2.describe_load_balancers()
            for lb in modern_lbs.get("LoadBalancers", []):
                resources.append({
                    "id": lb["LoadBalancerArn"],
                    "name": lb["LoadBalancerName"],
                    "type": lb.get("Type", "application"),
                })

        except ClientError as e:
            self.logger.error(f"Error listing ELB resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a load balancer."""
        resource_type = resource.get("type")
        resource_id = resource.get("id")

        try:
            if resource_type == "classic":
                elb = self.session.client("elb")
                elb.delete_load_balancer(LoadBalancerName=resource_id)
                return True
            else:
                elbv2 = self.session.client("elbv2")
                elbv2.delete_load_balancer(LoadBalancerArn=resource_id)
                return True

        except ClientError as e:
            self.logger.error(
                f"Error deleting ELB {resource_type} {resource_id}: {str(e)}"
            )
            return False
