"""Glue resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class GlueHandler(ResourceHandler):
    """Handler for AWS Glue databases, crawlers, and jobs."""

    @property
    def service_name(self) -> str:
        return "glue"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all Glue resources."""
        glue = self.session.client("glue")
        resources = []

        try:
            # List databases
            databases = glue.get_databases()
            for db in databases.get("DatabaseList", []):
                resources.append({
                    "id": db["Name"],
                    "name": db["Name"],
                    "type": "database",
                })

            # List crawlers
            crawlers_paginator = glue.get_paginator("get_crawlers")
            for page in crawlers_paginator.paginate():
                for crawler in page.get("Crawlers", []):
                    resources.append({
                        "id": crawler["Name"],
                        "name": crawler["Name"],
                        "type": "crawler",
                    })

            # List jobs
            jobs = glue.get_jobs()
            for job in jobs.get("Jobs", []):
                resources.append({
                    "id": job["Name"],
                    "name": job["Name"],
                    "type": "job",
                })

        except ClientError as e:
            self.logger.error(f"Error listing Glue resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a Glue resource."""
        glue = self.session.client("glue")
        resource_type = resource.get("type")
        resource_name = resource.get("name")

        try:
            if resource_type == "database":
                glue.delete_database(Name=resource_name)
                return True
            elif resource_type == "crawler":
                glue.delete_crawler(Name=resource_name)
                return True
            elif resource_type == "job":
                glue.delete_job(JobName=resource_name)
                return True

            return False

        except ClientError as e:
            self.logger.error(
                f"Error deleting Glue {resource_type} {resource_name}: {str(e)}"
            )
            return False
