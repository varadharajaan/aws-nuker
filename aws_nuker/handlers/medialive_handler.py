"""MediaLive resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class MediaLiveHandler(ResourceHandler):
    """Handler for AWS Elemental MediaLive resources."""

    @property
    def service_name(self) -> str:
        return "medialive"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all MediaLive resources."""
        medialive = self.session.client("medialive")
        resources = []

        try:
            # List channels
            paginator = medialive.get_paginator("list_channels")
            for page in paginator.paginate():
                for channel in page.get("Channels", []):
                    resources.append({
                        "id": channel["Id"],
                        "name": channel.get("Name", channel["Id"]),
                        "type": "channel",
                        "state": channel.get("State", ""),
                    })

        except ClientError as e:
            self.logger.error(f"Error listing MediaLive channels: {str(e)}")

        try:
            # List inputs
            paginator = medialive.get_paginator("list_inputs")
            for page in paginator.paginate():
                for input_item in page.get("Inputs", []):
                    resources.append({
                        "id": input_item["Id"],
                        "name": input_item.get("Name", input_item["Id"]),
                        "type": "input",
                        "state": input_item.get("State", ""),
                    })

        except ClientError as e:
            self.logger.error(f"Error listing MediaLive inputs: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a MediaLive resource."""
        medialive = self.session.client("medialive")
        resource_type = resource.get("type")
        resource_id = resource.get("id")

        try:
            if resource_type == "channel":
                # Stop channel if running
                state = resource.get("state", "")
                if state in ["RUNNING", "STARTING"]:
                    try:
                        medialive.stop_channel(ChannelId=resource_id)
                    except ClientError as e:
                        error_code = e.response.get("Error", {}).get("Code", "")
                        if error_code not in ["ResourceNotFoundException", "ConflictException"]:
                            self.logger.warning(
                                f"Error stopping MediaLive channel {resource_id}: {str(e)}"
                            )

                medialive.delete_channel(ChannelId=resource_id)
                return True

            elif resource_type == "input":
                medialive.delete_input(InputId=resource_id)
                return True

            return False

        except ClientError as e:
            self.logger.error(
                f"Error deleting MediaLive {resource_type} {resource_id}: {str(e)}"
            )
            return False
