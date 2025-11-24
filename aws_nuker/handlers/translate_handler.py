"""Translate resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class TranslateHandler(ResourceHandler):
    """Handler for Amazon Translate resources."""

    @property
    def service_name(self) -> str:
        return "translate"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all Translate resources."""
        translate = self.session.client("translate")
        resources = []

        try:
            # List terminologies
            response = translate.list_terminologies()
            for terminology in response.get("TerminologyPropertiesList", []):
                resources.append({
                    "id": terminology["Name"],
                    "name": terminology["Name"],
                    "type": "terminology",
                })

        except ClientError as e:
            self.logger.error(f"Error listing Translate terminologies: {str(e)}")

        try:
            # List parallel data
            response = translate.list_parallel_data()
            for data in response.get("ParallelDataPropertiesList", []):
                resources.append({
                    "id": data["Name"],
                    "name": data["Name"],
                    "type": "parallel_data",
                    "status": data.get("Status", ""),
                })

        except ClientError as e:
            self.logger.error(f"Error listing Translate parallel data: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a Translate resource."""
        translate = self.session.client("translate")
        resource_type = resource.get("type")
        resource_name = resource.get("name")

        try:
            if resource_type == "terminology":
                translate.delete_terminology(Name=resource_name)
                return True

            elif resource_type == "parallel_data":
                translate.delete_parallel_data(Name=resource_name)
                return True

            return False

        except ClientError as e:
            self.logger.error(
                f"Error deleting Translate {resource_type} {resource_name}: {str(e)}"
            )
            return False
