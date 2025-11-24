"""CloudTrail resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class CloudTrailHandler(ResourceHandler):
    """Handler for CloudTrail trails."""

    @property
    def service_name(self) -> str:
        return "cloudtrail"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all CloudTrail trails."""
        cloudtrail = self.session.client("cloudtrail")
        resources = []

        try:
            paginator = cloudtrail.get_paginator("list_trails")
            for page in paginator.paginate():
                for trail in page.get("Trails", []):
                    trail_arn = trail["TrailARN"]
                    trail_name = trail.get("Name", trail_arn.split("/")[-1])
                    
                    resources.append({
                        "id": trail_arn,
                        "name": trail_name,
                        "type": "trail",
                        "home_region": trail.get("HomeRegion", ""),
                    })

        except ClientError as e:
            self.logger.error(f"Error listing CloudTrail trails: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a CloudTrail trail."""
        cloudtrail = self.session.client("cloudtrail")
        trail_name = resource.get("name")

        try:
            cloudtrail.delete_trail(Name=trail_name)
            return True
        except ClientError as e:
            self.logger.error(
                f"Error deleting CloudTrail trail {trail_name}: {str(e)}"
            )
            return False
