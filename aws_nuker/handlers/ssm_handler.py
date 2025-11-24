"""SSM (Systems Manager) resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class SSMHandler(ResourceHandler):
    """Handler for SSM parameters and documents."""

    @property
    def service_name(self) -> str:
        return "ssm"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all SSM resources."""
        ssm = self.session.client("ssm")
        resources = []

        try:
            # List parameters
            paginator = ssm.get_paginator("describe_parameters")
            for page in paginator.paginate():
                for param in page.get("Parameters", []):
                    resources.append({
                        "id": param["Name"],
                        "name": param["Name"],
                        "type": "parameter",
                        "param_type": param.get("Type", ""),
                    })

        except ClientError as e:
            self.logger.error(f"Error listing SSM parameters: {str(e)}")

        try:
            # List custom documents (skip AWS-owned)
            paginator = ssm.get_paginator("list_documents")
            for page in paginator.paginate(
                Filters=[{"Key": "Owner", "Values": ["Self"]}]
            ):
                for doc in page.get("DocumentIdentifiers", []):
                    resources.append({
                        "id": doc["Name"],
                        "name": doc["Name"],
                        "type": "document",
                    })

        except ClientError as e:
            self.logger.error(f"Error listing SSM documents: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete an SSM resource."""
        ssm = self.session.client("ssm")
        resource_type = resource.get("type")
        resource_name = resource.get("name")

        try:
            if resource_type == "parameter":
                ssm.delete_parameter(Name=resource_name)
                return True

            elif resource_type == "document":
                ssm.delete_document(Name=resource_name)
                return True

            return False

        except ClientError as e:
            self.logger.error(
                f"Error deleting SSM {resource_type} {resource_name}: {str(e)}"
            )
            return False
