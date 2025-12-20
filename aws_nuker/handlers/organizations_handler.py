"""Organizations resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class OrganizationsHandler(ResourceHandler):
    """Handler for AWS Organizations resources."""

    @property
    def service_name(self) -> str:
        return "organizations"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all Organizations resources."""
        # Organizations is a global service
        organizations = self.session.client("organizations", region_name="us-east-1")
        resources = []

        try:
            # List organizational units
            response = organizations.list_roots()
            for root in response.get("Roots", []):
                root_id = root["Id"]
                
                # List OUs under root
                paginator = organizations.get_paginator("list_organizational_units_for_parent")
                for page in paginator.paginate(ParentId=root_id):
                    for ou in page.get("OrganizationalUnits", []):
                        resources.append({
                            "id": ou["Id"],
                            "name": ou.get("Name", ou["Id"]),
                            "type": "organizational_unit",
                        })

        except ClientError as e:
            self.logger.error(f"Error listing Organizations OUs: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete an Organizations resource."""
        organizations = self.session.client("organizations", region_name="us-east-1")
        resource_type = resource.get("type")
        resource_id = resource.get("id")

        try:
            if resource_type == "organizational_unit":
                organizations.delete_organizational_unit(OrganizationalUnitId=resource_id)
                return True

            return False

        except ClientError as e:
            self.logger.error(
                f"Error deleting Organizations {resource_type} {resource_id}: {str(e)}"
            )
            return False
