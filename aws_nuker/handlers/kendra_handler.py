"""Kendra resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class KendraHandler(ResourceHandler):
    """Handler for Amazon Kendra resources."""

    @property
    def service_name(self) -> str:
        return "kendra"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all Kendra resources."""
        kendra = self.session.client("kendra")
        resources = []

        try:
            # List indexes
            paginator = kendra.get_paginator("list_indices")
            for page in paginator.paginate():
                for index in page.get("IndexConfigurationSummaryItems", []):
                    resources.append({
                        "id": index["Id"],
                        "name": index.get("Name", index["Id"]),
                        "type": "index",
                        "status": index.get("Status", ""),
                    })

        except ClientError as e:
            self.logger.error(f"Error listing Kendra indexes: {str(e)}")

        try:
            # List data sources for each index
            for resource in list(resources):
                if resource["type"] == "index":
                    try:
                        ds_paginator = kendra.get_paginator("list_data_sources")
                        for page in ds_paginator.paginate(IndexId=resource["id"]):
                            for ds in page.get("SummaryItems", []):
                                resources.append({
                                    "id": ds["Id"],
                                    "name": ds.get("Name", ds["Id"]),
                                    "type": "data_source",
                                    "index_id": resource["id"],
                                })
                    except ClientError:
                        pass

        except ClientError as e:
            self.logger.error(f"Error listing Kendra data sources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a Kendra resource."""
        kendra = self.session.client("kendra")
        resource_type = resource.get("type")
        resource_id = resource.get("id")

        try:
            if resource_type == "data_source":
                index_id = resource.get("index_id")
                kendra.delete_data_source(
                    Id=resource_id,
                    IndexId=index_id
                )
                return True

            elif resource_type == "index":
                kendra.delete_index(Id=resource_id)
                return True

            return False

        except ClientError as e:
            self.logger.error(
                f"Error deleting Kendra {resource_type} {resource_id}: {str(e)}"
            )
            return False
