"""Handler for TRANSCRIBE resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class TranscribeHandler(ResourceHandler):
    """Handler for TRANSCRIBE resources."""

    @property
    def service_name(self) -> str:
        return "transcribe"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all TRANSCRIBE resources."""
        client = self.session.client("transcribe")
        resources = []

        try:
            response = client.list_transcription_jobs()
            for item in response.get("TranscriptionJobSummaries", []):
                resources.append({
                    "id": item.get("TranscriptionJobName", ""),
                    "name": item.get("TranscriptionJobName", ""),
                    "type": "job",
                })
        except ClientError as e:
            self.logger.error(f"Error listing TRANSCRIBE resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a TRANSCRIBE resource."""
        client = self.session.client("transcribe")
        resource_id = resource.get("id")

        try:
            client.delete_transcription_job(TranscriptionJobName=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting TRANSCRIBE resource {resource_id}: {str(e)}")
            return False
