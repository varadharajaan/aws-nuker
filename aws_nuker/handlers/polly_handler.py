"""Polly resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class PollyHandler(ResourceHandler):
    """Handler for Amazon Polly resources."""

    @property
    def service_name(self) -> str:
        return "polly"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all Polly resources."""
        polly = self.session.client("polly")
        resources = []

        try:
            # List lexicons
            response = polly.list_lexicons()
            for lexicon in response.get("Lexicons", []):
                resources.append({
                    "id": lexicon["Name"],
                    "name": lexicon["Name"],
                    "type": "lexicon",
                })

        except ClientError as e:
            self.logger.error(f"Error listing Polly lexicons: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a Polly resource."""
        polly = self.session.client("polly")
        resource_name = resource.get("name")

        try:
            polly.delete_lexicon(Name=resource_name)
            return True
        except ClientError as e:
            self.logger.error(
                f"Error deleting Polly lexicon {resource_name}: {str(e)}"
            )
            return False
