"""Detective resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class DetectiveHandler(ResourceHandler):
    """Handler for Amazon Detective resources."""

    @property
    def service_name(self) -> str:
        return "detective"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all Detective graphs."""
        detective = self.session.client("detective")
        resources = []

        try:
            # List graphs
            paginator = detective.get_paginator("list_graphs")
            for page in paginator.paginate():
                for graph in page.get("GraphList", []):
                    resources.append({
                        "id": graph["Arn"],
                        "name": graph["Arn"].split("/")[-1],
                        "type": "graph",
                    })

        except ClientError as e:
            self.logger.error(f"Error listing Detective graphs: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a Detective graph."""
        detective = self.session.client("detective")
        graph_arn = resource.get("id")

        try:
            detective.delete_graph(GraphArn=graph_arn)
            return True
        except ClientError as e:
            self.logger.error(
                f"Error deleting Detective graph {graph_arn}: {str(e)}"
            )
            return False
