"""Handler for QUICKSIGHT resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class QuicksightHandler(ResourceHandler):
    """Handler for QUICKSIGHT resources."""

    @property
    def service_name(self) -> str:
        return "quicksight"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all QUICKSIGHT resources."""
        client = self.session.client("quicksight")
        resources = []

        try:
            response = client.list_data_sets()
            for item in response.get("DataSetSummaries", []):
                resources.append({
                    "id": item.get("DataSetId", ""),
                    "name": item.get("Name", ""),
                    "type": "dataset",
                })
        except ClientError as e:
            self.logger.error(f"Error listing QUICKSIGHT resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a QUICKSIGHT resource."""
        client = self.session.client("quicksight")
        resource_id = resource.get("id")

        try:
            client.delete_data_set(DataSetId=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting QUICKSIGHT resource {resource_id}: {str(e)}")
            return False
