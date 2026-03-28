"""
Scaling and Load Balancing API Routes

Provides endpoints for cluster management, load balancing, and scaling operations.
"""


from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.api.models import APIResponse
from backend.core.logging import get_logger
from backend.core.scaling import NodeStatus, ScalingPolicy, cluster_manager, get_cluster_stats, get_leader_info

router = APIRouter(prefix="/scaling", tags=["Scaling & Load Balancing"])
logger = get_logger(__name__)

class ScalingConfig(BaseModel):
    """Scaling configuration model."""
    policy: ScalingPolicy
    min_nodes: int = 1
    max_nodes: int = 10
    target_cpu_utilization: float = 70.0
    scale_up_threshold: float = 80.0
    scale_down_threshold: float = 30.0

class NodeAction(BaseModel):
    """Node action request model."""
    node_id: str
    action: str  # "add", "remove", "drain", "maintain"
    weight: int = 1

@router.get("/cluster/stats", response_model=APIResponse)
async def get_scaling_stats():
    """
    Get cluster scaling statistics.
    
    Returns:
        APIResponse with cluster statistics
    """
    try:
        stats = await get_cluster_stats()

        return APIResponse(
            success=True,
            data=stats.dict(),
            message="Cluster statistics retrieved successfully"
        )
    except Exception as e:
        logger.error("Failed to get scaling stats", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

@router.get("/leader", response_model=APIResponse)
async def get_leader_status():
    """
    Get cluster leader information.
    
    Returns:
        APIResponse with leader information
    """
    try:
        leader_info = await get_leader_info()

        return APIResponse(
            success=True,
            data=leader_info.dict(),
            message="Leader information retrieved successfully"
        )
    except Exception as e:
        logger.error("Failed to get leader status", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get leader status: {str(e)}")

@router.post("/nodes/action", response_model=APIResponse)
async def perform_node_action(action: NodeAction):
    """
    Perform action on a cluster node.
    
    Args:
        action: Node action request
        
    Returns:
        APIResponse confirming action
    """
    try:
        if action.action == "drain":
            await cluster_manager.load_balancer.update_node_status(
                action.node_id,
                NodeStatus.DRAINING
            )
        elif action.action == "maintain":
            await cluster_manager.load_balancer.update_node_status(
                action.node_id,
                NodeStatus.MAINTENANCE
            )
        elif action.action == "add":
            # In a real implementation, this would involve provisioning
            # For now, we'll just log the action
            logger.info(f"Node add action requested for {action.node_id}")
        elif action.action == "remove":
            await cluster_manager.load_balancer.remove_node(action.node_id)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown action: {action.action}")

        return APIResponse(
            success=True,
            message=f"Action '{action.action}' performed on node {action.node_id}"
        )
    except Exception as e:
        logger.error("Failed to perform node action", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to perform action: {str(e)}")

@router.get("/policies", response_model=APIResponse)
async def get_scaling_policies():
    """
    Get available scaling policies.
    
    Returns:
        APIResponse with policy information
    """
    try:
        policies = {
            "available_policies": [policy.value for policy in ScalingPolicy],
            "current_policy": cluster_manager.load_balancer.policy.value,
            "descriptions": {
                "leader_election": "Single leader handles requests, others standby",
                "round_robin": "Distribute requests evenly across all nodes",
                "consistent_hash": "Hash-based routing for session affinity",
                "weighted_round_robin": "Round-robin with node weights"
            }
        }

        return APIResponse(
            success=True,
            data=policies,
            message="Scaling policies retrieved successfully"
        )
    except Exception as e:
        logger.error("Failed to get scaling policies", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get policies: {str(e)}")

@router.post("/policies/change", response_model=APIResponse)
async def change_scaling_policy(policy: ScalingPolicy):
    """
    Change the current scaling policy.
    
    Args:
        policy: New scaling policy
        
    Returns:
        APIResponse confirming policy change
    """
    try:
        cluster_manager.load_balancer.policy = policy
        logger.info(f"Scaling policy changed to {policy.value}")

        return APIResponse(
            success=True,
            message=f"Scaling policy changed to {policy.value}"
        )
    except Exception as e:
        logger.error("Failed to change scaling policy", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to change policy: {str(e)}")

@router.get("/health", response_model=APIResponse)
async def get_scaling_health():
    """
    Get scaling system health status.
    
    Returns:
        APIResponse with health information
    """
    try:
        stats = await get_cluster_stats()
        leader_info = await get_leader_info()

        # Determine overall health
        healthy_ratio = stats.healthy_nodes / max(stats.total_nodes, 1)
        is_healthy = (
            healthy_ratio >= 0.8 and  # At least 80% nodes healthy
            stats.total_nodes > 0 and  # Has nodes
            leader_info.leader_id != "unknown"  # Has leader
        )

        health_info = {
            "status": "healthy" if is_healthy else "degraded",
            "healthy_nodes_ratio": round(healthy_ratio, 2),
            "has_leader": leader_info.leader_id != "unknown",
            "total_nodes": stats.total_nodes,
            "healthy_nodes": stats.healthy_nodes,
            "current_leader": leader_info.leader_id,
            "is_local_leader": leader_info.is_leader
        }

        return APIResponse(
            success=is_healthy,
            data=health_info,
            message="Scaling health check completed"
        )
    except Exception as e:
        logger.error("Failed to perform scaling health check", error=str(e))
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@router.post("/nodes/weight", response_model=APIResponse)
async def update_node_weight(node_id: str, weight: int):
    """
    Update node weight for weighted load balancing.
    
    Args:
        node_id: Node identifier
        weight: New weight value (1-100)
        
    Returns:
        APIResponse confirming weight update
    """
    try:
        if weight < 1 or weight > 100:
            raise HTTPException(status_code=400, detail="Weight must be between 1 and 100")

        if node_id in cluster_manager.load_balancer.nodes:
            cluster_manager.load_balancer.nodes[node_id].weight = weight
            logger.info(f"Node {node_id} weight updated to {weight}")

            return APIResponse(
                success=True,
                message=f"Node {node_id} weight updated to {weight}"
            )
        else:
            raise HTTPException(status_code=404, detail=f"Node {node_id} not found")

    except Exception as e:
        logger.error("Failed to update node weight", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to update weight: {str(e)}")

@router.get("/recommendations", response_model=APIResponse)
async def get_scaling_recommendations():
    """
    Get scaling recommendations based on current load.
    
    Returns:
        APIResponse with scaling recommendations
    """
    try:
        stats = await get_cluster_stats()
        health = await get_scaling_health()

        recommendations = []

        # Check if we need more nodes
        if stats.healthy_nodes < 3:
            recommendations.append({
                "type": "scale_up",
                "priority": "high",
                "reason": "Low node count",
                "recommended_nodes": max(3 - stats.healthy_nodes, 1)
            })

        # Check node health distribution
        if health.data["healthy_nodes_ratio"] < 0.8:
            recommendations.append({
                "type": "investigate",
                "priority": "medium",
                "reason": "Poor node health ratio",
                "action": "Check unhealthy nodes"
            })

        # Check if we have too many nodes
        if stats.healthy_nodes > 10:
            recommendations.append({
                "type": "scale_down",
                "priority": "low",
                "reason": "Excess capacity",
                "recommended_nodes": max(stats.healthy_nodes - 8, 0)
            })

        return APIResponse(
            success=True,
            data={
                "recommendations": recommendations,
                "current_state": {
                    "nodes": stats.healthy_nodes,
                    "health_ratio": health.data["healthy_nodes_ratio"],
                    "leader_present": health.data["has_leader"]
                }
            },
            message="Scaling recommendations generated"
        )
    except Exception as e:
        logger.error("Failed to generate scaling recommendations", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to generate recommendations: {str(e)}")
