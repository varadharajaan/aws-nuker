"""Macie resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class MacieHandler(ResourceHandler):
    """Handler for Amazon Macie."""

    @property
    def service_name(self) -> str:
        return "macie"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all Macie resources."""
        macie2 = self.session.client("macie2")
        resources = []

        try:
            # Check if Macie is enabled
            response = macie2.get_macie_session()
            if response.get("status") == "ENABLED":
                resources.append({
                    "id": "macie-session",
                    "name": "Macie Session",
                    "type": "macie_session",
                    "status": response.get("status"),
                })

        except ClientError as e:
            # Macie might not be enabled
            if e.response.get("Error", {}).get("Code") != "ResourceNotFoundException":
                self.logger.error(f"Error checking Macie status: {str(e)}")

        try:
            # List classification jobs
            paginator = macie2.get_paginator("list_classification_jobs")
            for page in paginator.paginate():
                for job in page.get("items", []):
                    resources.append({
                        "id": job["jobId"],
                        "name": job.get("name", job["jobId"]),
                        "type": "classification_job",
                        "status": job.get("jobStatus", ""),
                    })

        except ClientError as e:
            self.logger.error(f"Error listing Macie classification jobs: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a Macie resource."""
        macie2 = self.session.client("macie2")
        resource_type = resource.get("type")
        resource_id = resource.get("id")

        try:
            if resource_type == "classification_job":
                # Cancel and delete job
                macie2.delete_classification_job(jobId=resource_id)
                return True

            elif resource_type == "macie_session":
                # Disable Macie
                macie2.disable_macie()
                return True

            return False

        except ClientError as e:
            self.logger.error(
                f"Error deleting Macie {resource_type} {resource_id}: {str(e)}"
            )
            return False
