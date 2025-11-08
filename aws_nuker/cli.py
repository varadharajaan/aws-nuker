"""Command-line interface for AWS Nuker."""

import sys
import click
from colorama import init, Fore, Style
from tabulate import tabulate

from .config import NukerConfig, ALL_AWS_REGIONS, ALL_AWS_SERVICES
from .orchestrator import AWSNuker
from .logger import get_logger
from .registry import get_available_services

# Initialize colorama
init(autoreset=True)


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """AWS Nuker - Ruthless AWS Resource Cleanup Tool

    A powerful tool to destroy all non-default AWS resources across multiple
    regions and services. Use with EXTREME CAUTION!
    """
    pass


@cli.command()
@click.option(
    "--regions",
    "-r",
    default="us-east-1",
    help="AWS regions (single, comma-separated, range, or wildcard). Examples: 'us-east-1', 'us-east-1,us-west-2', 'us-*', or '*' for all regions.",
)
@click.option(
    "--services",
    "-s",
    default="*",
    help="AWS services to target (comma-separated or wildcard). Examples: 'ec2,s3,rds' or '*' for all services.",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Perform a dry run without actually deleting resources.",
)
@click.option(
    "--force",
    "-f",
    is_flag=True,
    default=False,
    help="Force deletion of resources even with dependencies.",
)
@click.option(
    "--parallel",
    is_flag=True,
    default=False,
    help="Execute cleanup in parallel (faster but less controlled).",
)
@click.option(
    "--max-workers",
    default=5,
    type=int,
    help="Maximum number of parallel workers (default: 5).",
)
@click.option(
    "--yes",
    "-y",
    is_flag=True,
    default=False,
    help="Skip confirmation prompt.",
)
def nuke(regions, services, dry_run, force, parallel, max_workers, yes):
    """Execute the AWS resource cleanup operation.

    This command will DELETE all non-default AWS resources in the specified
    regions and services. THIS ACTION IS IRREVERSIBLE!

    Examples:

        # Dry run for EC2 in us-east-1
        aws-nuker nuke --regions us-east-1 --services ec2 --dry-run

        # Delete all S3 and RDS resources in multiple regions
        aws-nuker nuke --regions us-east-1,us-west-2 --services s3,rds --force

        # Nuclear option: Delete everything in all US regions
        aws-nuker nuke --regions "us-*" --services "*" --force --yes
    """
    logger = get_logger()

    # Parse configuration
    parsed_regions = NukerConfig.parse_regions(regions)
    parsed_services = NukerConfig.parse_services(services)

    # Create configuration
    config = NukerConfig(
        regions=parsed_regions,
        services=parsed_services,
        dry_run=dry_run,
        force=force,
        parallel_execution=parallel,
        max_workers=max_workers,
    )

    # Display configuration
    print(f"\n{Fore.RED}{'=' * 80}")
    print(f"{Fore.RED}AWS NUKER - CONFIGURATION")
    print(f"{Fore.RED}{'=' * 80}{Style.RESET_ALL}\n")

    print(f"{Fore.CYAN}Regions:{Style.RESET_ALL}")
    for region in config.regions:
        print(f"  - {region}")

    print(f"\n{Fore.CYAN}Services ({len(config.services)}):{Style.RESET_ALL}")
    service_list = sorted(config.services)
    for i in range(0, len(service_list), 5):
        print(f"  {', '.join(service_list[i:i+5])}")

    print(f"\n{Fore.CYAN}Options:{Style.RESET_ALL}")
    print(f"  Dry Run: {Fore.GREEN if dry_run else Fore.RED}{dry_run}{Style.RESET_ALL}")
    print(f"  Force: {Fore.RED if force else Fore.GREEN}{force}{Style.RESET_ALL}")
    print(f"  Parallel: {parallel}")
    if parallel:
        print(f"  Max Workers: {max_workers}")

    # Confirmation
    if not yes and not dry_run:
        print(f"\n{Fore.RED}{'=' * 80}")
        print(f"{Fore.RED}WARNING: THIS WILL DELETE RESOURCES PERMANENTLY!")
        print(f"{Fore.RED}{'=' * 80}{Style.RESET_ALL}\n")

        confirmation = click.prompt(
            f"{Fore.YELLOW}Type 'DELETE' to proceed{Style.RESET_ALL}",
            type=str,
        )

        if confirmation != "DELETE":
            print(f"{Fore.GREEN}Operation cancelled.{Style.RESET_ALL}")
            sys.exit(0)

    # Execute
    print(f"\n{Fore.GREEN}Starting cleanup operation...{Style.RESET_ALL}\n")

    try:
        nuker = AWSNuker(config)
        summary = nuker.execute()

        # Display summary
        print(f"\n{Fore.GREEN}{'=' * 80}")
        print(f"{Fore.GREEN}EXECUTION SUMMARY")
        print(f"{Fore.GREEN}{'=' * 80}{Style.RESET_ALL}\n")

        summary_data = [
            ["Total Execution Time", f"{summary['elapsed_time']:.2f}s"],
            ["Regions Processed", len(summary['regions'])],
            ["Services Processed", summary['services_processed']],
            ["Total Resources Found", summary['total_resources']],
            ["Resources Deleted", summary['total_deleted']],
            ["Resources Failed", summary['total_failed']],
            ["Resources Skipped", summary['total_skipped']],
        ]

        print(tabulate(summary_data, tablefmt="grid"))

        if summary["errors"]:
            print(f"\n{Fore.RED}Errors encountered: {len(summary['errors'])}{Style.RESET_ALL}")

        if summary["dry_run"]:
            print(f"\n{Fore.YELLOW}NOTE: This was a DRY RUN - no actual deletions occurred{Style.RESET_ALL}")

        # Display log locations
        print(f"\n{Fore.CYAN}Log Files:{Style.RESET_ALL}")
        print(f"  Main Log: {logger.get_log_file()}")
        print(f"  Audit Log: {logger.get_audit_file()}")

    except Exception as e:
        print(f"\n{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")
        logger.error(f"Fatal error: {str(e)}")
        sys.exit(1)


@cli.command()
def list_services():
    """List all available AWS services that can be targeted."""
    print(f"\n{Fore.CYAN}Available AWS Services:{Style.RESET_ALL}\n")

    services = get_available_services()
    for i in range(0, len(services), 5):
        print(f"  {', '.join(services[i:i+5])}")

    print(f"\n{Fore.GREEN}Total: {len(services)} services{Style.RESET_ALL}\n")


@cli.command()
def list_regions():
    """List all available AWS regions."""
    print(f"\n{Fore.CYAN}Available AWS Regions:{Style.RESET_ALL}\n")

    for i in range(0, len(ALL_AWS_REGIONS), 4):
        print(f"  {', '.join(ALL_AWS_REGIONS[i:i+4])}")

    print(f"\n{Fore.GREEN}Total: {len(ALL_AWS_REGIONS)} regions{Style.RESET_ALL}\n")


def main():
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()
