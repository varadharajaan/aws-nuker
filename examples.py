#!/usr/bin/env python3
"""
Example usage script for AWS Nuker

This script demonstrates various usage patterns of the AWS Nuker tool.
"""

import subprocess
import sys


def run_command(cmd, description):
    """Run a command and print its description"""
    print(f"\n{'='*80}")
    print(f"Example: {description}")
    print(f"{'='*80}")
    print(f"Command: {' '.join(cmd)}\n")
    
    # For examples, we'll just print the command, not execute it
    # Uncomment the line below to actually execute
    # subprocess.run(cmd)


def main():
    print("""
    AWS Nuker - Example Usage Patterns
    ===================================
    
    This script shows various ways to use AWS Nuker.
    NOTE: These are examples only. Uncomment run_command() calls to execute.
    """)
    
    # Example 1: List all available services
    run_command(
        ['aws-nuker', '--list-services'],
        "List all available AWS services that can be cleaned"
    )
    
    # Example 2: Dry run for EC2 in us-east-1
    run_command(
        ['aws-nuker', '--regions', 'us-east-1', '--services', 'ec2', '--dry-run'],
        "Dry run - see what EC2 instances would be deleted without actually deleting"
    )
    
    # Example 3: Delete EC2 instances in us-east-1
    run_command(
        ['aws-nuker', '--regions', 'us-east-1', '--services', 'ec2'],
        "Delete all EC2 instances in us-east-1 (requires confirmation)"
    )
    
    # Example 4: Delete multiple services
    run_command(
        ['aws-nuker', '--regions', 'us-east-1', '--services', 'ec2,ebs,ebs-snapshots,s3'],
        "Delete EC2, EBS, and S3 resources in us-east-1"
    )
    
    # Example 5: Delete all Lambda resources across multiple regions
    run_command(
        ['aws-nuker', '--regions', 'us-east-1,us-west-2,eu-west-1', '--services', 'lambda,lambda-layers'],
        "Delete all Lambda functions and layers in multiple regions"
    )
    
    # Example 6: Clean up RDS resources
    run_command(
        ['aws-nuker', '--regions', 'us-east-1', '--services', 'rds-instances,rds-clusters,rds-snapshots'],
        "Delete all RDS instances, clusters, and snapshots"
    )
    
    # Example 7: Clean all IAM resources (global)
    run_command(
        ['aws-nuker', '--regions', 'us-east-1', '--services', 'iam-users,iam-roles,iam-policies,iam-groups'],
        "Delete all IAM users, roles, policies, and groups"
    )
    
    # Example 8: Full cleanup in all regions (DANGEROUS!)
    run_command(
        ['aws-nuker', '--regions', 'all', '--services', 'all', '--yes'],
        "DANGER: Delete ALL resources in ALL regions (skip confirmation)"
    )
    
    # Example 9: Clean networking resources (preserves defaults)
    run_command(
        ['aws-nuker', '--regions', 'us-east-1', '--services', 'vpcs,subnets,security-groups'],
        "Delete all non-default VPCs, subnets, and security groups"
    )
    
    # Example 10: Clean container resources
    run_command(
        ['aws-nuker', '--regions', 'us-east-1', '--services', 'ecs-clusters,ecs-tasks,eks,ecr'],
        "Delete all ECS, EKS, and ECR resources"
    )
    
    print(f"\n{'='*80}")
    print("To actually execute these commands, run aws-nuker with the appropriate options.")
    print("Always use --dry-run first to preview changes!")
    print(f"{'='*80}\n")


if __name__ == '__main__':
    main()
