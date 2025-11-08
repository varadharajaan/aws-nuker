"""EC2 resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class EC2Handler(ResourceHandler):
    """Handler for EC2 resources including instances, volumes, snapshots, AMIs, etc."""

    @property
    def service_name(self) -> str:
        return "ec2"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all EC2 instances."""
        ec2 = self.session.client("ec2")
        resources = []

        try:
            # List instances
            response = ec2.describe_instances()
            for reservation in response.get("Reservations", []):
                for instance in reservation.get("Instances", []):
                    if instance["State"]["Name"] not in ["terminated"]:
                        resources.append({
                            "id": instance["InstanceId"],
                            "name": self._get_tag_name(instance.get("Tags", [])),
                            "type": "instance",
                            "state": instance["State"]["Name"],
                        })

            # List volumes
            volumes_response = ec2.describe_volumes()
            for volume in volumes_response.get("Volumes", []):
                # Skip volumes attached to instances (they'll be deleted with instance)
                if not volume.get("Attachments"):
                    resources.append({
                        "id": volume["VolumeId"],
                        "name": self._get_tag_name(volume.get("Tags", [])),
                        "type": "volume",
                        "state": volume["State"],
                    })

            # List snapshots owned by the account
            snapshots_response = ec2.describe_snapshots(OwnerIds=["self"])
            for snapshot in snapshots_response.get("Snapshots", []):
                resources.append({
                    "id": snapshot["SnapshotId"],
                    "name": self._get_tag_name(snapshot.get("Tags", [])),
                    "type": "snapshot",
                    "state": snapshot["State"],
                })

            # List AMIs owned by the account
            images_response = ec2.describe_images(Owners=["self"])
            for image in images_response.get("Images", []):
                resources.append({
                    "id": image["ImageId"],
                    "name": image.get("Name", ""),
                    "type": "ami",
                })

            # List security groups (excluding default)
            sgs_response = ec2.describe_security_groups()
            for sg in sgs_response.get("SecurityGroups", []):
                if sg["GroupName"] != "default":
                    resources.append({
                        "id": sg["GroupId"],
                        "name": sg["GroupName"],
                        "type": "security_group",
                    })

            # List key pairs
            keypairs_response = ec2.describe_key_pairs()
            for kp in keypairs_response.get("KeyPairs", []):
                resources.append({
                    "id": kp["KeyPairId"],
                    "name": kp["KeyName"],
                    "type": "key_pair",
                })

            # List elastic IPs
            eips_response = ec2.describe_addresses()
            for eip in eips_response.get("Addresses", []):
                resources.append({
                    "id": eip.get("AllocationId", eip.get("PublicIp")),
                    "name": eip.get("PublicIp", ""),
                    "type": "elastic_ip",
                })

        except ClientError as e:
            self.logger.error(f"Error listing EC2 resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete an EC2 resource."""
        ec2 = self.session.client("ec2")
        resource_type = resource.get("type")
        resource_id = resource.get("id")

        try:
            if resource_type == "instance":
                # Terminate instance
                ec2.terminate_instances(InstanceIds=[resource_id])
                return True

            elif resource_type == "volume":
                # Delete volume
                ec2.delete_volume(VolumeId=resource_id)
                return True

            elif resource_type == "snapshot":
                # Delete snapshot
                ec2.delete_snapshot(SnapshotId=resource_id)
                return True

            elif resource_type == "ami":
                # Deregister AMI
                ec2.deregister_image(ImageId=resource_id)
                return True

            elif resource_type == "security_group":
                # Delete security group
                ec2.delete_security_group(GroupId=resource_id)
                return True

            elif resource_type == "key_pair":
                # Delete key pair
                ec2.delete_key_pair(KeyPairId=resource_id)
                return True

            elif resource_type == "elastic_ip":
                # Release elastic IP
                if resource_id.startswith("eipalloc-"):
                    ec2.release_address(AllocationId=resource_id)
                else:
                    ec2.release_address(PublicIp=resource_id)
                return True

            return False

        except ClientError as e:
            self.logger.error(
                f"Error deleting EC2 {resource_type} {resource_id}: {str(e)}"
            )
            return False

    def is_default_resource(self, resource: Dict[str, Any]) -> bool:
        """Check if resource is a default resource."""
        # Default security groups should be preserved
        if (resource.get("type") == "security_group" and
                resource.get("name") == "default"):
            return True
        return False

    @staticmethod
    def _get_tag_name(tags: List[Dict[str, str]]) -> str:
        """Extract name from tags."""
        for tag in tags:
            if tag.get("Key") == "Name":
                return tag.get("Value", "")
        return ""
