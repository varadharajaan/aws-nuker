"""CloudSearch resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class CloudSearchHandler(ResourceHandler):
    """Handler for Amazon CloudSearch resources."""

    @property
    def service_name(self) -> str:
        return "cloudsearch"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all CloudSearch domains."""
        cloudsearch = self.session.client("cloudsearch")
        resources = []

        try:
            # List domains
            response = cloudsearch.describe_domains()
            for domain in response.get("DomainStatusList", []):
                resources.append({
                    "id": domain["ARN"],
                    "name": domain["DomainName"],
                    "type": "domain",
                })

        except ClientError as e:
            self.logger.error(f"Error listing CloudSearch domains: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a CloudSearch domain."""
        cloudsearch = self.session.client("cloudsearch")
        domain_name = resource.get("name")

        try:
            cloudsearch.delete_domain(DomainName=domain_name)
            return True
        except ClientError as e:
            self.logger.error(
                f"Error deleting CloudSearch domain {domain_name}: {str(e)}"
            )
            return False
