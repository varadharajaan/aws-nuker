"""VPC resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class VPCHandler(ResourceHandler):
    """Handler for VPC resources (excluding default VPCs)."""

    @property
    def service_name(self) -> str:
        return "vpc"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all VPC resources."""
        ec2 = self.session.client("ec2")
        resources = []

        try:
            # List VPCs (excluding default)
            vpcs_response = ec2.describe_vpcs()
            for vpc in vpcs_response.get("Vpcs", []):
                if not vpc.get("IsDefault"):
                    resources.append({
                        "id": vpc["VpcId"],
                        "name": self._get_tag_name(vpc.get("Tags", [])),
                        "type": "vpc",
                        "is_default": vpc.get("IsDefault", False),
                    })

            # List subnets (excluding default VPC subnets)
            subnets_response = ec2.describe_subnets()
            for subnet in subnets_response.get("Subnets", []):
                # Check if subnet belongs to default VPC
                vpc_id = subnet["VpcId"]
                vpc_info = ec2.describe_vpcs(VpcIds=[vpc_id])
                if not vpc_info["Vpcs"][0].get("IsDefault"):
                    resources.append({
                        "id": subnet["SubnetId"],
                        "name": self._get_tag_name(subnet.get("Tags", [])),
                        "type": "subnet",
                        "vpc_id": vpc_id,
                    })

            # List internet gateways (excluding default VPC IGWs)
            igws_response = ec2.describe_internet_gateways()
            for igw in igws_response.get("InternetGateways", []):
                # Check if attached to non-default VPC
                for attachment in igw.get("Attachments", []):
                    vpc_id = attachment["VpcId"]
                    vpc_info = ec2.describe_vpcs(VpcIds=[vpc_id])
                    if not vpc_info["Vpcs"][0].get("IsDefault"):
                        resources.append({
                            "id": igw["InternetGatewayId"],
                            "name": self._get_tag_name(igw.get("Tags", [])),
                            "type": "internet_gateway",
                            "vpc_id": vpc_id,
                        })

            # List NAT gateways
            nat_gws_response = ec2.describe_nat_gateways(
                Filters=[{"Name": "state", "Values": ["available", "pending"]}]
            )
            for nat_gw in nat_gws_response.get("NatGateways", []):
                resources.append({
                    "id": nat_gw["NatGatewayId"],
                    "name": self._get_tag_name(nat_gw.get("Tags", [])),
                    "type": "nat_gateway",
                    "vpc_id": nat_gw["VpcId"],
                })

        except ClientError as e:
            self.logger.error(f"Error listing VPC resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete a VPC resource."""
        ec2 = self.session.client("ec2")
        resource_type = resource.get("type")
        resource_id = resource.get("id")

        try:
            if resource_type == "nat_gateway":
                ec2.delete_nat_gateway(NatGatewayId=resource_id)
                return True

            elif resource_type == "internet_gateway":
                # Detach from VPC first
                vpc_id = resource.get("vpc_id")
                if vpc_id:
                    ec2.detach_internet_gateway(
                        InternetGatewayId=resource_id,
                        VpcId=vpc_id,
                    )
                ec2.delete_internet_gateway(InternetGatewayId=resource_id)
                return True

            elif resource_type == "subnet":
                ec2.delete_subnet(SubnetId=resource_id)
                return True

            elif resource_type == "vpc":
                ec2.delete_vpc(VpcId=resource_id)
                return True

            return False

        except ClientError as e:
            self.logger.error(
                f"Error deleting VPC {resource_type} {resource_id}: {str(e)}"
            )
            return False

    def is_default_resource(self, resource: Dict[str, Any]) -> bool:
        """Check if resource is a default VPC resource."""
        return resource.get("is_default", False)

    @staticmethod
    def _get_tag_name(tags: List[Dict[str, str]]) -> str:
        """Extract name from tags."""
        for tag in tags:
            if tag.get("Key") == "Name":
                return tag.get("Value", "")
        return ""
