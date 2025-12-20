"""Route53 resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class Route53Handler(ResourceHandler):
    """Handler for Route53 hosted zones."""

    @property
    def service_name(self) -> str:
        return "route53"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all Route53 hosted zones."""
        # Route53 is global, only process in us-east-1
        if self.region != "us-east-1":
            return []

        route53 = self.session.client("route53")
        resources = []

        try:
            paginator = route53.get_paginator("list_hosted_zones")
            for page in paginator.paginate():
                for zone in page.get("HostedZones", []):
                    resources.append({
                        "id": zone["Id"],
                        "name": zone["Name"],
                        "type": "hosted_zone",
                        "private": zone.get("Config", {}).get("PrivateZone", False),
                    })

        except ClientError as e:
            self.logger.error(f"Error listing Route53 hosted zones: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a Route53 hosted zone."""
        route53 = self.session.client("route53")
        zone_id = resource.get("id")

        try:
            # Delete all record sets except NS and SOA
            self._delete_record_sets(route53, zone_id)

            # Delete the hosted zone
            route53.delete_hosted_zone(Id=zone_id)
            return True

        except ClientError as e:
            self.logger.error(
                f"Error deleting Route53 hosted zone {zone_id}: {str(e)}"
            )
            return False

    def _delete_record_sets(self, route53, zone_id: str):
        """Delete all record sets in a hosted zone except NS and SOA."""
        try:
            paginator = route53.get_paginator("list_resource_record_sets")
            for page in paginator.paginate(HostedZoneId=zone_id):
                for record in page.get("ResourceRecordSets", []):
                    # Skip NS and SOA records
                    if record["Type"] not in ["NS", "SOA"]:
                        try:
                            route53.change_resource_record_sets(
                                HostedZoneId=zone_id,
                                ChangeBatch={
                                    "Changes": [
                                        {
                                            "Action": "DELETE",
                                            "ResourceRecordSet": record,
                                        }
                                    ]
                                },
                            )
                        except ClientError:
                            # Continue even if some records fail
                            pass

        except ClientError as e:
            self.logger.warning(
                f"Error deleting record sets for {zone_id}: {str(e)}"
            )
