"""RAM resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class RAMHandler(ResourceHandler):
    """Handler for AWS Resource Access Manager resources."""

    @property
    def service_name(self) -> str:
        return "ram"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all RAM resource shares."""
        ram = self.session.client("ram")
        resources = []

        try:
            # List resource shares (owned by self)
            paginator = ram.get_paginator("get_resource_shares")
            for page in paginator.paginate(resourceOwner="SELF"):
                for share in page.get("resourceShares", []):
                    resources.append({
                        "id": share["resourceShareArn"],
                        "name": share.get("name", share["resourceShareArn"].split("/")[-1]),
                        "type": "resource_share",
                        "status": share.get("status", ""),
                    })

        except ClientError as e:
            self.logger.error(f"Error listing RAM resource shares: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a RAM resource share."""
        ram = self.session.client("ram")
        share_arn = resource.get("id")

        try:
            ram.delete_resource_share(resourceShareArn=share_arn)
            return True
        except ClientError as e:
            self.logger.error(
                f"Error deleting RAM resource share {share_arn}: {str(e)}"
            )
            return False
