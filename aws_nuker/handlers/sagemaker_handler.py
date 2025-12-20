"""SageMaker resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class SageMakerHandler(ResourceHandler):
    """Handler for SageMaker resources."""

    @property
    def service_name(self) -> str:
        return "sagemaker"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all SageMaker resources."""
        sagemaker = self.session.client("sagemaker")
        resources = []

        try:
            # List notebook instances
            paginator = sagemaker.get_paginator("list_notebook_instances")
            for page in paginator.paginate():
                for notebook in page.get("NotebookInstances", []):
                    resources.append({
                        "id": notebook["NotebookInstanceArn"],
                        "name": notebook["NotebookInstanceName"],
                        "type": "notebook_instance",
                        "status": notebook.get("NotebookInstanceStatus", ""),
                    })

        except ClientError as e:
            self.logger.error(f"Error listing SageMaker notebook instances: {str(e)}")

        try:
            # List endpoints
            paginator = sagemaker.get_paginator("list_endpoints")
            for page in paginator.paginate():
                for endpoint in page.get("Endpoints", []):
                    resources.append({
                        "id": endpoint["EndpointArn"],
                        "name": endpoint["EndpointName"],
                        "type": "endpoint",
                        "status": endpoint.get("EndpointStatus", ""),
                    })

        except ClientError as e:
            self.logger.error(f"Error listing SageMaker endpoints: {str(e)}")

        try:
            # List models
            paginator = sagemaker.get_paginator("list_models")
            for page in paginator.paginate():
                for model in page.get("Models", []):
                    resources.append({
                        "id": model["ModelArn"],
                        "name": model["ModelName"],
                        "type": "model",
                    })

        except ClientError as e:
            self.logger.error(f"Error listing SageMaker models: {str(e)}")

        try:
            # List training jobs (only those in InProgress state)
            paginator = sagemaker.get_paginator("list_training_jobs")
            for page in paginator.paginate(StatusEquals="InProgress"):
                for job in page.get("TrainingJobSummaries", []):
                    resources.append({
                        "id": job["TrainingJobArn"],
                        "name": job["TrainingJobName"],
                        "type": "training_job",
                        "status": job.get("TrainingJobStatus", ""),
                    })

        except ClientError as e:
            self.logger.error(f"Error listing SageMaker training jobs: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a SageMaker resource."""
        sagemaker = self.session.client("sagemaker")
        resource_type = resource.get("type")
        resource_name = resource.get("name")

        try:
            if resource_type == "notebook_instance":
                # Stop notebook first if it's running
                try:
                    sagemaker.stop_notebook_instance(NotebookInstanceName=resource_name)
                except ClientError as e:
                    # Notebook might already be stopped or in invalid state
                    error_code = e.response.get("Error", {}).get("Code", "")
                    if error_code not in ["ValidationException", "ResourceNotFoundException"]:
                        self.logger.warning(
                            f"Error stopping notebook instance {resource_name}: {str(e)}"
                        )
                sagemaker.delete_notebook_instance(NotebookInstanceName=resource_name)
                return True

            elif resource_type == "endpoint":
                sagemaker.delete_endpoint(EndpointName=resource_name)
                return True

            elif resource_type == "model":
                sagemaker.delete_model(ModelName=resource_name)
                return True

            elif resource_type == "training_job":
                sagemaker.stop_training_job(TrainingJobName=resource_name)
                return True

            return False

        except ClientError as e:
            self.logger.error(
                f"Error deleting SageMaker {resource_type} {resource_name}: {str(e)}"
            )
            return False
