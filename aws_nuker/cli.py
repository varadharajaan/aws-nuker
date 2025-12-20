"""Command-line interface for AWS Nuker."""

import sys
import click
from colorama import init, Fore, Style
from tabulate import tabulate

from .config import NukerConfig, ALL_AWS_REGIONS
from .orchestrator import AWSNuker
from .logger import get_logger
from .registry import get_available_services
from .tag_manager import TagManager, TagFilter
from .policy_templates import PolicyTemplates, PolicyType
from .approval_gate import ApprovalGate
from .notification_manager import NotificationManager

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
    help=(
        "AWS regions (single, comma-separated, range, or wildcard). "
        "Examples: 'us-east-1', 'us-east-1,us-west-2', 'us-*', "
        "or '*' for all regions."
    ),
)
@click.option(
    "--services",
    "-s",
    default="*",
    help=(
        "AWS services to target (comma-separated or wildcard). "
        "Examples: 'ec2,s3,rds' or '*' for all services."
    ),
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
    print(
        f"  Dry Run: {Fore.GREEN if dry_run else Fore.RED}"
        f"{dry_run}{Style.RESET_ALL}"
    )
    print(
        f"  Force: {Fore.RED if force else Fore.GREEN}"
        f"{force}{Style.RESET_ALL}"
    )
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
            print(
                f"\n{Fore.RED}Errors encountered: "
                f"{len(summary['errors'])}{Style.RESET_ALL}"
            )

        if summary["dry_run"]:
            print(
                f"\n{Fore.YELLOW}NOTE: This was a DRY RUN - "
                f"no actual deletions occurred{Style.RESET_ALL}"
            )

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


@cli.command()
@click.option(
    "--region",
    "-r",
    default="us-east-1",
    help="AWS region to discover resources in"
)
@click.option(
    "--tag-key",
    help="Filter by tag key pattern (supports wildcards)"
)
@click.option(
    "--tag-value",
    help="Filter by tag value pattern (supports wildcards)"
)
@click.option(
    "--show-untagged",
    is_flag=True,
    help="Show untagged resources"
)
def discover_tags(region, tag_key, tag_value, show_untagged):
    """Discover and group resources by tags.
    
    Examples:
    
        # Discover all resources
        aws-nuker discover-tags --region us-east-1
        
        # Find resources with env=dev
        aws-nuker discover-tags --tag-key env --tag-value dev
        
        # Find untagged resources
        aws-nuker discover-tags --show-untagged
    """
    print(f"\n{Fore.CYAN}Discovering resources in {region}...{Style.RESET_ALL}\n")
    
    tag_manager = TagManager(region=region)
    
    # Create filters if specified
    tag_filters = []
    if tag_key or tag_value:
        tag_filters = tag_manager.filter_by_tag_pattern(
            key_pattern=tag_key,
            value_pattern=tag_value
        )
    
    # Discover resources
    result = tag_manager.discover_resources(tag_filters=tag_filters if tag_filters else None)
    
    # Display summary
    summary_data = [
        ["Total Resources", result.total_resources],
        ["Tagged Resources", result.tagged_resources],
        ["Untagged Resources", result.untagged_resources],
        ["Tag Groups", len(result.tag_groups)]
    ]
    
    print(f"{Fore.GREEN}Discovery Summary:{Style.RESET_ALL}\n")
    print(tabulate(summary_data, tablefmt="grid"))
    
    # Show top tag groups
    print(f"\n{Fore.GREEN}Top Tag Groups:{Style.RESET_ALL}\n")
    
    tag_group_data = []
    for i, group in enumerate(result.tag_groups[:10], 1):
        tags_str = ", ".join([f"{k}={v}" for k, v in group.tags.items()][:3])
        if len(group.tags) > 3:
            tags_str += "..."
        
        tag_group_data.append([
            i,
            tags_str or "UNTAGGED",
            group.resource_count,
            ", ".join(list(group.resource_types)[:2])
        ])
    
    print(tabulate(
        tag_group_data,
        headers=["#", "Tags", "Resources", "Types"],
        tablefmt="grid"
    ))
    
    if show_untagged:
        untagged = tag_manager.filter_untagged_resources(result)
        print(f"\n{Fore.YELLOW}Untagged Resources: {len(untagged)}{Style.RESET_ALL}\n")
        
        if untagged:
            untagged_data = []
            for resource in untagged[:20]:
                untagged_data.append([
                    resource.get('ResourceType', 'Unknown'),
                    resource.get('ARN', 'Unknown')[:60] + "..."
                ])
            
            print(tabulate(
                untagged_data,
                headers=["Type", "ARN"],
                tablefmt="grid"
            ))


@cli.command()
def list_policies():
    """List available cleanup policy templates.
    
    Shows predefined policies like dev cleanup, orphan purge, and cost optimization.
    """
    print(f"\n{Fore.CYAN}Available Cleanup Policies:{Style.RESET_ALL}\n")
    
    templates = PolicyTemplates.get_all_templates()
    
    policy_data = []
    for policy in templates:
        policy_data.append([
            policy.name,
            policy.policy_type.value,
            f"${policy.approval_threshold_usd}",
            "Yes" if policy.soft_delete else "No",
            policy.soft_delete_ttl_days if policy.soft_delete else "N/A"
        ])
    
    print(tabulate(
        policy_data,
        headers=["Name", "Type", "Approval >", "Soft Delete", "TTL Days"],
        tablefmt="grid"
    ))
    
    print(f"\n{Fore.GREEN}Use 'aws-nuker show-policy <type>' to see policy details{Style.RESET_ALL}\n")


@cli.command()
@click.argument("policy_type", type=click.Choice([
    "dev_cleanup", "orphan_purge", "cost_kill", "storage_cleanup"
]))
def show_policy(policy_type):
    """Show details of a specific policy template.
    
    Examples:
    
        aws-nuker show-policy dev_cleanup
        aws-nuker show-policy orphan_purge
    """
    policy = PolicyTemplates.get_template_by_type(PolicyType(policy_type))
    
    if not policy:
        print(f"{Fore.RED}Policy not found{Style.RESET_ALL}")
        return
    
    print(f"\n{Fore.CYAN}Policy: {policy.name}{Style.RESET_ALL}\n")
    print(f"{Fore.GREEN}Description:{Style.RESET_ALL} {policy.description}\n")
    
    details = [
        ["Type", policy.policy_type.value],
        ["Age Threshold", f"{policy.age_threshold_days} days"],
        ["Approval Required", "Yes" if policy.require_approval else "No"],
        ["Approval Threshold", f"${policy.approval_threshold_usd}"],
        ["Soft Delete", "Yes" if policy.soft_delete else "No"],
        ["Soft Delete TTL", f"{policy.soft_delete_ttl_days} days" if policy.soft_delete else "N/A"],
        ["Create Snapshots", "Yes" if policy.create_snapshot else "No"],
        ["Snapshot Threshold", f"{policy.snapshot_threshold_gb} GB" if policy.create_snapshot else "N/A"],
        ["Services", ", ".join(policy.included_services[:5]) + ("..." if len(policy.included_services) > 5 else "")],
        ["Notifications", ", ".join(policy.notification_channels)]
    ]
    
    print(tabulate(details, tablefmt="grid"))
    
    print(f"\n{Fore.CYAN}Tag Filters:{Style.RESET_ALL}\n")
    print(policy.to_json())


@cli.command()
@click.option(
    "--region",
    "-r",
    default="us-east-1",
    help="AWS region"
)
@click.option(
    "--min-resources",
    default=5,
    type=int,
    help="Minimum resources in group to suggest"
)
def suggest_cleanup(region, min_resources):
    """Get intelligent cleanup suggestions based on tags.
    
    Analyzes resources and suggests groups that might be good cleanup candidates.
    """
    print(f"\n{Fore.CYAN}Analyzing resources for cleanup opportunities...{Style.RESET_ALL}\n")
    
    tag_manager = TagManager(region=region)
    suggestions = tag_manager.suggest_cleanup_targets(min_resource_count=min_resources)
    
    if not suggestions:
        print(f"{Fore.GREEN}No cleanup suggestions found{Style.RESET_ALL}")
        return
    
    print(f"{Fore.YELLOW}Cleanup Suggestions:{Style.RESET_ALL}\n")
    
    suggestion_data = []
    for i, (group, reason) in enumerate(suggestions, 1):
        tags_str = ", ".join([f"{k}={v}" for k, v in group.tags.items()][:2])
        suggestion_data.append([
            i,
            tags_str,
            group.resource_count,
            reason
        ])
    
    print(tabulate(
        suggestion_data,
        headers=["#", "Tags", "Resources", "Reason"],
        tablefmt="grid"
    ))
    
    print(f"\n{Fore.GREEN}Total suggestions: {len(suggestions)}{Style.RESET_ALL}\n")


@cli.command()
@click.option(
    "--region",
    "-r",
    default="us-east-1",
    help="AWS region"
)
@click.option(
    "--tag-key",
    required=True,
    help="Tag key to filter by"
)
@click.option(
    "--tag-value",
    required=True,
    help="Tag value to filter by"
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Preview resources without deleting"
)
@click.option(
    "--yes",
    "-y",
    is_flag=True,
    help="Skip confirmation"
)
def nuke_by_tag(region, tag_key, tag_value, dry_run, yes):
    """Delete resources by tag (e.g., env=dev).
    
    Examples:
    
        # Preview deletion
        aws-nuker nuke-by-tag --tag-key env --tag-value dev --dry-run
        
        # Delete resources
        aws-nuker nuke-by-tag --tag-key env --tag-value dev --yes
    """
    print(f"\n{Fore.CYAN}Finding resources with {tag_key}={tag_value}...{Style.RESET_ALL}\n")
    
    tag_manager = TagManager(region=region)
    resources = tag_manager.get_resources_by_tags({tag_key: tag_value})
    
    if not resources:
        print(f"{Fore.GREEN}No resources found with specified tags{Style.RESET_ALL}")
        return
    
    print(f"{Fore.YELLOW}Found {len(resources)} resources{Style.RESET_ALL}\n")
    
    # Show preview
    preview_data = []
    for resource in resources[:20]:
        preview_data.append([
            resource.get('ResourceType', 'Unknown'),
            resource.get('ARN', 'Unknown')[:70] + "..."
        ])
    
    print(tabulate(
        preview_data,
        headers=["Type", "ARN"],
        tablefmt="grid"
    ))
    
    if len(resources) > 20:
        print(f"\n{Fore.YELLOW}... and {len(resources) - 20} more{Style.RESET_ALL}")
    
    if dry_run:
        print(f"\n{Fore.GREEN}Dry run complete - no resources deleted{Style.RESET_ALL}\n")
        return
    
    # Confirmation
    if not yes:
        print(f"\n{Fore.RED}WARNING: This will delete {len(resources)} resources!{Style.RESET_ALL}")
        confirmation = click.prompt(
            f"{Fore.YELLOW}Type 'DELETE' to proceed{Style.RESET_ALL}",
            type=str
        )
        
        if confirmation != "DELETE":
            print(f"{Fore.GREEN}Operation cancelled{Style.RESET_ALL}")
            return
    
    print(f"\n{Fore.RED}Tag-based deletion would proceed here{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Note: Full implementation requires orchestrator integration{Style.RESET_ALL}\n")


def main():
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()
