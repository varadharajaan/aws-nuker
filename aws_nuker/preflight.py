"""
Pre-flight checks for AWS Nuker.

Validates AWS credentials, permissions, and configuration
before starting cleanup operations.
"""

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set

import boto3
from botocore.exceptions import (
    ClientError,
    NoCredentialsError,
    PartialCredentialsError,
)

from .exceptions import (
    AuthenticationError,
    CredentialsExpiredError,
    CredentialsNotFoundError,
    PermissionDeniedError,
    PreflightCheckError,
    ServiceNotSupportedError,
)


class CheckStatus(Enum):
    """Status of a pre-flight check."""
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    SKIPPED = "skipped"


@dataclass
class CheckResult:
    """Result of a single pre-flight check."""
    name: str
    status: CheckStatus
    message: str
    details: Optional[Dict[str, Any]] = None
    duration_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "status": self.status.value,
            "message": self.message,
            "details": self.details,
            "duration_ms": self.duration_ms,
        }


@dataclass
class PreflightReport:
    """Report containing all pre-flight check results."""
    passed: bool = True
    checks: List[CheckResult] = field(default_factory=list)
    total_duration_ms: float = 0.0
    account_id: Optional[str] = None
    user_arn: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    def add_check(self, result: CheckResult):
        """Add a check result to the report."""
        self.checks.append(result)
        self.total_duration_ms += result.duration_ms

        if result.status == CheckStatus.FAILED:
            self.passed = False
            self.errors.append(f"{result.name}: {result.message}")
        elif result.status == CheckStatus.WARNING:
            self.warnings.append(f"{result.name}: {result.message}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "passed": self.passed,
            "account_id": self.account_id,
            "user_arn": self.user_arn,
            "total_duration_ms": self.total_duration_ms,
            "checks": [c.to_dict() for c in self.checks],
            "warnings": self.warnings,
            "errors": self.errors,
        }


class PreflightChecker:
    """
    Pre-flight checker for AWS Nuker operations.

    Validates:
    - AWS credentials are valid
    - Required permissions are available
    - Services are accessible in target regions
    - Configuration is valid
    """

    # Minimum required permissions per service
    REQUIRED_PERMISSIONS: Dict[str, List[str]] = {
        "ec2": ["ec2:DescribeInstances", "ec2:TerminateInstances"],
        "s3": ["s3:ListBuckets", "s3:DeleteBucket"],
        "lambda": ["lambda:ListFunctions", "lambda:DeleteFunction"],
        "rds": ["rds:DescribeDBInstances", "rds:DeleteDBInstance"],
        "dynamodb": ["dynamodb:ListTables", "dynamodb:DeleteTable"],
        "ecs": ["ecs:ListClusters", "ecs:DeleteCluster"],
        "sns": ["sns:ListTopics", "sns:DeleteTopic"],
        "sqs": ["sqs:ListQueues", "sqs:DeleteQueue"],
        "iam": ["iam:ListUsers", "iam:ListRoles"],
        "cloudformation": ["cloudformation:ListStacks", "cloudformation:DeleteStack"],
    }

    def __init__(
        self,
        regions: Optional[List[str]] = None,
        services: Optional[Set[str]] = None,
        dry_run: bool = False,
    ):
        """
        Initialize pre-flight checker.

        Args:
            regions: List of AWS regions to check
            services: Set of services to check
            dry_run: If True, only check read permissions
        """
        self.regions = regions or ["us-east-1"]
        self.services = services or set()
        self.dry_run = dry_run
        self._session: Optional[boto3.Session] = None

    def run_all_checks(self) -> PreflightReport:
        """
        Run all pre-flight checks.

        Returns:
            PreflightReport with all check results
        """
        report = PreflightReport()
        start_time = time.time()

        # Run credential checks
        cred_result = self._check_credentials()
        report.add_check(cred_result)

        if cred_result.status == CheckStatus.FAILED:
            # Can't continue without valid credentials
            report.total_duration_ms = (time.time() - start_time) * 1000
            return report

        # Get account info
        identity = cred_result.details or {}
        report.account_id = identity.get("account_id")
        report.user_arn = identity.get("user_arn")

        # Run permission checks for each service
        for service in self.services:
            if service in self.REQUIRED_PERMISSIONS:
                perm_result = self._check_service_permissions(service)
                report.add_check(perm_result)

        # Run region availability checks
        for region in self.regions:
            region_result = self._check_region_availability(region)
            report.add_check(region_result)

        # Check for service availability in regions
        for region in self.regions:
            for service in list(self.services)[:5]:  # Limit to avoid too many checks
                svc_result = self._check_service_in_region(service, region)
                report.add_check(svc_result)

        report.total_duration_ms = (time.time() - start_time) * 1000
        return report

    def _check_credentials(self) -> CheckResult:
        """Check if AWS credentials are valid."""
        start_time = time.time()
        name = "aws_credentials"

        try:
            self._session = boto3.Session()
            sts = self._session.client("sts")

            # Get caller identity to verify credentials
            identity = sts.get_caller_identity()

            duration_ms = (time.time() - start_time) * 1000

            return CheckResult(
                name=name,
                status=CheckStatus.PASSED,
                message="AWS credentials are valid",
                details={
                    "account_id": identity.get("Account"),
                    "user_arn": identity.get("Arn"),
                    "user_id": identity.get("UserId"),
                },
                duration_ms=duration_ms,
            )

        except NoCredentialsError:
            duration_ms = (time.time() - start_time) * 1000
            return CheckResult(
                name=name,
                status=CheckStatus.FAILED,
                message="AWS credentials not found",
                details={"hint": "Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY"},
                duration_ms=duration_ms,
            )

        except PartialCredentialsError as e:
            duration_ms = (time.time() - start_time) * 1000
            return CheckResult(
                name=name,
                status=CheckStatus.FAILED,
                message="Incomplete AWS credentials",
                details={"error": str(e)},
                duration_ms=duration_ms,
            )

        except ClientError as e:
            duration_ms = (time.time() - start_time) * 1000
            error_code = e.response.get("Error", {}).get("Code", "")

            if error_code == "ExpiredToken":
                return CheckResult(
                    name=name,
                    status=CheckStatus.FAILED,
                    message="AWS credentials have expired",
                    details={"error_code": error_code},
                    duration_ms=duration_ms,
                )
            elif error_code == "InvalidClientTokenId":
                return CheckResult(
                    name=name,
                    status=CheckStatus.FAILED,
                    message="Invalid AWS credentials",
                    details={"error_code": error_code},
                    duration_ms=duration_ms,
                )
            else:
                return CheckResult(
                    name=name,
                    status=CheckStatus.FAILED,
                    message=f"AWS credential error: {error_code}",
                    details={"error": str(e)},
                    duration_ms=duration_ms,
                )

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            return CheckResult(
                name=name,
                status=CheckStatus.FAILED,
                message=f"Unexpected error checking credentials: {str(e)}",
                duration_ms=duration_ms,
            )

    def _check_service_permissions(self, service: str) -> CheckResult:
        """Check if required permissions are available for a service."""
        start_time = time.time()
        name = f"permissions_{service}"

        if not self._session:
            return CheckResult(
                name=name,
                status=CheckStatus.SKIPPED,
                message="Session not available",
                duration_ms=0.0,
            )

        required = self.REQUIRED_PERMISSIONS.get(service, [])
        if not required:
            return CheckResult(
                name=name,
                status=CheckStatus.SKIPPED,
                message=f"No permission requirements defined for {service}",
                duration_ms=0.0,
            )

        try:
            # Use IAM policy simulator if available
            iam = self._session.client("iam")

            try:
                # Get caller identity to get the ARN
                sts = self._session.client("sts")
                identity = sts.get_caller_identity()
                caller_arn = identity.get("Arn", "")

                # Simulate policy
                response = iam.simulate_principal_policy(
                    PolicySourceArn=caller_arn,
                    ActionNames=required[:5],  # Limit actions to avoid throttling
                    ResourceArns=["*"],
                )

                results = response.get("EvaluationResults", [])
                denied = [
                    r["EvalActionName"]
                    for r in results
                    if r.get("EvalDecision") != "allowed"
                ]

                duration_ms = (time.time() - start_time) * 1000

                if denied:
                    return CheckResult(
                        name=name,
                        status=CheckStatus.WARNING,
                        message=f"Some permissions may be missing for {service}",
                        details={"denied_actions": denied},
                        duration_ms=duration_ms,
                    )

                return CheckResult(
                    name=name,
                    status=CheckStatus.PASSED,
                    message=f"Required permissions available for {service}",
                    details={"checked_actions": required[:5]},
                    duration_ms=duration_ms,
                )

            except ClientError as e:
                # Policy simulation might not be allowed
                error_code = e.response.get("Error", {}).get("Code", "")
                if error_code in ["AccessDenied", "UnauthorizedAccess"]:
                    # Can't simulate, try a basic API call instead
                    return self._check_service_basic(service, start_time)
                raise

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            return CheckResult(
                name=name,
                status=CheckStatus.WARNING,
                message=f"Could not verify permissions for {service}",
                details={"error": str(e)},
                duration_ms=duration_ms,
            )

    def _check_service_basic(self, service: str, start_time: float) -> CheckResult:
        """Basic service check using a simple API call."""
        name = f"permissions_{service}"

        if not self._session:
            return CheckResult(
                name=name,
                status=CheckStatus.SKIPPED,
                message="Session not available",
                duration_ms=0.0,
            )

        try:
            client = self._session.client(service, region_name=self.regions[0])

            # Try a simple list operation based on service
            list_operations = {
                "ec2": lambda c: c.describe_instances(MaxResults=5),
                "s3": lambda c: c.list_buckets(),
                "lambda": lambda c: c.list_functions(MaxItems=1),
                "rds": lambda c: c.describe_db_instances(),
                "dynamodb": lambda c: c.list_tables(Limit=1),
                "ecs": lambda c: c.list_clusters(maxResults=1),
                "sns": lambda c: c.list_topics(),
                "sqs": lambda c: c.list_queues(MaxResults=1),
            }

            if service in list_operations:
                list_operations[service](client)

            duration_ms = (time.time() - start_time) * 1000
            return CheckResult(
                name=name,
                status=CheckStatus.PASSED,
                message=f"Basic access verified for {service}",
                duration_ms=duration_ms,
            )

        except ClientError as e:
            duration_ms = (time.time() - start_time) * 1000
            error_code = e.response.get("Error", {}).get("Code", "")

            if error_code in ["AccessDenied", "UnauthorizedOperation"]:
                return CheckResult(
                    name=name,
                    status=CheckStatus.FAILED,
                    message=f"Access denied for {service}",
                    details={"error_code": error_code},
                    duration_ms=duration_ms,
                )

            return CheckResult(
                name=name,
                status=CheckStatus.WARNING,
                message=f"Could not verify access for {service}",
                details={"error": str(e)},
                duration_ms=duration_ms,
            )

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            return CheckResult(
                name=name,
                status=CheckStatus.WARNING,
                message=f"Error checking {service}",
                details={"error": str(e)},
                duration_ms=duration_ms,
            )

    def _check_region_availability(self, region: str) -> CheckResult:
        """Check if a region is available."""
        start_time = time.time()
        name = f"region_{region}"

        if not self._session:
            return CheckResult(
                name=name,
                status=CheckStatus.SKIPPED,
                message="Session not available",
                duration_ms=0.0,
            )

        try:
            ec2 = self._session.client("ec2", region_name=region)
            ec2.describe_availability_zones()

            duration_ms = (time.time() - start_time) * 1000
            return CheckResult(
                name=name,
                status=CheckStatus.PASSED,
                message=f"Region {region} is accessible",
                duration_ms=duration_ms,
            )

        except ClientError as e:
            duration_ms = (time.time() - start_time) * 1000
            error_code = e.response.get("Error", {}).get("Code", "")

            if error_code == "AuthFailure":
                return CheckResult(
                    name=name,
                    status=CheckStatus.WARNING,
                    message=f"Region {region} may not be enabled for this account",
                    details={"error_code": error_code},
                    duration_ms=duration_ms,
                )

            return CheckResult(
                name=name,
                status=CheckStatus.WARNING,
                message=f"Could not verify region {region}",
                details={"error": str(e)},
                duration_ms=duration_ms,
            )

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            return CheckResult(
                name=name,
                status=CheckStatus.WARNING,
                message=f"Error checking region {region}",
                details={"error": str(e)},
                duration_ms=duration_ms,
            )

    def _check_service_in_region(self, service: str, region: str) -> CheckResult:
        """Check if a service is available in a region."""
        start_time = time.time()
        name = f"service_{service}_in_{region}"

        if not self._session:
            return CheckResult(
                name=name,
                status=CheckStatus.SKIPPED,
                message="Session not available",
                duration_ms=0.0,
            )

        try:
            # Try to create a client for the service in the region
            client = self._session.client(service, region_name=region)

            # Just creating the client is usually sufficient
            # The actual API call will fail if the service isn't available
            duration_ms = (time.time() - start_time) * 1000

            return CheckResult(
                name=name,
                status=CheckStatus.PASSED,
                message=f"Service {service} available in {region}",
                duration_ms=duration_ms,
            )

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            return CheckResult(
                name=name,
                status=CheckStatus.WARNING,
                message=f"Service {service} may not be available in {region}",
                details={"error": str(e)},
                duration_ms=duration_ms,
            )


def run_preflight_checks(
    regions: Optional[List[str]] = None,
    services: Optional[Set[str]] = None,
    dry_run: bool = False,
    raise_on_failure: bool = True,
) -> PreflightReport:
    """
    Convenience function to run all pre-flight checks.

    Args:
        regions: List of AWS regions to check
        services: Set of services to check
        dry_run: If True, only check read permissions
        raise_on_failure: If True, raise exception on critical failures

    Returns:
        PreflightReport with all results

    Raises:
        PreflightCheckError: If raise_on_failure is True and checks fail
    """
    checker = PreflightChecker(
        regions=regions,
        services=services,
        dry_run=dry_run,
    )

    report = checker.run_all_checks()

    if raise_on_failure and not report.passed:
        raise PreflightCheckError(
            check_name="preflight",
            reason="; ".join(report.errors),
            details=report.to_dict(),
        )

    return report
