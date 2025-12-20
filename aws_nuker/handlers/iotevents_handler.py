"""IoT Events resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class IoTEventsHandler(ResourceHandler):
    """Handler for AWS IoT Events resources."""

    @property
    def service_name(self) -> str:
        return "iotevents"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all IoT Events resources."""
        iotevents = self.session.client("iotevents")
        resources = []

        try:
            # List detector models
            response = iotevents.list_detector_models()
            for model in response.get("detectorModelSummaries", []):
                resources.append({
                    "id": model["detectorModelName"],
                    "name": model["detectorModelName"],
                    "type": "detector_model",
                })

        except ClientError as e:
            self.logger.error(f"Error listing IoT Events detector models: {str(e)}")

        try:
            # List inputs
            response = iotevents.list_inputs()
            for input_item in response.get("inputSummaries", []):
                resources.append({
                    "id": input_item["inputName"],
                    "name": input_item["inputName"],
                    "type": "input",
                })

        except ClientError as e:
            self.logger.error(f"Error listing IoT Events inputs: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete an IoT Events resource."""
        iotevents = self.session.client("iotevents")
        resource_type = resource.get("type")
        resource_name = resource.get("name")

        try:
            if resource_type == "detector_model":
                iotevents.delete_detector_model(detectorModelName=resource_name)
                return True

            elif resource_type == "input":
                iotevents.delete_input(inputName=resource_name)
                return True

            return False

        except ClientError as e:
            self.logger.error(
                f"Error deleting IoT Events {resource_type} {resource_name}: {str(e)}"
            )
            return False
