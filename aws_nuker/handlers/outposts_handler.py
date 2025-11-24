"""Outposts resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class OutpostsHandler(ResourceHandler):
    """Handler for AWS Outposts resources."""

    @property
    def service_name(self) -> str:
        return "outposts"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all Outposts resources."""
        outposts = self.session.client("outposts")
        resources = []

        try:
            # List outposts
            paginator = outposts.get_paginator("list_outposts")
            for page in paginator.paginate():
                for outpost in page.get("Outposts", []):
                    resources.append({
                        "id": outpost["OutpostArn"],
                        "name": outpost.get("Name", outpost["OutpostId"]),
                        "type": "outpost",
                        "outpost_id": outpost["OutpostId"],
                    })

        except ClientError as e:
            self.logger.error(f"Error listing Outposts: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete an Outpost."""
        outposts = self.session.client("outposts")
        outpost_id = resource.get("outpost_id")

        try:
            outposts.delete_outpost(OutpostId=outpost_id)
            return True
        except ClientError as e:
            self.logger.error(
                f"Error deleting Outpost {outpost_id}: {str(e)}"
            )
            return False
