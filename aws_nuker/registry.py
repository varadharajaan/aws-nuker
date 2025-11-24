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
    ECRHandler,
    EKSHandler,
    KinesisHandler,
    AthenaHandler,
    GlueHandler,
    RedshiftHandler,
    ElastiCacheHandler,
    KMSHandler,
    SecretsManagerHandler,
    GuardDutyHandler,
    ACMHandler,
    CognitoHandler,
    CloudTrailHandler,
    ConfigHandler,
    EFSHandler,
    EMRHandler,
    CodeCommitHandler,
    CodeBuildHandler,
    CodePipelineHandler,
    StepFunctionsHandler,
    EventBridgeHandler,
    SESHandler,
    BatchHandler,
    SSMHandler,
    WAFv2Handler,
    CloudFrontHandler,
    BackupHandler,
    ElasticBeanstalkHandler,
    LightsailHandler,
    SageMakerHandler,
    NeptuneHandler,
    DocumentDBHandler,
    OpenSearchHandler,
    CloudMapHandler,
    AppFlowHandler,
    DMSHandler,
    FirehoseHandler,
    KafkaHandler,
    DirectConnectHandler,
    AppMeshHandler,
    WorkSpacesHandler,
    TransferHandler,
    FSxHandler,
    DataSyncHandler,
    InspectorHandler,
    AutoScalingHandler,
    CodeDeployHandler,
    XRayHandler,
    MQHandler,
    QuickSightHandler,
    MacieHandler,
    WAFHandler,
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
    "ecr": ECRHandler,
    "eks": EKSHandler,
    "kinesis": KinesisHandler,
    "athena": AthenaHandler,
    "glue": GlueHandler,
    "redshift": RedshiftHandler,
    "elasticache": ElastiCacheHandler,
    "kms": KMSHandler,
    "secretsmanager": SecretsManagerHandler,
    "guardduty": GuardDutyHandler,
    "acm": ACMHandler,
    "cognito": CognitoHandler,
    "cloudtrail": CloudTrailHandler,
    "config": ConfigHandler,
    "efs": EFSHandler,
    "emr": EMRHandler,
    "codecommit": CodeCommitHandler,
    "codebuild": CodeBuildHandler,
    "codepipeline": CodePipelineHandler,
    "stepfunctions": StepFunctionsHandler,
    "eventbridge": EventBridgeHandler,
    "ses": SESHandler,
    "batch": BatchHandler,
    "ssm": SSMHandler,
    "wafv2": WAFv2Handler,
    "cloudfront": CloudFrontHandler,
    "backup": BackupHandler,
    "elasticbeanstalk": ElasticBeanstalkHandler,
    "lightsail": LightsailHandler,
    "sagemaker": SageMakerHandler,
    "neptune": NeptuneHandler,
    "docdb": DocumentDBHandler,
    "opensearch": OpenSearchHandler,
    "cloudmap": CloudMapHandler,
    "appflow": AppFlowHandler,
    "dms": DMSHandler,
    "firehose": FirehoseHandler,
    "kafka": KafkaHandler,
    "directconnect": DirectConnectHandler,
    "appmesh": AppMeshHandler,
    "workspaces": WorkSpacesHandler,
    "transfer": TransferHandler,
    "fsx": FSxHandler,
    "datasync": DataSyncHandler,
    "inspector": InspectorHandler,
    "autoscaling": AutoScalingHandler,
    "codedeploy": CodeDeployHandler,
    "xray": XRayHandler,
    "mq": MQHandler,
    "quicksight": QuickSightHandler,
    "macie": MacieHandler,
    "waf": WAFHandler,
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
