"""
Horizontal Scaling and Load Balancing

Provides load distribution, auto-scaling policies, and cluster management
for distributed backend services.
"""

import asyncio
import hashlib
import json
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any

from fastapi import Response
from pydantic import BaseModel

from backend.core.config import get_settings
from backend.core.logging import get_logger
from backend.core.resources import resource_manager

logger = get_logger(__name__)
settings = get_settings()


class ScalingPolicy(str, Enum):
    """Scaling policy types."""

    LEADER_ELECTION = "leader_election"
    ROUND_ROBIN = "round_robin"
    CONSISTENT_HASH = "consistent_hash"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"


class NodeStatus(str, Enum):
    """Node status states."""

    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DRAINING = "draining"
    MAINTENANCE = "maintenance"


@dataclass
class ClusterNode:
    """Represents a node in the cluster."""

    node_id: str
    host: str
    port: int
    status: NodeStatus = NodeStatus.HEALTHY
    weight: int = 1
    last_heartbeat: float = 0
    metrics: dict[str, Any] = None

    def __post_init__(self):
        if self.metrics is None:
            self.metrics = {}

    @property
    def address(self) -> str:
        """Get node address."""
        return f"{self.host}:{self.port}"

    def is_healthy(self) -> bool:
        """Check if node is healthy."""
        return self.status == NodeStatus.HEALTHY and time.time() - self.last_heartbeat < settings.HEARTBEAT_TIMEOUT


class LoadBalancer:
    """Distributed load balancer with multiple algorithms."""

    def __init__(self, policy: ScalingPolicy = ScalingPolicy.CONSISTENT_HASH):
        self.policy = policy
        self.nodes: dict[str, ClusterNode] = {}
        self._node_ring: list[tuple[int, str]] = []  # For consistent hashing
        self._current_index = 0
        self._lock = asyncio.Lock()

    async def add_node(self, node: ClusterNode):
        """Add a node to the cluster."""
        async with self._lock:
            self.nodes[node.node_id] = node
            if self.policy == ScalingPolicy.CONSISTENT_HASH:
                self._build_consistent_hash_ring()
            logger.info(f"Node added: {node.node_id} ({node.address})")

    async def remove_node(self, node_id: str):
        """Remove a node from the cluster."""
        async with self._lock:
            if node_id in self.nodes:
                del self.nodes[node_id]
                if self.policy == ScalingPolicy.CONSISTENT_HASH:
                    self._build_consistent_hash_ring()
                logger.info(f"Node removed: {node_id}")

    async def update_node_status(self, node_id: str, status: NodeStatus):
        """Update node status."""
        async with self._lock:
            if node_id in self.nodes:
                self.nodes[node_id].status = status
                logger.info(f"Node {node_id} status updated to {status}")

    def get_next_node(self, key: str | None = None) -> ClusterNode | None:
        """Get next node based on load balancing policy."""
        healthy_nodes = [node for node in self.nodes.values() if node.is_healthy()]

        if not healthy_nodes:
            return None

        if self.policy == ScalingPolicy.ROUND_ROBIN:
            return self._round_robin(healthy_nodes)
        elif self.policy == ScalingPolicy.WEIGHTED_ROUND_ROBIN:
            return self._weighted_round_robin(healthy_nodes)
        elif self.policy == ScalingPolicy.CONSISTENT_HASH and key:
            return self._consistent_hash(healthy_nodes, key)
        else:
            # Default to round robin
            return self._round_robin(healthy_nodes)

    def _round_robin(self, nodes: list[ClusterNode]) -> ClusterNode:
        """Round-robin selection."""
        node = nodes[self._current_index % len(nodes)]
        self._current_index = (self._current_index + 1) % len(nodes)
        return node

    def _weighted_round_robin(self, nodes: list[ClusterNode]) -> ClusterNode:
        """Weighted round-robin selection."""
        # Simple weighted selection - could be improved with more sophisticated algorithms
        total_weight = sum(node.weight for node in nodes)
        choice = hash(str(time.time())) % total_weight

        current_weight = 0
        for node in nodes:
            current_weight += node.weight
            if choice < current_weight:
                return node

        return nodes[0]  # Fallback

    def _consistent_hash(self, nodes: list[ClusterNode], key: str) -> ClusterNode:
        """Consistent hashing selection."""
        if not self._node_ring:
            return nodes[0]

        # Hash the key
        key_hash = int(hashlib.md5(key.encode(), usedforsecurity=False).hexdigest(), 16)

        # Find the node responsible for this hash
        for position, node_id in self._node_ring:
            if key_hash <= position:
                return self.nodes[node_id]

        # Wrap around to the first node
        return self.nodes[self._node_ring[0][1]]

    def _build_consistent_hash_ring(self):
        """Build consistent hash ring."""
        self._node_ring = []

        for node_id, node in self.nodes.items():
            if node.is_healthy():
                # Add multiple virtual nodes for better distribution
                for i in range(settings.VIRTUAL_NODES_PER_SERVER):
                    virtual_key = f"{node_id}:{i}"
                    position = int(hashlib.md5(virtual_key.encode(), usedforsecurity=False).hexdigest(), 16)
                    self._node_ring.append((position, node_id))

        # Sort by position
        self._node_ring.sort()

    def get_cluster_stats(self) -> dict[str, Any]:
        """Get cluster statistics."""
        healthy_nodes = [node for node in self.nodes.values() if node.is_healthy()]

        return {
            "total_nodes": len(self.nodes),
            "healthy_nodes": len(healthy_nodes),
            "unhealthy_nodes": len(self.nodes) - len(healthy_nodes),
            "policy": self.policy.value,
            "nodes": [
                {
                    "node_id": node.node_id,
                    "address": node.address,
                    "status": node.status.value,
                    "weight": node.weight,
                    "last_heartbeat": node.last_heartbeat,
                    "metrics": node.metrics,
                }
                for node in self.nodes.values()
            ],
        }


class ClusterManager:
    """Manages cluster membership and coordination."""

    def __init__(self):
        self.load_balancer = LoadBalancer(ScalingPolicy.CONSISTENT_HASH)
        self._heartbeat_task = None
        self._discovery_task = None
        self._is_leader = False
        self._leader_lock = asyncio.Lock()
        self._cluster_lock = asyncio.Lock()

    async def initialize(self):
        """Initialize cluster manager."""
        # Register this node
        local_node = ClusterNode(
            node_id=settings.NODE_ID, host=settings.HOST, port=settings.PORT, weight=settings.NODE_WEIGHT
        )
        await self.load_balancer.add_node(local_node)

        # Start background tasks
        self._heartbeat_task = asyncio.create_task(self._send_heartbeats())
        self._discovery_task = asyncio.create_task(self._discover_nodes())

        logger.info("Cluster manager initialized")

    async def shutdown(self):
        """Shutdown cluster manager."""
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
        if self._discovery_task:
            self._discovery_task.cancel()

        logger.info("Cluster manager shutdown")

    async def _send_heartbeats(self):
        """Send periodic heartbeats to announce node availability."""
        while True:
            try:
                await self._announce_presence()
                await asyncio.sleep(settings.HEARTBEAT_INTERVAL)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Heartbeat error: {e}")
                await asyncio.sleep(settings.HEARTBEAT_INTERVAL)

    async def _discover_nodes(self):
        """Discover other nodes in the cluster."""
        while True:
            try:
                await self._scan_cluster()
                await asyncio.sleep(settings.DISCOVERY_INTERVAL)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Discovery error: {e}")
                await asyncio.sleep(settings.DISCOVERY_INTERVAL)

    async def _announce_presence(self):
        """Announce this node's presence to the cluster."""
        try:
            redis = resource_manager.get_redis_client()

            node_info = {
                "node_id": settings.NODE_ID,
                "host": settings.HOST,
                "port": settings.PORT,
                "weight": settings.NODE_WEIGHT,
                "timestamp": time.time(),
                "status": NodeStatus.HEALTHY.value,
            }

            # Publish heartbeat to Redis
            channel = f"cluster:heartbeat:{settings.NODE_ID}"
            await redis.publish(channel, json.dumps(node_info))

            # Set ephemeral key for discovery
            key = f"cluster:nodes:{settings.NODE_ID}"
            await redis.setex(
                key,
                settings.HEARTBEAT_TIMEOUT * 2,  # Double timeout for safety
                json.dumps(node_info),
            )

            # Update local node heartbeat
            if settings.NODE_ID in self.load_balancer.nodes:
                self.load_balancer.nodes[settings.NODE_ID].last_heartbeat = time.time()

        except Exception as e:
            logger.error(f"Failed to announce presence: {e}")

    async def _scan_cluster(self):
        """Scan for other nodes in the cluster."""
        try:
            redis = resource_manager.get_redis_client()

            # Get all node keys
            pattern = "cluster:nodes:*"
            keys = await redis.keys(pattern)

            for key in keys:
                try:
                    node_data = await redis.get(key)
                    if node_data:
                        node_info = json.loads(node_data)

                        node_id = node_info["node_id"]

                        # Skip self
                        if node_id == settings.NODE_ID:
                            continue

                        # Create or update node
                        node = ClusterNode(
                            node_id=node_id,
                            host=node_info["host"],
                            port=node_info["port"],
                            weight=node_info.get("weight", 1),
                            last_heartbeat=node_info["timestamp"],
                            status=NodeStatus(node_info["status"]),
                        )

                        await self.load_balancer.add_node(node)

                except Exception as e:
                    logger.error(f"Failed to process node {key}: {e}")

        except Exception as e:
            logger.error(f"Failed to scan cluster: {e}")

    async def elect_leader(self) -> str:
        """Elect cluster leader using Redis."""
        async with self._leader_lock:
            try:
                redis = resource_manager.get_redis_client()

                # Try to acquire leadership lock
                lock_key = "cluster:leader:lock"
                lock_value = settings.NODE_ID
                lock_ttl = settings.LEADER_LOCK_TTL

                acquired = await redis.set(
                    lock_key,
                    lock_value,
                    nx=True,  # Only set if not exists
                    ex=lock_ttl,
                )

                if acquired:
                    self._is_leader = True
                    logger.info(f"Node {settings.NODE_ID} elected as leader")
                    return settings.NODE_ID
                else:
                    # Get current leader
                    current_leader = await redis.get(lock_key)
                    if current_leader:
                        return current_leader.decode()
                    return "unknown"

            except Exception as e:
                logger.error(f"Leader election failed: {e}")
                return "unknown"

    def is_leader(self) -> bool:
        """Check if this node is the leader."""
        return self._is_leader

    def get_load_balancer(self) -> LoadBalancer:
        """Get the load balancer instance."""
        return self.load_balancer


# Global cluster manager instance
cluster_manager = ClusterManager()


# Middleware for request routing
class ClusterRoutingMiddleware:
    """Middleware for routing requests in a clustered environment."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Extract routing key from request
        routing_key = self._extract_routing_key(scope)

        # Get target node
        target_node = cluster_manager.load_balancer.get_next_node(routing_key)

        if not target_node or target_node.node_id == settings.NODE_ID:
            # Route to local node
            await self.app(scope, receive, send)
        else:
            # Route to remote node (would require proxy implementation)
            await self._proxy_request(scope, receive, send, target_node)

    def _extract_routing_key(self, scope: dict) -> str:
        """Extract routing key from request scope."""
        # Use path as routing key for consistent hashing
        return scope.get("path", "")

    async def _proxy_request(self, scope, receive, send, target_node):
        """Proxy request to target node (simplified implementation)."""
        # This is a simplified proxy - in production, you'd use a proper
        # HTTP client or reverse proxy

        response = Response(
            content=json.dumps({"error": "Request routed to another node", "target_node": target_node.address}),
            status_code=503,
        )

        await response(scope, receive, send)


# API Models
class ClusterStats(BaseModel):
    """Cluster statistics response model."""

    total_nodes: int
    healthy_nodes: int
    unhealthy_nodes: int
    policy: str
    nodes: list[dict[str, Any]]


class LeaderInfo(BaseModel):
    """Leader information response model."""

    is_leader: bool
    leader_id: str
    node_id: str


# Dependency for getting cluster stats
async def get_cluster_stats() -> ClusterStats:
    """Get current cluster statistics."""
    stats = cluster_manager.load_balancer.get_cluster_stats()
    return ClusterStats(**stats)


async def get_leader_info() -> LeaderInfo:
    """Get leader information."""
    leader_id = await cluster_manager.elect_leader()
    return LeaderInfo(is_leader=cluster_manager.is_leader(), leader_id=leader_id, node_id=settings.NODE_ID)
