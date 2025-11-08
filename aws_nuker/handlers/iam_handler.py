"""IAM resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class IAMHandler(ResourceHandler):
    """Handler for IAM resources (users, roles, policies)."""

    @property
    def service_name(self) -> str:
        return "iam"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all IAM resources."""
        # IAM is global, only process in us-east-1
        if self.region != "us-east-1":
            return []

        iam = self.session.client("iam")
        resources = []

        try:
            # List users
            users_paginator = iam.get_paginator("list_users")
            for page in users_paginator.paginate():
                for user in page.get("Users", []):
                    resources.append({
                        "id": user["UserName"],
                        "name": user["UserName"],
                        "type": "user",
                        "arn": user["Arn"],
                    })

            # List roles (exclude AWS service roles)
            roles_paginator = iam.get_paginator("list_roles")
            for page in roles_paginator.paginate():
                for role in page.get("Roles", []):
                    # Skip AWS service-linked roles
                    if not role["Path"].startswith("/aws-service-role/"):
                        resources.append({
                            "id": role["RoleName"],
                            "name": role["RoleName"],
                            "type": "role",
                            "arn": role["Arn"],
                        })

            # List policies (customer managed only)
            policies_paginator = iam.get_paginator("list_policies")
            for page in policies_paginator.paginate(Scope="Local"):
                for policy in page.get("Policies", []):
                    resources.append({
                        "id": policy["PolicyName"],
                        "name": policy["PolicyName"],
                        "type": "policy",
                        "arn": policy["Arn"],
                    })

        except ClientError as e:
            self.logger.error(f"Error listing IAM resources: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete an IAM resource."""
        iam = self.session.client("iam")
        resource_type = resource.get("type")
        resource_name = resource.get("name")

        try:
            if resource_type == "user":
                # Delete user and all associated resources
                self._delete_user_resources(iam, resource_name)
                iam.delete_user(UserName=resource_name)
                return True

            elif resource_type == "role":
                # Delete role and all associated resources
                self._delete_role_resources(iam, resource_name)
                iam.delete_role(RoleName=resource_name)
                return True

            elif resource_type == "policy":
                # Delete all policy versions first
                arn = resource.get("arn")
                versions = iam.list_policy_versions(PolicyArn=arn)
                for version in versions.get("Versions", []):
                    if not version.get("IsDefaultVersion"):
                        iam.delete_policy_version(
                            PolicyArn=arn,
                            VersionId=version["VersionId"],
                        )
                # Delete the policy
                iam.delete_policy(PolicyArn=arn)
                return True

            return False

        except ClientError as e:
            self.logger.error(
                f"Error deleting IAM {resource_type} {resource_name}: {str(e)}"
            )
            return False

    def _delete_user_resources(self, iam, user_name: str):
        """Delete all resources associated with a user."""
        try:
            # Delete access keys
            keys = iam.list_access_keys(UserName=user_name)
            for key in keys.get("AccessKeyMetadata", []):
                iam.delete_access_key(
                    UserName=user_name,
                    AccessKeyId=key["AccessKeyId"],
                )

            # Detach managed policies
            policies = iam.list_attached_user_policies(UserName=user_name)
            for policy in policies.get("AttachedPolicies", []):
                iam.detach_user_policy(
                    UserName=user_name,
                    PolicyArn=policy["PolicyArn"],
                )

            # Delete inline policies
            inline_policies = iam.list_user_policies(UserName=user_name)
            for policy_name in inline_policies.get("PolicyNames", []):
                iam.delete_user_policy(
                    UserName=user_name,
                    PolicyName=policy_name,
                )

            # Remove from groups
            groups = iam.list_groups_for_user(UserName=user_name)
            for group in groups.get("Groups", []):
                iam.remove_user_from_group(
                    UserName=user_name,
                    GroupName=group["GroupName"],
                )

        except ClientError as e:
            self.logger.warning(
                f"Error cleaning up user resources for {user_name}: {str(e)}"
            )

    def _delete_role_resources(self, iam, role_name: str):
        """Delete all resources associated with a role."""
        try:
            # Detach managed policies
            policies = iam.list_attached_role_policies(RoleName=role_name)
            for policy in policies.get("AttachedPolicies", []):
                iam.detach_role_policy(
                    RoleName=role_name,
                    PolicyArn=policy["PolicyArn"],
                )

            # Delete inline policies
            inline_policies = iam.list_role_policies(RoleName=role_name)
            for policy_name in inline_policies.get("PolicyNames", []):
                iam.delete_role_policy(
                    RoleName=role_name,
                    PolicyName=policy_name,
                )

            # Delete instance profiles
            instance_profiles = iam.list_instance_profiles_for_role(
                RoleName=role_name
            )
            for profile in instance_profiles.get("InstanceProfiles", []):
                iam.remove_role_from_instance_profile(
                    InstanceProfileName=profile["InstanceProfileName"],
                    RoleName=role_name,
                )

        except ClientError as e:
            self.logger.warning(
                f"Error cleaning up role resources for {role_name}: {str(e)}"
            )
