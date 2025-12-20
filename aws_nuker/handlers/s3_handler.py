"""S3 resource handler.

Enhanced handler for Amazon S3 resources including:
- S3 buckets (with intelligent emptying)
- S3 Access Points
- Multi-Region Access Points
- Storage Lens configurations
- Object Lambda Access Points
"""

from typing import List, Dict, Any, Optional
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class S3Handler(ResourceHandler):
    """
    Handler for Amazon S3 resources.

    Manages the lifecycle of:
    - S3 buckets with all objects and versions
    - S3 Access Points (single-region)
    - S3 Multi-Region Access Points
    - Storage Lens configurations
    - Object Lambda Access Points
    """

    @property
    def service_name(self) -> str:
        return "s3"

    def list_resources(self) -> List[Dict[str, Any]]:
        """
        List all S3 resources.

        Enumerates:
        - Buckets in the current region
        - Access Points
        - Multi-Region Access Points
        - Storage Lens configurations
        - Object Lambda Access Points
        """
        resources = []

        try:
            # List S3 buckets
            resources.extend(self._list_buckets())

            # List S3 Access Points
            resources.extend(self._list_access_points())

            # List Multi-Region Access Points
            resources.extend(self._list_multi_region_access_points())

            # List Storage Lens configurations
            resources.extend(self._list_storage_lens_configs())

            # List Object Lambda Access Points
            resources.extend(self._list_object_lambda_access_points())

        except ClientError as e:
            self.logger.error(f"Error listing S3 resources: {str(e)}")

        return resources

    def _list_buckets(self) -> List[Dict[str, Any]]:
        """List all S3 buckets in the current region."""
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
                        # Get additional bucket metadata
                        bucket_info = self._get_bucket_info(s3, bucket_name)
                        resources.append({
                            "id": bucket_name,
                            "name": bucket_name,
                            "type": "bucket",
                            "creation_date": bucket.get("CreationDate"),
                            **bucket_info,
                        })
                except ClientError:
                    # Skip buckets we can't access
                    pass

        except ClientError as e:
            self.logger.warning(f"Error listing S3 buckets: {str(e)}")

        return resources

    def _get_bucket_info(self, client, bucket_name: str) -> Dict[str, Any]:
        """Get additional information about a bucket."""
        info = {}

        try:
            # Check versioning status
            versioning = client.get_bucket_versioning(Bucket=bucket_name)
            info["versioning"] = versioning.get("Status", "Disabled")
        except ClientError:
            pass

        try:
            # Check encryption
            encryption = client.get_bucket_encryption(Bucket=bucket_name)
            rules = encryption.get("ServerSideEncryptionConfiguration", {}).get(
                "Rules", []
            )
            if rules:
                info["encryption"] = rules[0].get(
                    "ApplyServerSideEncryptionByDefault", {}
                ).get("SSEAlgorithm")
        except ClientError:
            # Encryption might not be configured
            pass

        return info

    def _list_access_points(self) -> List[Dict[str, Any]]:
        """
        List all S3 Access Points.

        Access Points simplify managing data access at scale for shared
        datasets in S3.
        """
        s3control = self.session.client("s3control")
        resources = []

        try:
            # Get account ID
            sts = self.session.client("sts")
            account_id = sts.get_caller_identity()["Account"]

            # List access points
            paginator = s3control.get_paginator("list_access_points")
            for page in paginator.paginate(AccountId=account_id):
                for ap in page.get("AccessPointList", []):
                    resources.append({
                        "id": ap["Name"],
                        "name": ap["Name"],
                        "type": "access_point",
                        "bucket": ap.get("Bucket"),
                        "access_point_arn": ap.get("AccessPointArn"),
                        "network_origin": ap.get("NetworkOrigin"),
                        "vpc_id": ap.get("VpcConfiguration", {}).get("VpcId"),
                    })

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "")
            if error_code not in ["AccessDenied", "NoSuchAccessPoint"]:
                self.logger.debug(f"Error listing S3 access points: {str(e)}")

        return resources

    def _list_multi_region_access_points(self) -> List[Dict[str, Any]]:
        """
        List all S3 Multi-Region Access Points.

        Multi-Region Access Points provide a global endpoint that spans S3 buckets
        in multiple regions.
        """
        s3control = self.session.client("s3control", region_name="us-west-2")
        resources = []

        try:
            # Get account ID
            sts = self.session.client("sts")
            account_id = sts.get_caller_identity()["Account"]

            # List multi-region access points
            paginator = s3control.get_paginator("list_multi_region_access_points")
            for page in paginator.paginate(AccountId=account_id):
                for mrap in page.get("AccessPoints", []):
                    regions = [
                        r.get("Bucket", "").split("/")[-1] if "/" in r.get("Bucket", "") 
                        else r.get("Bucket", "")
                        for r in mrap.get("Regions", [])
                    ]
                    resources.append({
                        "id": mrap["Name"],
                        "name": mrap["Name"],
                        "type": "multi_region_access_point",
                        "alias": mrap.get("Alias"),
                        "status": mrap.get("Status"),
                        "regions": regions,
                    })

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "")
            if error_code not in ["AccessDenied", "NoSuchMultiRegionAccessPoint"]:
                self.logger.debug(
                    f"Error listing multi-region access points: {str(e)}"
                )

        return resources

    def _list_storage_lens_configs(self) -> List[Dict[str, Any]]:
        """
        List all S3 Storage Lens configurations.

        Storage Lens delivers organization-wide visibility into object storage
        usage, activity trends, and recommendations.
        """
        s3control = self.session.client("s3control")
        resources = []

        try:
            # Get account ID
            sts = self.session.client("sts")
            account_id = sts.get_caller_identity()["Account"]

            # List storage lens configurations
            response = s3control.list_storage_lens_configurations(AccountId=account_id)

            for config in response.get("StorageLensConfigurationList", []):
                # Skip the default Storage Lens dashboard
                if config.get("IsEnabled") and config.get("Id") != "default-account-dashboard":
                    resources.append({
                        "id": config["Id"],
                        "name": config["Id"],
                        "type": "storage_lens_config",
                        "storage_lens_arn": config.get("StorageLensArn"),
                        "is_enabled": config.get("IsEnabled"),
                        "home_region": config.get("HomeRegion"),
                    })

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "")
            if error_code not in ["AccessDenied"]:
                self.logger.debug(f"Error listing storage lens configs: {str(e)}")

        return resources

    def _list_object_lambda_access_points(self) -> List[Dict[str, Any]]:
        """
        List all S3 Object Lambda Access Points.

        Object Lambda Access Points use Lambda functions to automatically
        transform data retrieved from S3.
        """
        s3control = self.session.client("s3control")
        resources = []

        try:
            # Get account ID
            sts = self.session.client("sts")
            account_id = sts.get_caller_identity()["Account"]

            # List object lambda access points
            paginator = s3control.get_paginator("list_access_points_for_object_lambda")
            for page in paginator.paginate(AccountId=account_id):
                for olap in page.get("ObjectLambdaAccessPointList", []):
                    resources.append({
                        "id": olap["Name"],
                        "name": olap["Name"],
                        "type": "object_lambda_access_point",
                        "object_lambda_access_point_arn": olap.get(
                            "ObjectLambdaAccessPointArn"
                        ),
                    })

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "")
            if error_code not in ["AccessDenied"]:
                self.logger.debug(
                    f"Error listing object lambda access points: {str(e)}"
                )

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete an S3 resource."""
        resource_type = resource.get("type")
        resource_id = resource.get("id")

        try:
            if resource_type == "bucket":
                return self._delete_bucket(resource_id)

            elif resource_type == "access_point":
                return self._delete_access_point(resource_id)

            elif resource_type == "multi_region_access_point":
                return self._delete_multi_region_access_point(resource_id)

            elif resource_type == "storage_lens_config":
                return self._delete_storage_lens_config(resource_id)

            elif resource_type == "object_lambda_access_point":
                return self._delete_object_lambda_access_point(resource_id)

            return False

        except ClientError as e:
            self.logger.error(
                f"Error deleting S3 {resource_type} {resource_id}: {str(e)}"
            )
            return False

    def _delete_bucket(self, bucket_name: str) -> bool:
        """Delete an S3 bucket and all its contents."""
        s3 = self.session.client("s3")

        # Empty the bucket first
        self._empty_bucket(bucket_name)

        # Delete the bucket
        s3.delete_bucket(Bucket=bucket_name)
        return True

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

    def _delete_access_point(self, name: str) -> bool:
        """Delete an S3 Access Point."""
        s3control = self.session.client("s3control")
        sts = self.session.client("sts")
        account_id = sts.get_caller_identity()["Account"]

        s3control.delete_access_point(
            AccountId=account_id,
            Name=name,
        )
        return True

    def _delete_multi_region_access_point(self, name: str) -> bool:
        """Delete an S3 Multi-Region Access Point."""
        s3control = self.session.client("s3control", region_name="us-west-2")
        sts = self.session.client("sts")
        account_id = sts.get_caller_identity()["Account"]

        # Multi-region access point deletion is async
        s3control.delete_multi_region_access_point(
            AccountId=account_id,
            Details={"Name": name},
        )
        return True

    def _delete_storage_lens_config(self, config_id: str) -> bool:
        """Delete an S3 Storage Lens configuration."""
        s3control = self.session.client("s3control")
        sts = self.session.client("sts")
        account_id = sts.get_caller_identity()["Account"]

        s3control.delete_storage_lens_configuration(
            ConfigId=config_id,
            AccountId=account_id,
        )
        return True

    def _delete_object_lambda_access_point(self, name: str) -> bool:
        """Delete an S3 Object Lambda Access Point."""
        s3control = self.session.client("s3control")
        sts = self.session.client("sts")
        account_id = sts.get_caller_identity()["Account"]

        s3control.delete_access_point_for_object_lambda(
            AccountId=account_id,
            Name=name,
        )
        return True
