"""Image Builder resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class ImageBuilderHandler(ResourceHandler):
    """Handler for EC2 Image Builder resources."""

    @property
    def service_name(self) -> str:
        return "imagebuilder"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all Image Builder resources."""
        imagebuilder = self.session.client("imagebuilder")
        resources = []

        try:
            # List image pipelines
            paginator = imagebuilder.get_paginator("list_image_pipelines")
            for page in paginator.paginate():
                for pipeline in page.get("imagePipelineList", []):
                    resources.append({
                        "id": pipeline["arn"],
                        "name": pipeline.get("name", pipeline["arn"].split("/")[-1]),
                        "type": "image_pipeline",
                    })

        except ClientError as e:
            self.logger.error(f"Error listing Image Builder pipelines: {str(e)}")

        try:
            # List image recipes
            paginator = imagebuilder.get_paginator("list_image_recipes")
            for page in paginator.paginate():
                for recipe in page.get("imageRecipeSummaryList", []):
                    resources.append({
                        "id": recipe["arn"],
                        "name": recipe.get("name", recipe["arn"].split("/")[-1]),
                        "type": "image_recipe",
                    })

        except ClientError as e:
            self.logger.error(f"Error listing Image Builder recipes: {str(e)}")

        try:
            # List infrastructure configurations
            paginator = imagebuilder.get_paginator("list_infrastructure_configurations")
            for page in paginator.paginate():
                for config in page.get("infrastructureConfigurationSummaryList", []):
                    resources.append({
                        "id": config["arn"],
                        "name": config.get("name", config["arn"].split("/")[-1]),
                        "type": "infrastructure_configuration",
                    })

        except ClientError as e:
            self.logger.error(f"Error listing Image Builder infrastructure configs: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete an Image Builder resource."""
        imagebuilder = self.session.client("imagebuilder")
        resource_type = resource.get("type")
        resource_arn = resource.get("id")

        try:
            if resource_type == "image_pipeline":
                imagebuilder.delete_image_pipeline(imagePipelineArn=resource_arn)
                return True

            elif resource_type == "image_recipe":
                imagebuilder.delete_image_recipe(imageRecipeArn=resource_arn)
                return True

            elif resource_type == "infrastructure_configuration":
                imagebuilder.delete_infrastructure_configuration(infrastructureConfigurationArn=resource_arn)
                return True

            return False

        except ClientError as e:
            self.logger.error(
                f"Error deleting Image Builder {resource_type} {resource_arn}: {str(e)}"
            )
            return False
