"""Athena resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class AthenaHandler(ResourceHandler):
    """Handler for Athena workgroups and named queries."""

    @property
    def service_name(self) -> str:
        return "athena"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all Athena workgroups and named queries."""
        athena = self.session.client("athena")
        resources = []

        try:
            # List workgroups (skip primary which is default)
            workgroups = athena.list_work_groups()
            for wg in workgroups.get("WorkGroups", []):
                if wg["Name"] != "primary":
                    resources.append({
                        "id": wg["Name"],
                        "name": wg["Name"],
                        "type": "workgroup",
                    })

            # List named queries
            queries_paginator = athena.get_paginator("list_named_queries")
            for page in queries_paginator.paginate():
                for query_id in page.get("NamedQueryIds", []):
                    resources.append({
                        "id": query_id,
                        "name": query_id,
                        "type": "named_query",
                    })

        except ClientError as e:
            self.logger.error(f"Error listing Athena resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete an Athena resource."""
        athena = self.session.client("athena")
        resource_type = resource.get("type")
        resource_id = resource.get("id")

        try:
            if resource_type == "workgroup":
                athena.delete_work_group(
                    WorkGroup=resource_id,
                    RecursiveDeleteOption=True
                )
                return True
            elif resource_type == "named_query":
                athena.delete_named_query(NamedQueryId=resource_id)
                return True

            return False

        except ClientError as e:
            self.logger.error(
                f"Error deleting Athena {resource_type} {resource_id}: {str(e)}"
            )
            return False

    def is_default_resource(self, resource: Dict[str, Any]) -> bool:
        """Check if resource is a default resource."""
        # The 'primary' workgroup is default
        if resource.get("type") == "workgroup" and resource.get("name") == "primary":
            return True
        return False
