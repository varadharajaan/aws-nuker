"""Handler for DATASYNC resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class DatasyncHandler(ResourceHandler):
    """Handler for DATASYNC resources."""

    @property
    def service_name(self) -> str:
        return "datasync"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all DATASYNC resources."""
        client = self.session.client("datasync")
        resources = []

        try:
            paginator = client.get_paginator("list_tasks")
            for page in paginator.paginate():
                for item in page.get("Tasks", []):
                    resources.append({
                        "id": item.get("TaskArn", ""),
                        "name": item.get("TaskArn", ""),
                        "type": "task",
                    })
        except ClientError as e:
            self.logger.error(f"Error listing DATASYNC resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a DATASYNC resource."""
        client = self.session.client("datasync")
        resource_id = resource.get("id")

        try:
            client.delete_task(TaskArn=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting DATASYNC resource {resource_id}: {str(e)}")
            return False
