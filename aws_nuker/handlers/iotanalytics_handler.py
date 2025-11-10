"""Handler for IOTANALYTICS resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class IotanalyticsHandler(ResourceHandler):
    """Handler for IOTANALYTICS resources."""

    @property
    def service_name(self) -> str:
        return "iotanalytics"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all IOTANALYTICS resources."""
        client = self.session.client("iotanalytics")
        resources = []

        try:
            paginator = client.get_paginator("list_datasets")
            for page in paginator.paginate():
                for item in page.get("datasetSummaries", []):
                    resources.append({
                        "id": item.get("datasetName", ""),
                        "name": item.get("datasetName", ""),
                        "type": "dataset",
                    })
        except ClientError as e:
            self.logger.error(f"Error listing IOTANALYTICS resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a IOTANALYTICS resource."""
        client = self.session.client("iotanalytics")
        resource_id = resource.get("id")

        try:
            client.delete_dataset(datasetName=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting IOTANALYTICS resource {resource_id}: {str(e)}")
            return False
