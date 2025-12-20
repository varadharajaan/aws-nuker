"""QuickSight resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class QuickSightHandler(ResourceHandler):
    """Handler for QuickSight resources."""

    @property
    def service_name(self) -> str:
        return "quicksight"

    def _get_account_id(self) -> str:
        """Get AWS account ID."""
        sts = self.session.client("sts")
        try:
            return sts.get_caller_identity()["Account"]
        except ClientError:
            self.logger.error("Could not get AWS account ID")
            return ""

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all QuickSight resources."""
        quicksight = self.session.client("quicksight")
        resources = []

        account_id = self._get_account_id()
        if not account_id:
            return resources

        try:
            # List data sets
            response = quicksight.list_data_sets(AwsAccountId=account_id)
            for dataset in response.get("DataSetSummaries", []):
                resources.append({
                    "id": dataset["DataSetId"],
                    "name": dataset.get("Name", dataset["DataSetId"]),
                    "type": "data_set",
                })

        except ClientError as e:
            self.logger.error(f"Error listing QuickSight data sets: {str(e)}")

        try:
            # List dashboards
            response = quicksight.list_dashboards(AwsAccountId=account_id)
            for dashboard in response.get("DashboardSummaryList", []):
                resources.append({
                    "id": dashboard["DashboardId"],
                    "name": dashboard.get("Name", dashboard["DashboardId"]),
                    "type": "dashboard",
                })

        except ClientError as e:
            self.logger.error(f"Error listing QuickSight dashboards: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a QuickSight resource."""
        quicksight = self.session.client("quicksight")
        resource_type = resource.get("type")
        resource_id = resource.get("id")

        account_id = self._get_account_id()
        if not account_id:
            return False

        try:
            if resource_type == "data_set":
                quicksight.delete_data_set(
                    AwsAccountId=account_id,
                    DataSetId=resource_id
                )
                return True

            elif resource_type == "dashboard":
                quicksight.delete_dashboard(
                    AwsAccountId=account_id,
                    DashboardId=resource_id
                )
                return True

            return False

        except ClientError as e:
            self.logger.error(
                f"Error deleting QuickSight {resource_type} {resource_id}: {str(e)}"
            )
            return False
