"""Handler registry for mapping services to handlers."""

from typing import Dict, Type
from .base_handler import ResourceHandler
from .handlers import (
    EC2Handler,
    S3Handler,
    RDSHandler,
    LambdaHandler,
    IAMHandler,
    DynamoDBHandler,
    CloudFormationHandler,
    ECSHandler,
    SNSHandler,
    SQSHandler,
    CloudWatchHandler,
    APIGatewayHandler,
    ELBHandler,
    Route53Handler,
    VPCHandler,
)


# Service name to handler class mapping
HANDLER_REGISTRY: Dict[str, Type[ResourceHandler]] = {
    "ec2": EC2Handler,
    "s3": S3Handler,
    "rds": RDSHandler,
    "lambda": LambdaHandler,
    "iam": IAMHandler,
    "dynamodb": DynamoDBHandler,
    "cloudformation": CloudFormationHandler,
    "ecs": ECSHandler,
    "sns": SNSHandler,
    "sqs": SQSHandler,
    "cloudwatch": CloudWatchHandler,
    "logs": CloudWatchHandler,  # CloudWatch Logs uses same handler
    "apigateway": APIGatewayHandler,
    "apigatewayv2": APIGatewayHandler,  # API Gateway v2 uses same handler
    "elb": ELBHandler,
    "elbv2": ELBHandler,  # ELBv2 uses same handler
    "route53": Route53Handler,
    "vpc": VPCHandler,
}


def get_handler(
    service_name: str,
    region: str,
    dry_run: bool = False,
    force: bool = False,
) -> ResourceHandler:
    """
    Get handler instance for a service.

    Args:
        service_name: AWS service name
        region: AWS region
        dry_run: Dry run mode
        force: Force deletion mode

    Returns:
        Handler instance

    Raises:
        ValueError: If service handler not found
    """
    handler_class = HANDLER_REGISTRY.get(service_name.lower())
    if handler_class is None:
        raise ValueError(f"No handler found for service: {service_name}")

    return handler_class(region=region, dry_run=dry_run, force=force)


def get_available_services() -> list:
    """Get list of available service names."""
    return sorted(set(HANDLER_REGISTRY.keys()))
