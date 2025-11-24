"""CloudFront resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class CloudFrontHandler(ResourceHandler):
    """Handler for CloudFront distributions."""

    @property
    def service_name(self) -> str:
        return "cloudfront"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all CloudFront distributions."""
        # CloudFront is a global service, only list in us-east-1
        if self.region != "us-east-1":
            return []

        cloudfront = self.session.client("cloudfront")
        resources = []

        try:
            paginator = cloudfront.get_paginator("list_distributions")
            for page in paginator.paginate():
                distribution_list = page.get("DistributionList", {})
                for dist in distribution_list.get("Items", []):
                    resources.append({
                        "id": dist["Id"],
                        "name": dist.get("DomainName", dist["Id"]),
                        "type": "distribution",
                        "status": dist.get("Status", ""),
                        "enabled": dist.get("Enabled", False),
                        "etag": dist.get("ETag", ""),
                    })

        except ClientError as e:
            self.logger.error(f"Error listing CloudFront distributions: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a CloudFront distribution."""
        cloudfront = self.session.client("cloudfront")
        distribution_id = resource.get("id")
        enabled = resource.get("enabled", False)

        try:
            # Get current distribution config
            response = cloudfront.get_distribution(Id=distribution_id)
            etag = response["ETag"]
            config = response["Distribution"]["DistributionConfig"]

            # If distribution is enabled, disable it first
            if enabled:
                config["Enabled"] = False
                cloudfront.update_distribution(
                    Id=distribution_id,
                    DistributionConfig=config,
                    IfMatch=etag
                )
                self.logger.info(
                    f"Disabled CloudFront distribution {distribution_id}. "
                    "It must be fully deployed before deletion."
                )
                # Note: Distribution must be in "Deployed" state before deletion
                # This may take several minutes, so deletion might fail initially
                return True

            # If already disabled, try to delete
            response = cloudfront.get_distribution(Id=distribution_id)
            etag = response["ETag"]
            cloudfront.delete_distribution(Id=distribution_id, IfMatch=etag)
            return True

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "")
            if error_code == "DistributionNotDisabled":
                self.logger.warning(
                    f"Distribution {distribution_id} must be disabled before deletion"
                )
            elif error_code == "PreconditionFailed":
                self.logger.warning(
                    f"Distribution {distribution_id} is still deploying, retry later"
                )
            else:
                self.logger.error(
                    f"Error deleting CloudFront distribution {distribution_id}: {str(e)}"
                )
            return False
