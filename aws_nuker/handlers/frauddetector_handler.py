"""Fraud Detector resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class FraudDetectorHandler(ResourceHandler):
    """Handler for Amazon Fraud Detector resources."""

    @property
    def service_name(self) -> str:
        return "frauddetector"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all Fraud Detector resources."""
        frauddetector = self.session.client("frauddetector")
        resources = []

        try:
            # List detectors
            paginator = frauddetector.get_paginator("get_detectors")
            for page in paginator.paginate():
                for detector in page.get("detectors", []):
                    resources.append({
                        "id": detector["detectorId"],
                        "name": detector["detectorId"],
                        "type": "detector",
                    })

        except ClientError as e:
            self.logger.error(f"Error listing Fraud Detector detectors: {str(e)}")

        try:
            # List models
            paginator = frauddetector.get_paginator("get_models")
            for page in paginator.paginate():
                for model in page.get("models", []):
                    resources.append({
                        "id": model["modelId"],
                        "name": model["modelId"],
                        "type": "model",
                        "model_type": model.get("modelType", ""),
                    })

        except ClientError as e:
            self.logger.error(f"Error listing Fraud Detector models: {str(e)}")

        try:
            # List outcomes
            paginator = frauddetector.get_paginator("get_outcomes")
            for page in paginator.paginate():
                for outcome in page.get("outcomes", []):
                    resources.append({
                        "id": outcome["name"],
                        "name": outcome["name"],
                        "type": "outcome",
                    })

        except ClientError as e:
            self.logger.error(f"Error listing Fraud Detector outcomes: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a Fraud Detector resource."""
        frauddetector = self.session.client("frauddetector")
        resource_type = resource.get("type")
        resource_name = resource.get("name")

        try:
            if resource_type == "detector":
                frauddetector.delete_detector(detectorId=resource_name)
                return True

            elif resource_type == "model":
                model_type = resource.get("model_type", "ONLINE_FRAUD_INSIGHTS")
                frauddetector.delete_model(
                    modelId=resource_name,
                    modelType=model_type
                )
                return True

            elif resource_type == "outcome":
                frauddetector.delete_outcome(name=resource_name)
                return True

            return False

        except ClientError as e:
            self.logger.error(
                f"Error deleting Fraud Detector {resource_type} {resource_name}: {str(e)}"
            )
            return False
