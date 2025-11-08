"""S3 resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class S3Handler(ResourceHandler):
    """Handler for S3 buckets and objects."""

    @property
    def service_name(self) -> str:
        return "s3"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all S3 buckets."""
        s3 = self.session.client("s3")
        resources = []

        try:
            response = s3.list_buckets()
            for bucket in response.get("Buckets", []):
                bucket_name = bucket["Name"]

                # Check if bucket is in the current region
                try:
                    location = s3.get_bucket_location(Bucket=bucket_name)
                    bucket_region = location.get("LocationConstraint") or "us-east-1"

                    # Normalize region (us-east-1 returns None in LocationConstraint)
                    if bucket_region == self.region or (
                        self.region == "us-east-1" and bucket_region is None
                    ):
                        resources.append({
                            "id": bucket_name,
                            "name": bucket_name,
                            "type": "bucket",
                            "creation_date": bucket.get("CreationDate"),
                        })
                except ClientError:
                    # Skip buckets we can't access
                    pass

        except ClientError as e:
            self.logger.error(f"Error listing S3 buckets: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete an S3 bucket and all its contents."""
        s3 = self.session.client("s3")
        bucket_name = resource.get("id")

        try:
            # Empty the bucket first
            self._empty_bucket(bucket_name)

            # Delete the bucket
            s3.delete_bucket(Bucket=bucket_name)
            return True

        except ClientError as e:
            self.logger.error(f"Error deleting S3 bucket {bucket_name}: {str(e)}")
            return False

    def _empty_bucket(self, bucket_name: str):
        """
        Empty all objects and versions from a bucket.

        Args:
            bucket_name: Name of the bucket to empty
        """
        s3 = self.session.resource("s3")
        bucket = s3.Bucket(bucket_name)

        try:
            # Check if versioning is enabled
            versioning = s3.BucketVersioning(bucket_name)

            if versioning.status == "Enabled":
                # Delete all object versions
                bucket.object_versions.all().delete()
            else:
                # Delete all objects
                bucket.objects.all().delete()

        except ClientError as e:
            self.logger.warning(
                f"Error emptying bucket {bucket_name}: {str(e)}"
            )
