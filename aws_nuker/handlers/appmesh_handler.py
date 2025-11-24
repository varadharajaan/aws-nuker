"""App Mesh resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class AppMeshHandler(ResourceHandler):
    """Handler for App Mesh resources."""

    @property
    def service_name(self) -> str:
        return "appmesh"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all App Mesh resources."""
        appmesh = self.session.client("appmesh")
        resources = []

        try:
            # List meshes
            paginator = appmesh.get_paginator("list_meshes")
            for page in paginator.paginate():
                for mesh in page.get("meshes", []):
                    mesh_name = mesh["meshName"]
                    resources.append({
                        "id": mesh["arn"],
                        "name": mesh_name,
                        "type": "mesh",
                    })

                    # List virtual nodes in this mesh
                    try:
                        vn_paginator = appmesh.get_paginator("list_virtual_nodes")
                        for vn_page in vn_paginator.paginate(meshName=mesh_name):
                            for vnode in vn_page.get("virtualNodes", []):
                                resources.append({
                                    "id": vnode["arn"],
                                    "name": vnode["virtualNodeName"],
                                    "type": "virtual_node",
                                    "mesh_name": mesh_name,
                                })
                    except ClientError:
                        pass

        except ClientError as e:
            self.logger.error(f"Error listing App Mesh resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete an App Mesh resource."""
        appmesh = self.session.client("appmesh")
        resource_type = resource.get("type")
        resource_name = resource.get("name")

        try:
            if resource_type == "virtual_node":
                mesh_name = resource.get("mesh_name")
                appmesh.delete_virtual_node(
                    meshName=mesh_name,
                    virtualNodeName=resource_name
                )
                return True

            elif resource_type == "mesh":
                appmesh.delete_mesh(meshName=resource_name)
                return True

            return False

        except ClientError as e:
            self.logger.error(
                f"Error deleting App Mesh {resource_type} {resource_name}: {str(e)}"
            )
            return False
