"""MediaTailor resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class MediaTailorHandler(ResourceHandler):
    """Handler for AWS Elemental MediaTailor resources."""

    @property
    def service_name(self) -> str:
        return "mediatailor"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all MediaTailor resources."""
        mediatailor = self.session.client("mediatailor")
        resources = []

        try:
            # List playback configurations
            paginator = mediatailor.get_paginator("list_playback_configurations")
            for page in paginator.paginate():
                for config in page.get("Items", []):
                    resources.append({
                        "id": config["PlaybackConfigurationArn"],
                        "name": config["Name"],
                        "type": "playback_configuration",
                    })

        except ClientError as e:
            self.logger.error(f"Error listing MediaTailor playback configurations: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a MediaTailor resource."""
        mediatailor = self.session.client("mediatailor")
        resource_name = resource.get("name")

        try:
            mediatailor.delete_playback_configuration(Name=resource_name)
            return True
        except ClientError as e:
            self.logger.error(
                f"Error deleting MediaTailor playback configuration {resource_name}: {str(e)}"
            )
            return False
