"""Transcribe resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class TranscribeHandler(ResourceHandler):
    """Handler for Amazon Transcribe resources."""

    @property
    def service_name(self) -> str:
        return "transcribe"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all Transcribe resources."""
        transcribe = self.session.client("transcribe")
        resources = []

        try:
            # List vocabularies
            paginator = transcribe.get_paginator("list_vocabularies")
            for page in paginator.paginate():
                for vocab in page.get("Vocabularies", []):
                    resources.append({
                        "id": vocab["VocabularyName"],
                        "name": vocab["VocabularyName"],
                        "type": "vocabulary",
                        "state": vocab.get("VocabularyState", ""),
                    })

        except ClientError as e:
            self.logger.error(f"Error listing Transcribe vocabularies: {str(e)}")

        try:
            # List language models
            response = transcribe.list_language_models()
            for model in response.get("Models", []):
                resources.append({
                    "id": model["ModelName"],
                    "name": model["ModelName"],
                    "type": "language_model",
                })

        except ClientError as e:
            self.logger.error(f"Error listing Transcribe language models: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a Transcribe resource."""
        transcribe = self.session.client("transcribe")
        resource_type = resource.get("type")
        resource_name = resource.get("name")

        try:
            if resource_type == "vocabulary":
                transcribe.delete_vocabulary(VocabularyName=resource_name)
                return True

            elif resource_type == "language_model":
                transcribe.delete_language_model(ModelName=resource_name)
                return True

            return False

        except ClientError as e:
            self.logger.error(
                f"Error deleting Transcribe {resource_type} {resource_name}: {str(e)}"
            )
            return False
