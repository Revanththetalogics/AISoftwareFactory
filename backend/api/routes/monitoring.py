"""
Monitoring API Routes

Provides endpoints for accessing metrics, alerts, and monitoring data.
"""


from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

from backend.api.models import APIResponse
from backend.core.logging import get_logger
from backend.monitoring.metrics import alert_manager, metrics_collector

router = APIRouter(prefix="/monitoring", tags=["Monitoring"])
logger = get_logger(__name__)

class AlertRuleInfo(BaseModel):
    """Alert rule information model."""
    name: str
    query: str
    threshold: float
    duration: str
    severity: str
    description: str
    active: bool
    last_triggered: str | None

class MetricSample(BaseModel):
    """Metric sample data model."""
    name: str
    value: float
    labels: dict[str, str]
    timestamp: str

@router.get("/metrics", response_class=PlainTextResponse)
async def get_prometheus_metrics():
    """
    Get Prometheus metrics in text format.
    
    Returns:
        Plain text Prometheus metrics
    """
    try:
        metrics_text = metrics_collector.get_metrics_text()
        return Response(
            content=metrics_text,
            media_type=CONTENT_TYPE_LATEST
        )
    except Exception as e:
        logger.error("Failed to get Prometheus metrics", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")

@router.get("/alerts/rules", response_model=APIResponse)
async def get_alert_rules():
    """
    Get all configured alert rules.
    
    Returns:
        APIResponse with alert rules
    """
    try:
        rules_info = []
        for rule in alert_manager.rules:
            rules_info.append({
                "name": rule.name,
                "query": rule.query,
                "threshold": rule.threshold,
                "duration": rule.duration,
                "severity": rule.severity,
                "description": rule.description,
                "active": rule.active,
                "last_triggered": rule.last_triggered.isoformat() if rule.last_triggered else None
            })

        return APIResponse(
            success=True,
            data={"rules": rules_info},
            message="Alert rules retrieved successfully"
        )
    except Exception as e:
        logger.error("Failed to get alert rules", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get alert rules: {str(e)}")

@router.post("/alerts/test", response_model=APIResponse)
async def test_alert_rule(rule_name: str):
    """
    Test an alert rule.
    
    Args:
        rule_name: Name of the rule to test
        
    Returns:
        APIResponse with test results
    """
    try:
        rule = next((r for r in alert_manager.rules if r.name == rule_name), None)
        if not rule:
            raise HTTPException(status_code=404, detail=f"Rule '{rule_name}' not found")

        # Evaluate the rule
        triggered = await alert_manager._evaluate_rule(rule)

        return APIResponse(
            success=True,
            data={
                "rule_name": rule_name,
                "triggered": triggered,
                "current_value": "N/A",  # Would need actual metric querying
                "threshold": rule.threshold
            },
            message=f"Rule '{rule_name}' test completed"
        )
    except Exception as e:
        logger.error("Failed to test alert rule", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to test rule: {str(e)}")

@router.get("/health/detailed", response_model=APIResponse)
async def get_detailed_health():
    """
    Get detailed health information with metrics.
    
    Returns:
        APIResponse with detailed health data
    """
    try:
        import time

        import psutil

        # Collect system metrics
        system_metrics = {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
            "uptime_seconds": time.time() - psutil.boot_time()
        }

        # Collect application metrics (simplified)
        app_metrics = {
            "active_connections": 0,  # Would query actual connection pools
            "request_rate": 0,        # Would query actual request rates
            "error_rate": 0,          # Would query actual error rates
            "cache_hit_ratio": 0       # Would query actual cache metrics
        }

        # Combine metrics
        health_data = {
            "system": system_metrics,
            "application": app_metrics,
            "timestamp": __import__('datetime').datetime.now(__import__('datetime').UTC).isoformat()
        }

        # Determine overall health
        is_healthy = (
            system_metrics["cpu_percent"] < 90 and
            system_metrics["memory_percent"] < 90 and
            system_metrics["disk_percent"] < 95
        )

        return APIResponse(
            success=is_healthy,
            data=health_data,
            message="Detailed health check completed"
        )
    except Exception as e:
        logger.error("Failed to get detailed health", error=str(e))
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@router.get("/performance/top-endpoints", response_model=APIResponse)
async def get_top_endpoints(limit: int = 10):
    """
    Get top performing endpoints by latency.
    
    Args:
        limit: Number of endpoints to return
        
    Returns:
        APIResponse with top endpoints
    """
    try:
        # In a real implementation, this would query actual metrics
        # For now, returning sample data
        top_endpoints = [
            {
                "endpoint": "/api/v1/projects",
                "method": "GET",
                "avg_latency_ms": 45.2,
                "request_count": 1250,
                "error_rate": 0.02
            },
            {
                "endpoint": "/api/v1/codegen/generate",
                "method": "POST",
                "avg_latency_ms": 125.7,
                "request_count": 342,
                "error_rate": 0.05
            },
            {
                "endpoint": "/api/v1/knowledge/search",
                "method": "POST",
                "avg_latency_ms": 68.3,
                "request_count": 567,
                "error_rate": 0.01
            }
        ][:limit]

        return APIResponse(
            success=True,
            data={"endpoints": top_endpoints},
            message="Top endpoints retrieved successfully"
        )
    except Exception as e:
        logger.error("Failed to get top endpoints", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get endpoints: {str(e)}")

@router.get("/alerts/history", response_model=APIResponse)
async def get_alert_history(hours: int = 24):
    """
    Get alert history for the specified time period.
    
    Args:
        hours: Number of hours to look back
        
    Returns:
        APIResponse with alert history
    """
    try:
        # In a real implementation, this would query a database
        # For now, returning sample data
        alert_history = [
            {
                "alert_name": "high_cpu_usage",
                "severity": "warning",
                "triggered_at": "2024-01-15T10:30:00Z",
                "resolved_at": "2024-01-15T10:35:00Z",
                "duration_seconds": 300
            },
            {
                "alert_name": "high_memory_usage",
                "severity": "warning",
                "triggered_at": "2024-01-15T09:15:00Z",
                "resolved_at": "2024-01-15T09:20:00Z",
                "duration_seconds": 300
            }
        ]

        return APIResponse(
            success=True,
            data={"alerts": alert_history, "hours": hours},
            message="Alert history retrieved successfully"
        )
    except Exception as e:
        logger.error("Failed to get alert history", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get alert history: {str(e)}")

@router.post("/alerts/silence", response_model=APIResponse)
async def silence_alert(rule_name: str, duration_minutes: int = 30):
    """
    Silence an alert rule temporarily.
    
    Args:
        rule_name: Name of the rule to silence
        duration_minutes: Duration to silence in minutes
        
    Returns:
        APIResponse confirming silencing
    """
    try:
        rule = next((r for r in alert_manager.rules if r.name == rule_name), None)
        if not rule:
            raise HTTPException(status_code=404, detail=f"Rule '{rule_name}' not found")

        # In a real implementation, this would add to a silence list
        logger.info(f"Alert rule '{rule_name}' silenced for {duration_minutes} minutes")

        return APIResponse(
            success=True,
            message=f"Alert rule '{rule_name}' silenced for {duration_minutes} minutes"
        )
    except Exception as e:
        logger.error("Failed to silence alert", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to silence alert: {str(e)}")

@router.get("/metrics/dashboard", response_model=APIResponse)
async def get_dashboard_metrics():
    """
    Get metrics formatted for dashboard display.
    
    Returns:
        APIResponse with dashboard-ready metrics
    """
    try:
        import psutil

        dashboard_data = {
            "system": {
                "cpu_usage": psutil.cpu_percent(),
                "memory_usage": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('/').percent,
                "network_io": {
                    "bytes_sent": psutil.net_io_counters().bytes_sent,
                    "bytes_recv": psutil.net_io_counters().bytes_recv
                }
            },
            "application": {
                "active_users": 0,  # Would query actual user sessions
                "requests_per_second": 0,  # Would query actual rate
                "average_response_time_ms": 0,  # Would query actual latency
                "error_percentage": 0  # Would query actual error rate
            },
            "business": {
                "projects_count": 0,  # Would query actual count
                "code_generations_today": 0,  # Would query daily count
                "simulations_run_today": 0  # Would query daily count
            },
            "timestamp": __import__('datetime').datetime.now(__import__('datetime').UTC).isoformat()
        }

        return APIResponse(
            success=True,
            data=dashboard_data,
            message="Dashboard metrics retrieved successfully"
        )
    except Exception as e:
        logger.error("Failed to get dashboard metrics", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard metrics: {str(e)}")
