"""ACM (AWS Certificate Manager) resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class ACMHandler(ResourceHandler):
    """Handler for ACM certificates."""

    @property
    def service_name(self) -> str:
        return "acm"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all ACM certificates."""
        acm = self.session.client("acm")
        resources = []

        try:
            paginator = acm.get_paginator("list_certificates")
            for page in paginator.paginate():
                for cert in page.get("CertificateSummaryList", []):
                    cert_arn = cert["CertificateArn"]
                    
                    # Get certificate details
                    try:
                        details = acm.describe_certificate(CertificateArn=cert_arn)
                        cert_info = details["Certificate"]
                        
                        resources.append({
                            "id": cert_arn,
                            "name": cert.get("DomainName", cert_arn),
                            "type": "certificate",
                            "domain": cert.get("DomainName", ""),
                            "status": cert_info.get("Status", ""),
                        })
                    except ClientError:
                        # Skip certificates we can't describe
                        pass

        except ClientError as e:
            self.logger.error(f"Error listing ACM certificates: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete an ACM certificate."""
        acm = self.session.client("acm")
        cert_arn = resource.get("id")

        try:
            acm.delete_certificate(CertificateArn=cert_arn)
            return True
        except ClientError as e:
            self.logger.error(
                f"Error deleting ACM certificate {cert_arn}: {str(e)}"
            )
            return False
