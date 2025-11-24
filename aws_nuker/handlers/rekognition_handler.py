"""Rekognition resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class RekognitionHandler(ResourceHandler):
    """Handler for Amazon Rekognition resources."""

    @property
    def service_name(self) -> str:
        return "rekognition"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all Rekognition resources."""
        rekognition = self.session.client("rekognition")
        resources = []

        try:
            # List collections
            paginator = rekognition.get_paginator("list_collections")
            for page in paginator.paginate():
                for collection_id in page.get("CollectionIds", []):
                    resources.append({
                        "id": collection_id,
                        "name": collection_id,
                        "type": "collection",
                    })

        except ClientError as e:
            self.logger.error(f"Error listing Rekognition collections: {str(e)}")

        try:
            # List stream processors
            paginator = rekognition.get_paginator("list_stream_processors")
            for page in paginator.paginate():
                for processor in page.get("StreamProcessors", []):
                    resources.append({
                        "id": processor["Name"],
                        "name": processor["Name"],
                        "type": "stream_processor",
                        "status": processor.get("Status", ""),
                    })

        except ClientError as e:
            self.logger.error(f"Error listing Rekognition stream processors: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a Rekognition resource."""
        rekognition = self.session.client("rekognition")
        resource_type = resource.get("type")
        resource_name = resource.get("name")

        try:
            if resource_type == "collection":
                rekognition.delete_collection(CollectionId=resource_name)
                return True

            elif resource_type == "stream_processor":
                # Stop processor if running
                status = resource.get("status", "")
                if status == "RUNNING":
                    try:
                        rekognition.stop_stream_processor(Name=resource_name)
                    except ClientError as e:
                        error_code = e.response.get("Error", {}).get("Code", "")
                        if error_code not in ["ResourceNotFoundException"]:
                            self.logger.warning(
                                f"Error stopping stream processor {resource_name}: {str(e)}"
                            )

                rekognition.delete_stream_processor(Name=resource_name)
                return True

            return False

        except ClientError as e:
            self.logger.error(
                f"Error deleting Rekognition {resource_type} {resource_name}: {str(e)}"
            )
            return False
