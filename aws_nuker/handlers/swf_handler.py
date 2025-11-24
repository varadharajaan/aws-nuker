"""SWF resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class SWFHandler(ResourceHandler):
    """Handler for Amazon Simple Workflow Service resources."""

    @property
    def service_name(self) -> str:
        return "swf"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all SWF domains."""
        swf = self.session.client("swf")
        resources = []

        try:
            # List domains (registered)
            paginator = swf.get_paginator("list_domains")
            for page in paginator.paginate(registrationStatus="REGISTERED"):
                for domain in page.get("domainInfos", []):
                    resources.append({
                        "id": domain["name"],
                        "name": domain["name"],
                        "type": "domain",
                        "status": domain.get("status", ""),
                    })

        except ClientError as e:
            self.logger.error(f"Error listing SWF domains: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete an SWF domain."""
        swf = self.session.client("swf")
        domain_name = resource.get("name")

        try:
            swf.deprecate_domain(name=domain_name)
            return True
        except ClientError as e:
            self.logger.error(
                f"Error deprecating SWF domain {domain_name}: {str(e)}"
            )
            return False
