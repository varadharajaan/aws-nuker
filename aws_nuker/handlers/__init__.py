"""AWS resource handlers package."""

from .ec2_handler import EC2Handler
from .s3_handler import S3Handler
from .rds_handler import RDSHandler
from .lambda_handler import LambdaHandler
from .iam_handler import IAMHandler
from .dynamodb_handler import DynamoDBHandler
from .cloudformation_handler import CloudFormationHandler
from .ecs_handler import ECSHandler
from .sns_handler import SNSHandler
from .sqs_handler import SQSHandler
from .cloudwatch_handler import CloudWatchHandler
from .apigateway_handler import APIGatewayHandler
from .elb_handler import ELBHandler
from .route53_handler import Route53Handler
from .vpc_handler import VPCHandler

__all__ = [
    "EC2Handler",
    "S3Handler",
    "RDSHandler",
    "LambdaHandler",
    "IAMHandler",
    "DynamoDBHandler",
    "CloudFormationHandler",
    "ECSHandler",
    "SNSHandler",
    "SQSHandler",
    "CloudWatchHandler",
    "APIGatewayHandler",
    "ELBHandler",
    "Route53Handler",
    "VPCHandler",
]
