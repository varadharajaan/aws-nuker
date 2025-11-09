"""GuardDuty resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class GuardDutyHandler(ResourceHandler):
    """Handler for Amazon GuardDuty detectors."""

    @property
    def service_name(self) -> str:
        return "guardduty"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all GuardDuty detectors."""
        guardduty = self.session.client("guardduty")
        resources = []

        try:
            detectors_response = guardduty.list_detectors()
            for detector_id in detectors_response.get("DetectorIds", []):
                resources.append({
                    "id": detector_id,
                    "name": detector_id,
                    "type": "detector",
                })

        except ClientError as e:
            self.logger.error(f"Error listing GuardDuty detectors: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a GuardDuty detector."""
        guardduty = self.session.client("guardduty")
        detector_id = resource.get("id")

        try:
            guardduty.delete_detector(DetectorId=detector_id)
            return True
        except ClientError as e:
            self.logger.error(
                f"Error deleting GuardDuty detector {detector_id}: {str(e)}"
            )
            return False
