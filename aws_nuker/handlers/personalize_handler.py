"""Personalize resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class PersonalizeHandler(ResourceHandler):
    """Handler for Amazon Personalize resources."""

    @property
    def service_name(self) -> str:
        return "personalize"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all Personalize resources."""
        personalize = self.session.client("personalize")
        resources = []

        try:
            # List datasets
            paginator = personalize.get_paginator("list_datasets")
            for page in paginator.paginate():
                for dataset in page.get("datasets", []):
                    resources.append({
                        "id": dataset["datasetArn"],
                        "name": dataset.get("name", dataset["datasetArn"]),
                        "type": "dataset",
                    })

        except ClientError as e:
            self.logger.error(f"Error listing Personalize datasets: {str(e)}")

        try:
            # List dataset groups
            paginator = personalize.get_paginator("list_dataset_groups")
            for page in paginator.paginate():
                for group in page.get("datasetGroups", []):
                    resources.append({
                        "id": group["datasetGroupArn"],
                        "name": group.get("name", group["datasetGroupArn"]),
                        "type": "dataset_group",
                    })

        except ClientError as e:
            self.logger.error(f"Error listing Personalize dataset groups: {str(e)}")

        try:
            # List solutions
            paginator = personalize.get_paginator("list_solutions")
            for page in paginator.paginate():
                for solution in page.get("solutions", []):
                    resources.append({
                        "id": solution["solutionArn"],
                        "name": solution.get("name", solution["solutionArn"]),
                        "type": "solution",
                    })

        except ClientError as e:
            self.logger.error(f"Error listing Personalize solutions: {str(e)}")

        try:
            # List campaigns
            paginator = personalize.get_paginator("list_campaigns")
            for page in paginator.paginate():
                for campaign in page.get("campaigns", []):
                    resources.append({
                        "id": campaign["campaignArn"],
                        "name": campaign.get("name", campaign["campaignArn"]),
                        "type": "campaign",
                    })

        except ClientError as e:
            self.logger.error(f"Error listing Personalize campaigns: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a Personalize resource."""
        personalize = self.session.client("personalize")
        resource_type = resource.get("type")
        resource_arn = resource.get("id")

        try:
            if resource_type == "campaign":
                personalize.delete_campaign(campaignArn=resource_arn)
                return True

            elif resource_type == "solution":
                personalize.delete_solution(solutionArn=resource_arn)
                return True

            elif resource_type == "dataset":
                personalize.delete_dataset(datasetArn=resource_arn)
                return True

            elif resource_type == "dataset_group":
                personalize.delete_dataset_group(datasetGroupArn=resource_arn)
                return True

            return False

        except ClientError as e:
            self.logger.error(
                f"Error deleting Personalize {resource_type} {resource_arn}: {str(e)}"
            )
            return False
