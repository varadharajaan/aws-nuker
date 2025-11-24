"""MediaConvert resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class MediaConvertHandler(ResourceHandler):
    """Handler for AWS Elemental MediaConvert resources."""

    @property
    def service_name(self) -> str:
        return "mediaconvert"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all MediaConvert resources."""
        mediaconvert = self.session.client("mediaconvert")
        resources = []

        try:
            # Get endpoint first
            endpoints = mediaconvert.describe_endpoints()
            if not endpoints.get("Endpoints"):
                return resources
            
            endpoint_url = endpoints["Endpoints"][0]["Url"]
            mediaconvert = self.session.client("mediaconvert", endpoint_url=endpoint_url)

        except ClientError as e:
            self.logger.error(f"Error getting MediaConvert endpoint: {str(e)}")
            return resources

        try:
            # List job templates
            paginator = mediaconvert.get_paginator("list_job_templates")
            for page in paginator.paginate():
                for template in page.get("JobTemplates", []):
                    resources.append({
                        "id": template["Arn"],
                        "name": template["Name"],
                        "type": "job_template",
                    })

        except ClientError as e:
            self.logger.error(f"Error listing MediaConvert job templates: {str(e)}")

        try:
            # List presets
            paginator = mediaconvert.get_paginator("list_presets")
            for page in paginator.paginate():
                for preset in page.get("Presets", []):
                    resources.append({
                        "id": preset["Arn"],
                        "name": preset["Name"],
                        "type": "preset",
                    })

        except ClientError as e:
            self.logger.error(f"Error listing MediaConvert presets: {str(e)}")

        try:
            # List queues (skip default)
            paginator = mediaconvert.get_paginator("list_queues")
            for page in paginator.paginate():
                for queue in page.get("Queues", []):
                    if queue["Name"] != "Default":
                        resources.append({
                            "id": queue["Arn"],
                            "name": queue["Name"],
                            "type": "queue",
                        })

        except ClientError as e:
            self.logger.error(f"Error listing MediaConvert queues: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a MediaConvert resource."""
        mediaconvert = self.session.client("mediaconvert")
        
        try:
            # Get endpoint first
            endpoints = mediaconvert.describe_endpoints()
            if not endpoints.get("Endpoints"):
                return False
            
            endpoint_url = endpoints["Endpoints"][0]["Url"]
            mediaconvert = self.session.client("mediaconvert", endpoint_url=endpoint_url)

        except ClientError:
            return False

        resource_type = resource.get("type")
        resource_name = resource.get("name")

        try:
            if resource_type == "job_template":
                mediaconvert.delete_job_template(Name=resource_name)
                return True

            elif resource_type == "preset":
                mediaconvert.delete_preset(Name=resource_name)
                return True

            elif resource_type == "queue":
                mediaconvert.delete_queue(Name=resource_name)
                return True

            return False

        except ClientError as e:
            self.logger.error(
                f"Error deleting MediaConvert {resource_type} {resource_name}: {str(e)}"
            )
            return False
