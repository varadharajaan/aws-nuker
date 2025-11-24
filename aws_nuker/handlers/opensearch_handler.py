"""OpenSearch resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class OpenSearchHandler(ResourceHandler):
    """Handler for OpenSearch domains."""

    @property
    def service_name(self) -> str:
        return "opensearch"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all OpenSearch domains."""
        opensearch = self.session.client("opensearch")
        resources = []

        try:
            # List domain names
            response = opensearch.list_domain_names()
            domain_names = [d["DomainName"] for d in response.get("DomainNames", [])]

            # Get details for each domain
            if domain_names:
                for domain_name in domain_names:
                    try:
                        response = opensearch.describe_domain(DomainName=domain_name)
                        domain = response.get("DomainStatus", {})
                        resources.append({
                            "id": domain.get("ARN", domain_name),
                            "name": domain_name,
                            "type": "domain",
                            "engine_version": domain.get("EngineVersion", ""),
                        })
                    except ClientError as e:
                        # If we can't describe, add it anyway
                        error_code = e.response.get("Error", {}).get("Code", "")
                        if error_code not in ["ResourceNotFoundException"]:
                            self.logger.warning(
                                f"Could not describe OpenSearch domain {domain_name}: {str(e)}"
                            )
                        resources.append({
                            "id": domain_name,
                            "name": domain_name,
                            "type": "domain",
                        })

        except ClientError as e:
            self.logger.error(f"Error listing OpenSearch domains: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete an OpenSearch domain."""
        opensearch = self.session.client("opensearch")
        domain_name = resource.get("name")

        try:
            opensearch.delete_domain(DomainName=domain_name)
            return True
        except ClientError as e:
            self.logger.error(
                f"Error deleting OpenSearch domain {domain_name}: {str(e)}"
            )
            return False
