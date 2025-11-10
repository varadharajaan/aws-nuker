"""Handler for ACM resources."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class AcmHandler(ResourceHandler):
    """Handler for ACM resources."""

    @property
    def service_name(self) -> str:
        return "acm"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all ACM resources."""
        client = self.session.client("acm")
        resources = []

        try:
            paginator = client.get_paginator("list_certificates")
            for page in paginator.paginate():
                for item in page.get("CertificateSummaryList", []):
                    resources.append({
                        "id": item.get("CertificateArn", ""),
                        "name": item.get("DomainName", ""),
                        "type": "certificate",
                    })
        except ClientError as e:
            self.logger.error(f"Error listing ACM resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a ACM resource."""
        client = self.session.client("acm")
        resource_id = resource.get("id")

        try:
            client.delete_certificate(CertificateArn=resource_id)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting ACM resource {resource_id}: {str(e)}")
            return False
