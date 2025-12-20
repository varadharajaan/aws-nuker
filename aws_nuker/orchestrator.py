"""Main orchestrator for AWS Nuker."""

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Any

from .config import NukerConfig
from .logger import get_logger
from .registry import get_handler


class AWSNuker:
    """Main orchestrator for AWS resource cleanup."""

    def __init__(self, config: NukerConfig):
        """
        Initialize AWS Nuker.

        Args:
            config: Configuration object
        """
        self.config = config
        self.logger = get_logger()
        self.results: List[Dict[str, Any]] = []

    def execute(self) -> Dict[str, Any]:
        """
        Execute the cleanup operation.

        Returns:
            Summary of execution results
        """
        start_time = time.time()

        self.logger.info("=" * 80)
        self.logger.info("AWS Nuker - Starting cleanup operation")
        self.logger.info("=" * 80)
        self.logger.info(f"Regions: {', '.join(self.config.regions)}")
        self.logger.info(f"Services: {len(self.config.services)} selected")
        self.logger.info(f"Dry Run: {self.config.dry_run}")
        self.logger.info(f"Force: {self.config.force}")
        self.logger.info("=" * 80)

        # Execute cleanup
        if self.config.parallel_execution:
            self._execute_parallel()
        else:
            self._execute_sequential()

        # Calculate summary
        elapsed_time = time.time() - start_time
        summary = self._generate_summary(elapsed_time)

        self.logger.info("=" * 80)
        self.logger.info("AWS Nuker - Cleanup operation completed")
        self.logger.info("=" * 80)
        self._log_summary(summary)

        return summary

    def _execute_sequential(self):
        """Execute cleanup sequentially."""
        for region in self.config.regions:
            for service in sorted(self.config.services):
                try:
                    handler = get_handler(
                        service,
                        region,
                        dry_run=self.config.dry_run,
                        force=self.config.force,
                    )
                    result = handler.nuke_all()
                    self.results.append(result)
                except ValueError as e:
                    self.logger.warning(str(e))
                except Exception as e:
                    self.logger.error(
                        f"Error processing {service} in {region}: {str(e)}"
                    )

    def _execute_parallel(self):
        """Execute cleanup in parallel."""
        tasks = []
        for region in self.config.regions:
            for service in self.config.services:
                tasks.append((service, region))

        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            future_to_task = {
                executor.submit(
                    self._process_service, service, region
                ): (service, region)
                for service, region in tasks
            }

            for future in as_completed(future_to_task):
                service, region = future_to_task[future]
                try:
                    result = future.result()
                    if result:
                        self.results.append(result)
                except Exception as e:
                    self.logger.error(
                        f"Error processing {service} in {region}: {str(e)}"
                    )

    def _process_service(self, service: str, region: str) -> Dict[str, Any]:
        """
        Process a single service in a region.

        Args:
            service: Service name
            region: Region name

        Returns:
            Result dictionary
        """
        try:
            handler = get_handler(
                service,
                region,
                dry_run=self.config.dry_run,
                force=self.config.force,
            )
            return handler.nuke_all()
        except ValueError as e:
            self.logger.warning(str(e))
            return None
        except Exception as e:
            self.logger.error(
                f"Error processing {service} in {region}: {str(e)}"
            )
            return None

    def _generate_summary(self, elapsed_time: float) -> Dict[str, Any]:
        """
        Generate execution summary.

        Args:
            elapsed_time: Total elapsed time in seconds

        Returns:
            Summary dictionary
        """
        total_resources = sum(r["total"] for r in self.results)
        total_deleted = sum(r["deleted"] for r in self.results)
        total_failed = sum(r["failed"] for r in self.results)
        total_skipped = sum(r["skipped"] for r in self.results)

        all_errors = []
        for result in self.results:
            all_errors.extend(result.get("errors", []))

        return {
            "elapsed_time": elapsed_time,
            "regions": self.config.regions,
            "services_processed": len(self.results),
            "total_resources": total_resources,
            "total_deleted": total_deleted,
            "total_failed": total_failed,
            "total_skipped": total_skipped,
            "errors": all_errors,
            "dry_run": self.config.dry_run,
        }

    def _log_summary(self, summary: Dict[str, Any]):
        """
        Log execution summary.

        Args:
            summary: Summary dictionary
        """
        self.logger.info(f"Total execution time: {summary['elapsed_time']:.2f}s")
        self.logger.info(f"Regions processed: {len(summary['regions'])}")
        self.logger.info(f"Services processed: {summary['services_processed']}")
        self.logger.info(f"Total resources found: {summary['total_resources']}")
        self.logger.info(f"Resources deleted: {summary['total_deleted']}")
        self.logger.info(f"Resources failed: {summary['total_failed']}")
        self.logger.info(f"Resources skipped: {summary['total_skipped']}")

        if summary["errors"]:
            self.logger.warning(f"Total errors: {len(summary['errors'])}")

        if summary["dry_run"]:
            self.logger.info("NOTE: This was a DRY RUN - no actual deletions occurred")
