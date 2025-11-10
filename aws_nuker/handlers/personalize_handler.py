"""Handler for PERSONALIZE resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class PersonalizeHandler(ResourceHandler):
    """Handler for PERSONALIZE resources."""

    @property
    def service_name(self) -> str:
        return "personalize"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all PERSONALIZE resources."""
        client = self.session.client("personalize")
        resources = []

        try:
            paginator = client.get_paginator("list_solutions")
            for page in paginator.paginate():
                for item in page.get("solutions", []):
                    resources.append({
                        "id": item.get("solutionArn", ""),
                        "name": item.get("name", ""),
                        "type": "solution",
                    })
        except ClientError as e:
            self.logger.error(f"Error listing PERSONALIZE resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a PERSONALIZE resource."""
        client = self.session.client("personalize")
        resource_id = resource.get("id")

        try:
            client.delete_solution(solutionArn=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting PERSONALIZE resource {resource_id}: {str(e)}")
            return False
