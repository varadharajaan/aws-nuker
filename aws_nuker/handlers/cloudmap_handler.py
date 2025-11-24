"""CloudMap resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class CloudMapHandler(ResourceHandler):
    """Handler for CloudMap namespaces and services."""

    @property
    def service_name(self) -> str:
        return "cloudmap"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all CloudMap resources."""
        servicediscovery = self.session.client("servicediscovery")
        resources = []

        try:
            # List namespaces
            paginator = servicediscovery.get_paginator("list_namespaces")
            for page in paginator.paginate():
                for namespace in page.get("Namespaces", []):
                    resources.append({
                        "id": namespace["Id"],
                        "name": namespace.get("Name", namespace["Id"]),
                        "type": "namespace",
                        "namespace_type": namespace.get("Type", ""),
                    })

                    # List services in this namespace
                    try:
                        svc_paginator = servicediscovery.get_paginator("list_services")
                        for svc_page in svc_paginator.paginate(
                            Filters=[{"Name": "NAMESPACE_ID", "Values": [namespace["Id"]]}]
                        ):
                            for service in svc_page.get("Services", []):
                                resources.append({
                                    "id": service["Id"],
                                    "name": service.get("Name", service["Id"]),
                                    "type": "service",
                                    "namespace_id": namespace["Id"],
                                })
                    except ClientError:
                        pass

        except ClientError as e:
            self.logger.error(f"Error listing CloudMap namespaces: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a CloudMap resource."""
        servicediscovery = self.session.client("servicediscovery")
        resource_type = resource.get("type")
        resource_id = resource.get("id")

        try:
            if resource_type == "service":
                servicediscovery.delete_service(Id=resource_id)
                return True

            elif resource_type == "namespace":
                servicediscovery.delete_namespace(Id=resource_id)
                return True

            return False

        except ClientError as e:
            self.logger.error(
                f"Error deleting CloudMap {resource_type} {resource_id}: {str(e)}"
            )
            return False
