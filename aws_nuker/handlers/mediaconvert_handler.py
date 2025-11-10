"""Handler for MEDIACONVERT resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class MediaconvertHandler(ResourceHandler):
    """Handler for MEDIACONVERT resources."""

    @property
    def service_name(self) -> str:
        return "mediaconvert"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all MEDIACONVERT resources."""
        client = self.session.client("mediaconvert")
        resources = []

        try:
            paginator = client.get_paginator("list_jobs")
            for page in paginator.paginate():
                for item in page.get("Jobs", []):
                    resources.append({
                        "id": item.get("Id", ""),
                        "name": item.get("Id", ""),
                        "type": "job",
                    })
        except ClientError as e:
            self.logger.error(f"Error listing MEDIACONVERT resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a MEDIACONVERT resource."""
        client = self.session.client("mediaconvert")
        resource_id = resource.get("id")

        try:
            client.cancel_job(Id=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting MEDIACONVERT resource {resource_id}: {str(e)}")
            return False
