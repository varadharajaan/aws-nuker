"""Comprehend resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class ComprehendHandler(ResourceHandler):
    """Handler for Amazon Comprehend resources."""

    @property
    def service_name(self) -> str:
        return "comprehend"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all Comprehend resources."""
        comprehend = self.session.client("comprehend")
        resources = []

        try:
            # List document classifiers
            paginator = comprehend.get_paginator("list_document_classifiers")
            for page in paginator.paginate():
                for classifier in page.get("DocumentClassifierPropertiesList", []):
                    resources.append({
                        "id": classifier["DocumentClassifierArn"],
                        "name": classifier.get("DocumentClassifierArn", "").split("/")[-1],
                        "type": "document_classifier",
                        "status": classifier.get("Status", ""),
                    })

        except ClientError as e:
            self.logger.error(f"Error listing Comprehend document classifiers: {str(e)}")

        try:
            # List entity recognizers
            paginator = comprehend.get_paginator("list_entity_recognizers")
            for page in paginator.paginate():
                for recognizer in page.get("EntityRecognizerPropertiesList", []):
                    resources.append({
                        "id": recognizer["EntityRecognizerArn"],
                        "name": recognizer.get("EntityRecognizerArn", "").split("/")[-1],
                        "type": "entity_recognizer",
                        "status": recognizer.get("Status", ""),
                    })

        except ClientError as e:
            self.logger.error(f"Error listing Comprehend entity recognizers: {str(e)}")

        try:
            # List endpoints
            response = comprehend.list_endpoints()
            for endpoint in response.get("EndpointPropertiesList", []):
                resources.append({
                    "id": endpoint["EndpointArn"],
                    "name": endpoint.get("EndpointArn", "").split("/")[-1],
                    "type": "endpoint",
                    "status": endpoint.get("Status", ""),
                })

        except ClientError as e:
            self.logger.error(f"Error listing Comprehend endpoints: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a Comprehend resource."""
        comprehend = self.session.client("comprehend")
        resource_type = resource.get("type")
        resource_arn = resource.get("id")

        try:
            if resource_type == "document_classifier":
                comprehend.delete_document_classifier(DocumentClassifierArn=resource_arn)
                return True

            elif resource_type == "entity_recognizer":
                comprehend.delete_entity_recognizer(EntityRecognizerArn=resource_arn)
                return True

            elif resource_type == "endpoint":
                comprehend.delete_endpoint(EndpointArn=resource_arn)
                return True

            return False

        except ClientError as e:
            self.logger.error(
                f"Error deleting Comprehend {resource_type} {resource_arn}: {str(e)}"
            )
            return False
