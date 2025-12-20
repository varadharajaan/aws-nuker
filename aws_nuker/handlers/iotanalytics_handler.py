"""IoT Analytics resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class IoTAnalyticsHandler(ResourceHandler):
    """Handler for AWS IoT Analytics resources."""

    @property
    def service_name(self) -> str:
        return "iotanalytics"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all IoT Analytics resources."""
        iotanalytics = self.session.client("iotanalytics")
        resources = []

        try:
            # List channels
            paginator = iotanalytics.get_paginator("list_channels")
            for page in paginator.paginate():
                for channel in page.get("channelSummaries", []):
                    resources.append({
                        "id": channel["channelName"],
                        "name": channel["channelName"],
                        "type": "channel",
                    })

        except ClientError as e:
            self.logger.error(f"Error listing IoT Analytics channels: {str(e)}")

        try:
            # List datastores
            paginator = iotanalytics.get_paginator("list_datastores")
            for page in paginator.paginate():
                for datastore in page.get("datastoreSummaries", []):
                    resources.append({
                        "id": datastore["datastoreName"],
                        "name": datastore["datastoreName"],
                        "type": "datastore",
                    })

        except ClientError as e:
            self.logger.error(f"Error listing IoT Analytics datastores: {str(e)}")

        try:
            # List pipelines
            paginator = iotanalytics.get_paginator("list_pipelines")
            for page in paginator.paginate():
                for pipeline in page.get("pipelineSummaries", []):
                    resources.append({
                        "id": pipeline["pipelineName"],
                        "name": pipeline["pipelineName"],
                        "type": "pipeline",
                    })

        except ClientError as e:
            self.logger.error(f"Error listing IoT Analytics pipelines: {str(e)}")

        try:
            # List datasets
            paginator = iotanalytics.get_paginator("list_datasets")
            for page in paginator.paginate():
                for dataset in page.get("datasetSummaries", []):
                    resources.append({
                        "id": dataset["datasetName"],
                        "name": dataset["datasetName"],
                        "type": "dataset",
                    })

        except ClientError as e:
            self.logger.error(f"Error listing IoT Analytics datasets: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete an IoT Analytics resource."""
        iotanalytics = self.session.client("iotanalytics")
        resource_type = resource.get("type")
        resource_name = resource.get("name")

        try:
            if resource_type == "channel":
                iotanalytics.delete_channel(channelName=resource_name)
                return True

            elif resource_type == "datastore":
                iotanalytics.delete_datastore(datastoreName=resource_name)
                return True

            elif resource_type == "pipeline":
                iotanalytics.delete_pipeline(pipelineName=resource_name)
                return True

            elif resource_type == "dataset":
                iotanalytics.delete_dataset(datasetName=resource_name)
                return True

            return False

        except ClientError as e:
            self.logger.error(
                f"Error deleting IoT Analytics {resource_type} {resource_name}: {str(e)}"
            )
            return False
