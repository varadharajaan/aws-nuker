"""ElastiCache resource handler."""

from typing import List, Dict, Any
from botocore.exceptions import ClientError

from ..base_handler import ResourceHandler


class ElastiCacheHandler(ResourceHandler):
    """Handler for ElastiCache clusters (Redis and Memcached)."""

    @property
    def service_name(self) -> str:
        return "elasticache"

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all ElastiCache clusters."""
        elasticache = self.session.client("elasticache")
        resources = []

        try:
            # List cache clusters
            clusters_response = elasticache.describe_cache_clusters()
            for cluster in clusters_response.get("CacheClusters", []):
                resources.append({
                    "id": cluster["CacheClusterId"],
                    "name": cluster["CacheClusterId"],
                    "type": "cache_cluster",
                    "engine": cluster.get("Engine", ""),
                })

            # List replication groups (Redis)
            repl_groups_response = elasticache.describe_replication_groups()
            for rg in repl_groups_response.get("ReplicationGroups", []):
                resources.append({
                    "id": rg["ReplicationGroupId"],
                    "name": rg["ReplicationGroupId"],
                    "type": "replication_group",
                })

        except ClientError as e:
            self.logger.error(f"Error listing ElastiCache clusters: {str(e)}")

        return resources

    def delete_resource(self, resource: Dict[str, Any]) -> bool:
        """Delete an ElastiCache resource."""
        elasticache = self.session.client("elasticache")
        resource_type = resource.get("type")
        resource_id = resource.get("id")

        try:
            if resource_type == "cache_cluster":
                elasticache.delete_cache_cluster(
                    CacheClusterId=resource_id
                )
                return True
            elif resource_type == "replication_group":
                elasticache.delete_replication_group(
                    ReplicationGroupId=resource_id,
                    RetainPrimaryCluster=False
                )
                return True

            return False

        except ClientError as e:
            self.logger.error(
                f"Error deleting ElastiCache {resource_type} {resource_id}: {str(e)}"
            )
            return False
