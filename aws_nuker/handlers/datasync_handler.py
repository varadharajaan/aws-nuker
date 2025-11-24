"""DataSync resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class DataSyncHandler(ResourceHandler):
    """Handler for DataSync tasks and locations."""

    @property
    def service_name(self) -> str:
        return "datasync"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all DataSync resources."""
        datasync = self.session.client("datasync")
        resources = []

        try:
            # List tasks
            paginator = datasync.get_paginator("list_tasks")
            for page in paginator.paginate():
                for task in page.get("Tasks", []):
                    resources.append({
                        "id": task["TaskArn"],
                        "name": task.get("Name", task["TaskArn"]),
                        "type": "task",
                        "status": task.get("Status", ""),
                    })

        except ClientError as e:
            self.logger.error(f"Error listing DataSync tasks: {str(e)}")

        try:
            # List locations
            paginator = datasync.get_paginator("list_locations")
            for page in paginator.paginate():
                for location in page.get("Locations", []):
                    resources.append({
                        "id": location["LocationArn"],
                        "name": location.get("LocationUri", location["LocationArn"]),
                        "type": "location",
                    })

        except ClientError as e:
            self.logger.error(f"Error listing DataSync locations: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a DataSync resource."""
        datasync = self.session.client("datasync")
        resource_type = resource.get("type")
        resource_arn = resource.get("id")

        try:
            if resource_type == "task":
                datasync.delete_task(TaskArn=resource_arn)
                return True

            elif resource_type == "location":
                datasync.delete_location(LocationArn=resource_arn)
                return True

            return False

        except ClientError as e:
            self.logger.error(
                f"Error deleting DataSync {resource_type} {resource_arn}: {str(e)}"
            )
            return False
