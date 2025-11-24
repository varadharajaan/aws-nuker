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
from .acm_handler import ACMHandler
from .cognito_handler import CognitoHandler
from .cloudtrail_handler import CloudTrailHandler
from .config_handler import ConfigHandler
from .efs_handler import EFSHandler
from .emr_handler import EMRHandler
from .codecommit_handler import CodeCommitHandler
from .codebuild_handler import CodeBuildHandler
from .codepipeline_handler import CodePipelineHandler
from .stepfunctions_handler import StepFunctionsHandler
from .eventbridge_handler import EventBridgeHandler
from .ses_handler import SESHandler
from .batch_handler import BatchHandler
from .ssm_handler import SSMHandler
from .wafv2_handler import WAFv2Handler
from .cloudfront_handler import CloudFrontHandler
from .backup_handler import BackupHandler
from .elasticbeanstalk_handler import ElasticBeanstalkHandler
from .lightsail_handler import LightsailHandler
from .sagemaker_handler import SageMakerHandler
from .neptune_handler import NeptuneHandler
from .docdb_handler import DocumentDBHandler
from .opensearch_handler import OpenSearchHandler
from .cloudmap_handler import CloudMapHandler
from .appflow_handler import AppFlowHandler
from .dms_handler import DMSHandler
from .firehose_handler import FirehoseHandler
from .kafka_handler import KafkaHandler
from .directconnect_handler import DirectConnectHandler
from .appmesh_handler import AppMeshHandler
from .workspaces_handler import WorkSpacesHandler
from .transfer_handler import TransferHandler
from .fsx_handler import FSxHandler
from .datasync_handler import DataSyncHandler
from .inspector_handler import InspectorHandler
from .autoscaling_handler import AutoScalingHandler
from .codedeploy_handler import CodeDeployHandler
from .xray_handler import XRayHandler
from .mq_handler import MQHandler
from .quicksight_handler import QuickSightHandler
from .macie_handler import MacieHandler
from .waf_handler import WAFHandler

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
    "ACMHandler",
    "CognitoHandler",
    "CloudTrailHandler",
    "ConfigHandler",
    "EFSHandler",
    "EMRHandler",
    "CodeCommitHandler",
    "CodeBuildHandler",
    "CodePipelineHandler",
    "StepFunctionsHandler",
    "EventBridgeHandler",
    "SESHandler",
    "BatchHandler",
    "SSMHandler",
    "WAFv2Handler",
    "CloudFrontHandler",
    "BackupHandler",
    "ElasticBeanstalkHandler",
    "LightsailHandler",
    "SageMakerHandler",
    "NeptuneHandler",
    "DocumentDBHandler",
    "OpenSearchHandler",
    "CloudMapHandler",
    "AppFlowHandler",
    "DMSHandler",
    "FirehoseHandler",
    "KafkaHandler",
    "DirectConnectHandler",
    "AppMeshHandler",
    "WorkSpacesHandler",
    "TransferHandler",
    "FSxHandler",
    "DataSyncHandler",
    "InspectorHandler",
    "AutoScalingHandler",
    "CodeDeployHandler",
    "XRayHandler",
    "MQHandler",
    "QuickSightHandler",
    "MacieHandler",
    "WAFHandler",
]
