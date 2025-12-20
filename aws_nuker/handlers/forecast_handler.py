"""Forecast resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class ForecastHandler(ResourceHandler):
    """Handler for Amazon Forecast resources."""

    @property
    def service_name(self) -> str:
        return "forecast"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all Forecast resources."""
        forecast = self.session.client("forecast")
        resources = []

        try:
            # List datasets
            paginator = forecast.get_paginator("list_datasets")
            for page in paginator.paginate():
                for dataset in page.get("Datasets", []):
                    resources.append({
                        "id": dataset["DatasetArn"],
                        "name": dataset.get("DatasetName", dataset["DatasetArn"]),
                        "type": "dataset",
                    })

        except ClientError as e:
            self.logger.error(f"Error listing Forecast datasets: {str(e)}")

        try:
            # List dataset groups
            paginator = forecast.get_paginator("list_dataset_groups")
            for page in paginator.paginate():
                for group in page.get("DatasetGroups", []):
                    resources.append({
                        "id": group["DatasetGroupArn"],
                        "name": group.get("DatasetGroupName", group["DatasetGroupArn"]),
                        "type": "dataset_group",
                    })

        except ClientError as e:
            self.logger.error(f"Error listing Forecast dataset groups: {str(e)}")

        try:
            # List predictors
            paginator = forecast.get_paginator("list_predictors")
            for page in paginator.paginate():
                for predictor in page.get("Predictors", []):
                    resources.append({
                        "id": predictor["PredictorArn"],
                        "name": predictor.get("PredictorName", predictor["PredictorArn"]),
                        "type": "predictor",
                    })

        except ClientError as e:
            self.logger.error(f"Error listing Forecast predictors: {str(e)}")

        try:
            # List forecasts
            paginator = forecast.get_paginator("list_forecasts")
            for page in paginator.paginate():
                for forecast_item in page.get("Forecasts", []):
                    resources.append({
                        "id": forecast_item["ForecastArn"],
                        "name": forecast_item.get("ForecastName", forecast_item["ForecastArn"]),
                        "type": "forecast",
                    })

        except ClientError as e:
            self.logger.error(f"Error listing Forecasts: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a Forecast resource."""
        forecast = self.session.client("forecast")
        resource_type = resource.get("type")
        resource_arn = resource.get("id")

        try:
            if resource_type == "forecast":
                forecast.delete_forecast(ForecastArn=resource_arn)
                return True

            elif resource_type == "predictor":
                forecast.delete_predictor(PredictorArn=resource_arn)
                return True

            elif resource_type == "dataset":
                forecast.delete_dataset(DatasetArn=resource_arn)
                return True

            elif resource_type == "dataset_group":
                forecast.delete_dataset_group(DatasetGroupArn=resource_arn)
                return True

            return False

        except ClientError as e:
            self.logger.error(
                f"Error deleting Forecast {resource_type} {resource_arn}: {str(e)}"
            )
            return False
