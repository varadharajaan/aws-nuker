"""AWS Batch resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class BatchHandler(ResourceHandler):
    """Handler for AWS Batch resources."""

    @property
    def service_name(self) -> str:
        return "batch"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all AWS Batch resources."""
        batch = self.session.client("batch")
        resources = []

        try:
            # List job queues
            paginator = batch.get_paginator("describe_job_queues")
            for page in paginator.paginate():
                for queue in page.get("jobQueues", []):
                    resources.append({
                        "id": queue["jobQueueArn"],
                        "name": queue["jobQueueName"],
                        "type": "job_queue",
                        "state": queue.get("state", ""),
                    })

        except ClientError as e:
            self.logger.error(f"Error listing Batch job queues: {str(e)}")

        try:
            # List job definitions
            paginator = batch.get_paginator("describe_job_definitions")
            for page in paginator.paginate(status="ACTIVE"):
                for job_def in page.get("jobDefinitions", []):
                    resources.append({
                        "id": job_def["jobDefinitionArn"],
                        "name": job_def["jobDefinitionName"],
                        "type": "job_definition",
                        "revision": job_def.get("revision", 0),
                    })

        except ClientError as e:
            self.logger.error(f"Error listing Batch job definitions: {str(e)}")

        try:
            # List compute environments
            paginator = batch.get_paginator("describe_compute_environments")
            for page in paginator.paginate():
                for env in page.get("computeEnvironments", []):
                    resources.append({
                        "id": env["computeEnvironmentArn"],
                        "name": env["computeEnvironmentName"],
                        "type": "compute_environment",
                        "state": env.get("state", ""),
                    })

        except ClientError as e:
            self.logger.error(f"Error listing Batch compute environments: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete an AWS Batch resource."""
        batch = self.session.client("batch")
        resource_type = resource.get("type")
        resource_name = resource.get("name")

        try:
            if resource_type == "job_queue":
                # Disable and then delete
                batch.update_job_queue(jobQueue=resource_name, state="DISABLED")
                batch.delete_job_queue(jobQueue=resource_name)
                return True

            elif resource_type == "job_definition":
                batch.deregister_job_definition(jobDefinition=resource_name)
                return True

            elif resource_type == "compute_environment":
                # Disable and then delete
                batch.update_compute_environment(
                    computeEnvironment=resource_name,
                    state="DISABLED"
                )
                batch.delete_compute_environment(computeEnvironment=resource_name)
                return True

            return False

        except ClientError as e:
            self.logger.error(
                f"Error deleting Batch {resource_type} {resource_name}: {str(e)}"
            )
            return False
