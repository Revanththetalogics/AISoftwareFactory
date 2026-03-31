"""
Real-time Monitoring API Routes

Provides WebSocket endpoints and REST APIs for real-time monitoring
of system metrics and infrastructure status.
"""

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, WebSocket
from pydantic import BaseModel

from backend.api.models import APIResponse
from backend.core.logging import get_logger
from backend.monitoring.realtime import MonitorEventType, MonitoringEventTrigger, realtime_monitor

router = APIRouter(prefix="/realtime", tags=["Real-time Monitoring"])
logger = get_logger(__name__)

class MonitoringSubscription(BaseModel):
    """Monitoring subscription request model."""
    topics: list[str]
    client_id: str | None = None

class EventFilter(BaseModel):
    """Event filter criteria."""
    event_types: list[MonitorEventType] | None = None
    severity_levels: list[str] | None = None
    time_range_minutes: int | None = 60

class TriggerAlertRequest(BaseModel):
    """Request model for triggering an alert event."""
    alert_name: str
    severity: str
    details: dict[str, Any] = {}

class TriggerServiceStatusRequest(BaseModel):
    """Request model for triggering a service status change event."""
    service_name: str
    old_status: str
    new_status: str

@router.websocket("/monitor")
async def realtime_monitoring_websocket(websocket: WebSocket, client_id: str = None):
    """
    WebSocket endpoint for real-time monitoring.

    Args:
        websocket: WebSocket connection
        client_id: Optional client identifier
    """
    if client_id is None:
        client_id = str(uuid.uuid4())

    await realtime_monitoring_endpoint(websocket, client_id)

@router.post("/subscribe", response_model=APIResponse)
async def subscribe_to_monitoring(subscription: MonitoringSubscription):
    """
    Subscribe to real-time monitoring topics.

    Args:
        subscription: Subscription details

    Returns:
        APIResponse confirming subscription
    """
    try:
        # In a real implementation, this would manage subscriptions
        # For now, we'll just log the subscription
        logger.info(f"Client subscribed to topics: {subscription.topics}")

        return APIResponse(
            success=True,
            message=f"Subscribed to {len(subscription.topics)} topics"
        )
    except Exception as e:
        logger.error("Failed to process subscription", error=str(e))
        raise HTTPException(status_code=500, detail=f"Subscription failed: {str(e)}")

@router.post("/unsubscribe", response_model=APIResponse)
async def unsubscribe_from_monitoring(subscription: MonitoringSubscription):
    """
    Unsubscribe from real-time monitoring topics.

    Args:
        subscription: Unsubscription details

    Returns:
        APIResponse confirming unsubscription
    """
    try:
        logger.info(f"Client unsubscribed from topics: {subscription.topics}")

        return APIResponse(
            success=True,
            message=f"Unsubscribed from {len(subscription.topics)} topics"
        )
    except Exception as e:
        logger.error("Failed to process unsubscription", error=str(e))
        raise HTTPException(status_code=500, detail=f"Unsubscription failed: {str(e)}")

@router.get("/snapshot", response_model=APIResponse)
async def get_current_snapshot():
    """
    Get current system snapshot.

    Returns:
        APIResponse with current system state
    """
    try:
        snapshot = await realtime_monitor._collect_system_snapshot()

        return APIResponse(
            success=True,
            data=snapshot,
            message="Current system snapshot retrieved"
        )
    except Exception as e:
        logger.error("Failed to get system snapshot", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get snapshot: {str(e)}")

@router.get("/events/recent", response_model=APIResponse)
async def get_recent_events(limit: int = 100, filter: EventFilter = Depends()):
    """
    Get recent monitoring events.

    Args:
        limit: Maximum number of events to return
        filter: Event filtering criteria

    Returns:
        APIResponse with recent events
    """
    try:
        events = realtime_monitor.get_recent_events(limit)

        # Apply filters if specified
        if filter.event_types:
            events = [e for e in events if e.event_type in filter.event_types]

        if filter.severity_levels:
            events = [e for e in events if e.severity in filter.severity_levels]

        # Convert events to serializable format
        serialized_events = []
        for event in events:
            serialized_events.append({
                "type": event.event_type.value,
                "timestamp": event.timestamp.isoformat(),
                "data": event.data,
                "severity": event.severity
            })

        return APIResponse(
            success=True,
            data={
                "events": serialized_events,
                "total_count": len(serialized_events),
                "filters_applied": {
                    "event_types": [t.value for t in filter.event_types] if filter.event_types else None,
                    "severity_levels": filter.severity_levels,
                    "time_range_minutes": filter.time_range_minutes
                }
            },
            message=f"Retrieved {len(serialized_events)} recent events"
        )
    except Exception as e:
        logger.error("Failed to get recent events", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get events: {str(e)}")

@router.post("/events/trigger/alert", response_model=APIResponse)
async def trigger_alert_event(request: TriggerAlertRequest):
    """
    Manually trigger an alert event.

    Args:
        request: Alert trigger request with alert_name, severity, and details

    Returns:
        APIResponse confirming alert trigger
    """
    try:
        await MonitoringEventTrigger.trigger_alert(request.alert_name, request.severity, request.details)

        return APIResponse(
            success=True,
            message=f"Alert '{request.alert_name}' triggered with severity '{request.severity}'"
        )
    except Exception as e:
        logger.error("Failed to trigger alert", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to trigger alert: {str(e)}")

@router.post("/events/trigger/service-status", response_model=APIResponse)
async def trigger_service_status_event(request: TriggerServiceStatusRequest):
    """
    Manually trigger a service status change event.

    Args:
        request: Service status trigger request with service_name, old_status, new_status

    Returns:
        APIResponse confirming event trigger
    """
    try:
        await MonitoringEventTrigger.trigger_service_status_change(
            request.service_name, request.old_status, request.new_status
        )

        return APIResponse(
            success=True,
            message=f"Service status change triggered for '{request.service_name}'"
        )
    except Exception as e:
        logger.error("Failed to trigger service status event", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to trigger event: {str(e)}")

@router.get("/connections", response_model=APIResponse)
async def get_active_connections():
    """
    Get information about active WebSocket connections.

    Returns:
        APIResponse with connection information
    """
    try:
        # In a real implementation, this would return actual connection data
        connection_info = {
            "active_connections": len(realtime_monitor.active_connections),
            "subscribed_clients": len(realtime_monitor.subscribed_clients),
            "broadcast_status": "running" if realtime_monitor._is_running else "stopped",
            "event_buffer_size": len(realtime_monitor._event_buffer)
        }

        return APIResponse(
            success=True,
            data=connection_info,
            message="Connection information retrieved"
        )
    except Exception as e:
        logger.error("Failed to get connection information", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get connections: {str(e)}")

@router.post("/control/start", response_model=APIResponse)
async def start_monitoring_broadcast():
    """
    Start real-time monitoring broadcast.

    Returns:
        APIResponse confirming start
    """
    try:
        await realtime_monitor.start_monitoring()

        return APIResponse(
            success=True,
            message="Real-time monitoring broadcast started"
        )
    except Exception as e:
        logger.error("Failed to start monitoring", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to start monitoring: {str(e)}")

@router.post("/control/stop", response_model=APIResponse)
async def stop_monitoring_broadcast():
    """
    Stop real-time monitoring broadcast.

    Returns:
        APIResponse confirming stop
    """
    try:
        await realtime_monitor.stop_monitoring()

        return APIResponse(
            success=True,
            message="Real-time monitoring broadcast stopped"
        )
    except Exception as e:
        logger.error("Failed to stop monitoring", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to stop monitoring: {str(e)}")

@router.get("/metrics/live", response_model=APIResponse)
async def get_live_metrics():
    """
    Get live metrics stream information.

    Returns:
        APIResponse with live metrics configuration
    """
    try:
        metrics_config = {
            "update_intervals": {
                "frequent_metrics": f"{realtime_monitor.METRIC_UPDATE_INTERVAL}s",
                "system_metrics": f"{realtime_monitor.SYSTEM_METRIC_INTERVAL}s",
                "cluster_metrics": f"{realtime_monitor.CLUSTER_METRIC_INTERVAL}s"
            },
            "available_metrics": [
                "cpu_percent",
                "memory_percent",
                "disk_percent",
                "network_io",
                "database_connections",
                "redis_connections",
                "processes",
                "cluster_status"
            ],
            "broadcast_status": "active" if realtime_monitor._is_running else "inactive"
        }

        return APIResponse(
            success=True,
            data=metrics_config,
            message="Live metrics configuration retrieved"
        )
    except Exception as e:
        logger.error("Failed to get live metrics info", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get metrics info: {str(e)}")

# WebSocket endpoint function (imported from realtime module)
async def realtime_monitoring_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for real-time monitoring."""
    await realtime_monitor.connect(websocket, client_id)
