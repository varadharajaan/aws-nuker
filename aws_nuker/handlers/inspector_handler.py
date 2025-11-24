"""Inspector resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class InspectorHandler(ResourceHandler):
    """Handler for Amazon Inspector assessment templates and targets."""

    @property
    def service_name(self) -> str:
        return "inspector"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all Inspector resources."""
        inspector = self.session.client("inspector")
        resources = []

        try:
            # List assessment templates
            paginator = inspector.get_paginator("list_assessment_templates")
            for page in paginator.paginate():
                template_arns = page.get("assessmentTemplateArns", [])
                if template_arns:
                    response = inspector.describe_assessment_templates(
                        assessmentTemplateArns=template_arns
                    )
                    for template in response.get("assessmentTemplates", []):
                        resources.append({
                            "id": template["arn"],
                            "name": template["name"],
                            "type": "assessment_template",
                        })

        except ClientError as e:
            self.logger.error(f"Error listing Inspector assessment templates: {str(e)}")

        try:
            # List assessment targets
            paginator = inspector.get_paginator("list_assessment_targets")
            for page in paginator.paginate():
                target_arns = page.get("assessmentTargetArns", [])
                if target_arns:
                    response = inspector.describe_assessment_targets(
                        assessmentTargetArns=target_arns
                    )
                    for target in response.get("assessmentTargets", []):
                        resources.append({
                            "id": target["arn"],
                            "name": target["name"],
                            "type": "assessment_target",
                        })

        except ClientError as e:
            self.logger.error(f"Error listing Inspector assessment targets: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete an Inspector resource."""
        inspector = self.session.client("inspector")
        resource_type = resource.get("type")
        resource_arn = resource.get("id")

        try:
            if resource_type == "assessment_template":
                inspector.delete_assessment_template(assessmentTemplateArn=resource_arn)
                return True

            elif resource_type == "assessment_target":
                inspector.delete_assessment_target(assessmentTargetArn=resource_arn)
                return True

            return False

        except ClientError as e:
            self.logger.error(
                f"Error deleting Inspector {resource_type} {resource_arn}: {str(e)}"
            )
            return False
