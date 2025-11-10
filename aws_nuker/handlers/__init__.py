"""AWS resource handlers package."""

# Existing handlers
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

# New handlers
from .acm_handler import AcmHandler
from .appflow_handler import AppflowHandler
from .appmesh_handler import AppmeshHandler
from .apprunner_handler import ApprunnerHandler
from .appstream_handler import AppstreamHandler
from .autoscaling_handler import AutoscalingHandler
from .backup_handler import BackupHandler
from .batch_handler import BatchHandler
from .chime_handler import ChimeHandler
from .cloud9_handler import Cloud9Handler
from .cloudfront_handler import CloudfrontHandler
from .cloudhsm_handler import CloudhsmHandler
from .cloudmap_handler import CloudmapHandler
from .cloudsearch_handler import CloudsearchHandler
from .cloudtrail_handler import CloudtrailHandler
from .codeartifact_handler import CodeartifactHandler
from .codebuild_handler import CodebuildHandler
from .codecommit_handler import CodecommitHandler
from .codedeploy_handler import CodedeployHandler
from .codepipeline_handler import CodepipelineHandler
from .cognito_handler import CognitoHandler
from .comprehend_handler import ComprehendHandler
from .config_handler import ConfigHandler
from .connect_handler import ConnectHandler
from .datasync_handler import DatasyncHandler
from .detective_handler import DetectiveHandler
from .directconnect_handler import DirectconnectHandler
from .dms_handler import DmsHandler
from .docdb_handler import DocdbHandler
from .efs_handler import EfsHandler
from .elasticbeanstalk_handler import ElasticbeanstalkHandler
from .elastictranscoder_handler import ElastictranscoderHandler
from .emr_handler import EmrHandler
from .eventbridge_handler import EventbridgeHandler
from .firehose_handler import FirehoseHandler
from .fms_handler import FmsHandler
from .forecast_handler import ForecastHandler
from .frauddetector_handler import FrauddetectorHandler
from .fsx_handler import FsxHandler
from .glacier_handler import GlacierHandler
from .globalaccelerator_handler import GlobalacceleratorHandler
from .imagebuilder_handler import ImagebuilderHandler
from .inspector_handler import InspectorHandler
from .iot_handler import IotHandler
from .iotanalytics_handler import IotanalyticsHandler
from .iotevents_handler import IoteventsHandler
from .iotsitewise_handler import IotsitewiseHandler
from .ivs_handler import IvsHandler
from .kafka_handler import KafkaHandler
from .kendra_handler import KendraHandler
from .keyspaces_handler import KeyspacesHandler
from .lakeformation_handler import LakeformationHandler
from .lightsail_handler import LightsailHandler
from .macie_handler import MacieHandler
from .mediaconvert_handler import MediaconvertHandler
from .medialive_handler import MedialiveHandler
from .mediapackage_handler import MediapackageHandler
from .mediastore_handler import MediastoreHandler
from .mediatailor_handler import MediatailorHandler
from .memorydb_handler import MemorydbHandler
from .mq_handler import MqHandler
from .neptune_handler import NeptuneHandler
from .opensearch_handler import OpensearchHandler
from .opsworks_handler import OpsworksHandler
from .organizations_handler import OrganizationsHandler
from .outposts_handler import OutpostsHandler
from .personalize_handler import PersonalizeHandler
from .pinpoint_handler import PinpointHandler
from .polly_handler import PollyHandler
from .qldb_handler import QldbHandler
from .quicksight_handler import QuicksightHandler
from .ram_handler import RamHandler
from .rekognition_handler import RekognitionHandler
from .sagemaker_handler import SagemakerHandler
from .securityhub_handler import SecurityhubHandler
from .serverlessrepo_handler import ServerlessrepoHandler
from .servicecatalog_handler import ServicecatalogHandler
from .ses_handler import SesHandler
from .shield_handler import ShieldHandler
from .signer_handler import SignerHandler
from .ssm_handler import SsmHandler
from .stepfunctions_handler import StepfunctionsHandler
from .storagegateway_handler import StoragegatewayHandler
from .sts_handler import StsHandler
from .swf_handler import SwfHandler
from .textract_handler import TextractHandler
from .timestream_handler import TimestreamHandler
from .transcribe_handler import TranscribeHandler
from .transfer_handler import TransferHandler
from .translate_handler import TranslateHandler
from .waf_handler import WafHandler
from .wafv2_handler import Wafv2Handler
from .workdocs_handler import WorkdocsHandler
from .workmail_handler import WorkmailHandler
from .workspaces_handler import WorkspacesHandler
from .xray_handler import XrayHandler

__all__ = [
    "APIGatewayHandler",
    "AcmHandler",
    "AppflowHandler",
    "AppmeshHandler",
    "ApprunnerHandler",
    "AppstreamHandler",
    "AthenaHandler",
    "AutoscalingHandler",
    "BackupHandler",
    "BatchHandler",
    "ChimeHandler",
    "Cloud9Handler",
    "CloudFormationHandler",
    "CloudWatchHandler",
    "CloudfrontHandler",
    "CloudhsmHandler",
    "CloudmapHandler",
    "CloudsearchHandler",
    "CloudtrailHandler",
    "CodeartifactHandler",
    "CodebuildHandler",
    "CodecommitHandler",
    "CodedeployHandler",
    "CodepipelineHandler",
    "CognitoHandler",
    "ComprehendHandler",
    "ConfigHandler",
    "ConnectHandler",
    "DatasyncHandler",
    "DetectiveHandler",
    "DirectconnectHandler",
    "DmsHandler",
    "DocdbHandler",
    "DynamoDBHandler",
    "EC2Handler",
    "ECRHandler",
    "ECSHandler",
    "EKSHandler",
    "ELBHandler",
    "EfsHandler",
    "ElastiCacheHandler",
    "ElasticbeanstalkHandler",
    "ElastictranscoderHandler",
    "EmrHandler",
    "EventbridgeHandler",
    "FirehoseHandler",
    "FmsHandler",
    "ForecastHandler",
    "FrauddetectorHandler",
    "FsxHandler",
    "GlacierHandler",
    "GlobalacceleratorHandler",
    "GlueHandler",
    "GuardDutyHandler",
    "IAMHandler",
    "ImagebuilderHandler",
    "InspectorHandler",
    "IotHandler",
    "IotanalyticsHandler",
    "IoteventsHandler",
    "IotsitewiseHandler",
    "IvsHandler",
    "KMSHandler",
    "KafkaHandler",
    "KendraHandler",
    "KeyspacesHandler",
    "KinesisHandler",
    "LakeformationHandler",
    "LambdaHandler",
    "LightsailHandler",
    "MacieHandler",
    "MediaconvertHandler",
    "MedialiveHandler",
    "MediapackageHandler",
    "MediastoreHandler",
    "MediatailorHandler",
    "MemorydbHandler",
    "MqHandler",
    "NeptuneHandler",
    "OpensearchHandler",
    "OpsworksHandler",
    "OrganizationsHandler",
    "OutpostsHandler",
    "PersonalizeHandler",
    "PinpointHandler",
    "PollyHandler",
    "QldbHandler",
    "QuicksightHandler",
    "RDSHandler",
    "RamHandler",
    "RedshiftHandler",
    "RekognitionHandler",
    "Route53Handler",
    "S3Handler",
    "SNSHandler",
    "SQSHandler",
    "SagemakerHandler",
    "SecretsManagerHandler",
    "SecurityhubHandler",
    "ServerlessrepoHandler",
    "ServicecatalogHandler",
    "SesHandler",
    "ShieldHandler",
    "SignerHandler",
    "SsmHandler",
    "StepfunctionsHandler",
    "StoragegatewayHandler",
    "StsHandler",
    "SwfHandler",
    "TextractHandler",
    "TimestreamHandler",
    "TranscribeHandler",
    "TransferHandler",
    "TranslateHandler",
    "VPCHandler",
    "WafHandler",
    "Wafv2Handler",
    "WorkdocsHandler",
    "WorkmailHandler",
    "WorkspacesHandler",
    "XrayHandler",
]
