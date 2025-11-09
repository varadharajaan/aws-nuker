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
from .ecr_handler import ECRHandler
from .eks_handler import EKSHandler
from .kinesis_handler import KinesisHandler
from .athena_handler import AthenaHandler
from .glue_handler import GlueHandler
from .redshift_handler import RedshiftHandler
from .elasticache_handler import ElastiCacheHandler
from .kms_handler import KMSHandler
from .secretsmanager_handler import SecretsManagerHandler
from .guardduty_handler import GuardDutyHandler

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
    "ECRHandler",
    "EKSHandler",
    "KinesisHandler",
    "AthenaHandler",
    "GlueHandler",
    "RedshiftHandler",
    "ElastiCacheHandler",
    "KMSHandler",
    "SecretsManagerHandler",
    "GuardDutyHandler",
]
