"""IVS (Interactive Video Service) resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class IVSHandler(ResourceHandler):
    """Handler for Amazon IVS resources."""

    @property
    def service_name(self) -> str:
        return "ivs"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all IVS resources."""
        ivs = self.session.client("ivs")
        resources = []

        try:
            # List channels
            paginator = ivs.get_paginator("list_channels")
            for page in paginator.paginate():
                for channel in page.get("channels", []):
                    resources.append({
                        "id": channel["arn"],
                        "name": channel.get("name", channel["arn"]),
                        "type": "channel",
                    })

        except ClientError as e:
            self.logger.error(f"Error listing IVS channels: {str(e)}")

        try:
            # List stream keys
            paginator = ivs.get_paginator("list_stream_keys")
            for page in paginator.paginate():
                for stream_key in page.get("streamKeys", []):
                    resources.append({
                        "id": stream_key["arn"],
                        "name": stream_key.get("arn", ""),
                        "type": "stream_key",
                    })

        except ClientError as e:
            self.logger.error(f"Error listing IVS stream keys: {str(e)}")

        try:
            # List recording configurations
            paginator = ivs.get_paginator("list_recording_configurations")
            for page in paginator.paginate():
                for config in page.get("recordingConfigurations", []):
                    resources.append({
                        "id": config["arn"],
                        "name": config.get("name", config["arn"]),
                        "type": "recording_configuration",
                    })

        except ClientError as e:
            self.logger.error(f"Error listing IVS recording configurations: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete an IVS resource."""
        ivs = self.session.client("ivs")
        resource_type = resource.get("type")
        resource_arn = resource.get("id")

        try:
            if resource_type == "channel":
                ivs.delete_channel(arn=resource_arn)
                return True

            elif resource_type == "stream_key":
                ivs.delete_stream_key(arn=resource_arn)
                return True

            elif resource_type == "recording_configuration":
                ivs.delete_recording_configuration(arn=resource_arn)
                return True

            return False

        except ClientError as e:
            self.logger.error(
                f"Error deleting IVS {resource_type} {resource_arn}: {str(e)}"
            )
            return False
