"""CodeArtifact resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class CodeArtifactHandler(ResourceHandler):
    """Handler for AWS CodeArtifact resources."""

    @property
    def service_name(self) -> str:
        return "codeartifact"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all CodeArtifact resources."""
        codeartifact = self.session.client("codeartifact")
        resources = []

        try:
            # List domains
            paginator = codeartifact.get_paginator("list_domains")
            for page in paginator.paginate():
                for domain in page.get("domains", []):
                    domain_name = domain["name"]
                    resources.append({
                        "id": domain["arn"],
                        "name": domain_name,
                        "type": "domain",
                        "owner": domain["owner"],
                    })

                    # List repositories in this domain
                    try:
                        repo_paginator = codeartifact.get_paginator("list_repositories_in_domain")
                        for repo_page in repo_paginator.paginate(domain=domain_name, domainOwner=domain["owner"]):
                            for repo in repo_page.get("repositories", []):
                                resources.append({
                                    "id": repo["arn"],
                                    "name": repo["name"],
                                    "type": "repository",
                                    "domain": domain_name,
                                    "domain_owner": domain["owner"],
                                })
                    except ClientError as e:
                        self.logger.error(f"Error listing repositories in domain {domain_name}: {str(e)}")

        except ClientError as e:
            self.logger.error(f"Error listing CodeArtifact domains: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a CodeArtifact resource."""
        codeartifact = self.session.client("codeartifact")
        resource_type = resource.get("type")

        try:
            if resource_type == "repository":
                codeartifact.delete_repository(
                    domain=resource.get("domain"),
                    domainOwner=resource.get("domain_owner"),
                    repository=resource.get("name")
                )
                return True

            elif resource_type == "domain":
                codeartifact.delete_domain(
                    domain=resource.get("name"),
                    domainOwner=resource.get("owner")
                )
                return True

            return False

        except ClientError as e:
            self.logger.error(
                f"Error deleting CodeArtifact {resource_type} {resource.get('name')}: {str(e)}"
            )
            return False
