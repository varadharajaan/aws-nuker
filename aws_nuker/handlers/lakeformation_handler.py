"""Lake Formation resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class LakeFormationHandler(ResourceHandler):
    """Handler for AWS Lake Formation resources."""

    @property
    def service_name(self) -> str:
        return "lakeformation"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all Lake Formation resources."""
        lakeformation = self.session.client("lakeformation")
        resources = []

        try:
            # List data lake settings (one per account/region)
            response = lakeformation.get_data_lake_settings()
            if response.get("DataLakeSettings"):
                resources.append({
                    "id": "data-lake-settings",
                    "name": "Data Lake Settings",
                    "type": "settings",
                })

        except ClientError as e:
            self.logger.error(f"Error listing Lake Formation settings: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a Lake Formation resource."""
        # Lake Formation settings cannot be deleted, only reset
        # This is a minimal handler
        return False
