"""
Real-time Monitoring System

Provides WebSocket-based real-time monitoring of system metrics,
performance data, and infrastructure status updates.
"""

import asyncio
import json
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from typing import Any

import psutil
from backend.core.logging import get_logger
from backend.core.resources import resource_manager
from backend.core.scaling import cluster_manager
from fastapi import WebSocket, WebSocketDisconnect

logger = get_logger(__name__)

class MonitorEventType(str, Enum):
    """Types of monitoring events."""
    METRIC_UPDATE = "metric_update"
    ALERT_TRIGGERED = "alert_triggered"
    SERVICE_STATUS_CHANGE = "service_status_change"
    CLUSTER_TOPOLOGY_CHANGE = "cluster_topology_change"
    PERFORMANCE_DEGRADATION = "performance_degradation"

@dataclass
class MonitorEvent:
    """Represents a monitoring event."""
    event_type: MonitorEventType
    timestamp: datetime
    data: dict[str, Any]
    severity: str = "info"

class RealtimeMonitor:
    """Real-time monitoring system with WebSocket broadcasting."""

    def __init__(self):
        self.active_connections: set[WebSocket] = set()
        self.subscribed_clients: dict[str, set[WebSocket]] = {}
        self._broadcast_task = None
        self._is_running = False

        # Monitoring intervals
        self.METRIC_UPDATE_INTERVAL = 1.0  # seconds
        self.SYSTEM_METRIC_INTERVAL = 5.0  # seconds
        self.CLUSTER_METRIC_INTERVAL = 10.0  # seconds

        # Event buffers
        self._event_buffer: list[MonitorEvent] = []
        self._max_buffer_size = 1000

    async def connect(self, websocket: WebSocket, client_id: str):
        """Connect a new WebSocket client."""
        await websocket.accept()
        self.active_connections.add(websocket)

        # Initialize client subscriptions
        if client_id not in self.subscribed_clients:
            self.subscribed_clients[client_id] = set()
        self.subscribed_clients[client_id].add(websocket)

        logger.info(f"Client {client_id} connected to realtime monitoring")

        try:
            # Send initial connection confirmation
            await self._send_event(websocket, MonitorEvent(
                event_type=MonitorEventType.METRIC_UPDATE,
                timestamp=datetime.now(UTC),
                data={"message": "Connected to realtime monitoring", "client_id": client_id},
                severity="info"
            ))

            # Handle incoming messages
            while True:
                data = await websocket.receive_text()
                await self._handle_client_message(websocket, client_id, data)

        except WebSocketDisconnect:
            await self.disconnect(websocket, client_id)
        except Exception as e:
            logger.error(f"Error handling client {client_id}: {e}")
            await self.disconnect(websocket, client_id)

    async def disconnect(self, websocket: WebSocket, client_id: str):
        """Disconnect a WebSocket client."""
        self.active_connections.discard(websocket)
        if client_id in self.subscribed_clients:
            self.subscribed_clients[client_id].discard(websocket)
            if not self.subscribed_clients[client_id]:
                del self.subscribed_clients[client_id]

        logger.info(f"Client {client_id} disconnected from realtime monitoring")

    async def _handle_client_message(self, websocket: WebSocket, client_id: str, message: str):
        """Handle messages from connected clients."""
        try:
            data = json.loads(message)
            action = data.get("action")

            if action == "subscribe":
                topics = data.get("topics", [])
                await self._handle_subscription(websocket, client_id, topics)
            elif action == "unsubscribe":
                topics = data.get("topics", [])
                await self._handle_unsubscription(websocket, client_id, topics)
            elif action == "get_snapshot":
                await self._send_current_snapshot(websocket)
            else:
                await self._send_error(websocket, f"Unknown action: {action}")

        except json.JSONDecodeError:
            await self._send_error(websocket, "Invalid JSON message")
        except Exception as e:
            logger.error(f"Error handling client message: {e}")
            await self._send_error(websocket, str(e))

    async def _handle_subscription(self, websocket: WebSocket, client_id: str, topics: list[str]):
        """Handle subscription requests."""
        # For simplicity, we'll treat all subscriptions the same way
        # In a real implementation, you might have topic-based filtering
        response = {
            "type": "subscription_confirmed",
            "topics": topics,
            "timestamp": datetime.now(UTC).isoformat()
        }
        await websocket.send_text(json.dumps(response))

    async def _handle_unsubscription(self, websocket: WebSocket, client_id: str, topics: list[str]):
        """Handle unsubscription requests."""
        response = {
            "type": "unsubscription_confirmed",
            "topics": topics,
            "timestamp": datetime.now(UTC).isoformat()
        }
        await websocket.send_text(json.dumps(response))

    async def _send_current_snapshot(self, websocket: WebSocket):
        """Send current system snapshot to client."""
        try:
            snapshot = await self._collect_system_snapshot()
            await self._send_event(websocket, MonitorEvent(
                event_type=MonitorEventType.METRIC_UPDATE,
                timestamp=datetime.now(UTC),
                data=snapshot,
                severity="info"
            ))
        except Exception as e:
            await self._send_error(websocket, f"Failed to collect snapshot: {e}")

    async def start_monitoring(self):
        """Start the real-time monitoring broadcast."""
        if self._is_running:
            return

        self._is_running = True
        self._broadcast_task = asyncio.create_task(self._broadcast_loop())
        logger.info("Real-time monitoring started")

    async def stop_monitoring(self):
        """Stop the real-time monitoring broadcast."""
        self._is_running = False
        if self._broadcast_task:
            self._broadcast_task.cancel()
            try:
                await self._broadcast_task
            except asyncio.CancelledError:
                pass
        logger.info("Real-time monitoring stopped")

    async def _broadcast_loop(self):
        """Main broadcasting loop."""
        last_system_update = 0
        last_cluster_update = 0

        while self._is_running:
            try:
                current_time = time.time()

                # Collect and broadcast frequent metrics
                if current_time - last_system_update >= self.METRIC_UPDATE_INTERVAL:
                    await self._broadcast_frequent_metrics()
                    last_system_update = current_time

                # Collect and broadcast system metrics
                if current_time - last_system_update >= self.SYSTEM_METRIC_INTERVAL:
                    await self._broadcast_system_metrics()
                    last_system_update = current_time

                # Collect and broadcast cluster metrics
                if current_time - last_cluster_update >= self.CLUSTER_METRIC_INTERVAL:
                    await self._broadcast_cluster_metrics()
                    last_cluster_update = current_time

                await asyncio.sleep(0.1)  # Small delay to prevent busy looping

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Broadcast loop error: {e}")
                await asyncio.sleep(1)

    async def _broadcast_frequent_metrics(self):
        """Broadcast frequently updated metrics."""
        try:
            # Collect CPU and memory metrics
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()

            event_data = {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "timestamp": datetime.now(UTC).isoformat()
            }

            event = MonitorEvent(
                event_type=MonitorEventType.METRIC_UPDATE,
                timestamp=datetime.now(UTC),
                data=event_data,
                severity="info"
            )

            await self._broadcast_event(event)

        except Exception as e:
            logger.error(f"Failed to broadcast frequent metrics: {e}")

    async def _broadcast_system_metrics(self):
        """Broadcast comprehensive system metrics."""
        try:
            snapshot = await self._collect_system_snapshot()

            event = MonitorEvent(
                event_type=MonitorEventType.METRIC_UPDATE,
                timestamp=datetime.now(UTC),
                data=snapshot,
                severity="info"
            )

            await self._broadcast_event(event)

        except Exception as e:
            logger.error(f"Failed to broadcast system metrics: {e}")

    async def _broadcast_cluster_metrics(self):
        """Broadcast cluster topology and status metrics."""
        try:
            cluster_stats = cluster_manager.load_balancer.get_cluster_stats()
            leader_info = await cluster_manager.elect_leader()

            event_data = {
                "cluster_stats": cluster_stats,
                "leader_info": {
                    "is_leader": cluster_manager.is_leader(),
                    "leader_id": leader_info,
                    "node_id": "current_node_id"  # Would get actual node ID
                },
                "timestamp": datetime.now(UTC).isoformat()
            }

            event = MonitorEvent(
                event_type=MonitorEventType.CLUSTER_TOPOLOGY_CHANGE,
                timestamp=datetime.now(UTC),
                data=event_data,
                severity="info"
            )

            await self._broadcast_event(event)

        except Exception as e:
            logger.error(f"Failed to broadcast cluster metrics: {e}")

    async def _collect_system_snapshot(self) -> dict[str, Any]:
        """Collect a comprehensive system snapshot."""
        try:
            # System metrics
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            net_io = psutil.net_io_counters()

            # Resource manager metrics
            resource_metrics = resource_manager.get_metrics()
            resource_health = await resource_manager.health_check()

            # Process information
            top_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    top_processes.append({
                        "pid": proc.info['pid'],
                        "name": proc.info['name'],
                        "cpu_percent": proc.info['cpu_percent'] or 0,
                        "memory_percent": proc.info['memory_percent'] or 0
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            # Sort and limit processes
            top_processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
            top_processes = top_processes[:10]

            return {
                "system": {
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "disk_percent": (disk.used / disk.total) * 100,
                    "network_io": {
                        "bytes_sent": net_io.bytes_sent,
                        "bytes_recv": net_io.bytes_recv
                    },
                    "boot_time": datetime.fromtimestamp(psutil.boot_time(), UTC).isoformat(),
                    "uptime_seconds": time.time() - psutil.boot_time()
                },
                "resources": {
                    "database_connections": resource_metrics.get("db_connections_active", 0),
                    "redis_connections": resource_metrics.get("redis_connections_active", 0),
                    "database_health": resource_health.get("database", {}).get("status", "unknown"),
                    "redis_health": resource_health.get("redis", {}).get("status", "unknown")
                },
                "processes": top_processes,
                "timestamp": datetime.now(UTC).isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to collect system snapshot: {e}")
            return {"error": str(e), "timestamp": datetime.now(UTC).isoformat()}

    async def _broadcast_event(self, event: MonitorEvent):
        """Broadcast event to all connected clients."""
        # Add to buffer
        self._event_buffer.append(event)
        if len(self._event_buffer) > self._max_buffer_size:
            self._event_buffer.pop(0)

        # Broadcast to all connections
        disconnected = set()
        for websocket in self.active_connections.copy():
            try:
                await self._send_event(websocket, event)
            except Exception as e:
                logger.error(f"Failed to send event to client: {e}")
                disconnected.add(websocket)

        # Remove disconnected clients
        self.active_connections -= disconnected

    async def _send_event(self, websocket: WebSocket, event: MonitorEvent):
        """Send a single event to a WebSocket."""
        message = {
            "type": event.event_type.value,
            "timestamp": event.timestamp.isoformat(),
            "data": event.data,
            "severity": event.severity
        }
        await websocket.send_text(json.dumps(message))

    async def _send_error(self, websocket: WebSocket, error_message: str):
        """Send an error message to a WebSocket."""
        error_event = MonitorEvent(
            event_type=MonitorEventType.METRIC_UPDATE,  # Using metric update for errors
            timestamp=datetime.now(UTC),
            data={"error": error_message},
            severity="error"
        )
        await self._send_event(websocket, error_event)

    def add_event(self, event: MonitorEvent):
        """Add an event to the buffer (for external event sources)."""
        self._event_buffer.append(event)
        if len(self._event_buffer) > self._max_buffer_size:
            self._event_buffer.pop(0)

    def get_recent_events(self, limit: int = 100) -> list[MonitorEvent]:
        """Get recent events from the buffer."""
        return self._event_buffer[-limit:] if self._event_buffer else []

# Global realtime monitor instance
realtime_monitor = RealtimeMonitor()

# WebSocket endpoint for real-time monitoring
async def realtime_monitoring_endpoint(websocket: WebSocket, client_id: str = "anonymous"):
    """
    WebSocket endpoint for real-time monitoring.
    
    Clients can subscribe to different types of metrics and receive
    real-time updates.
    """
    await realtime_monitor.connect(websocket, client_id)

# API for triggering events
class MonitoringEventTrigger:
    """Utility for triggering monitoring events from other parts of the system."""

    @staticmethod
    async def trigger_alert(alert_name: str, severity: str, details: dict[str, Any]):
        """Trigger an alert event."""
        event = MonitorEvent(
            event_type=MonitorEventType.ALERT_TRIGGERED,
            timestamp=datetime.now(UTC),
            data={
                "alert_name": alert_name,
                "severity": severity,
                "details": details
            },
            severity=severity
        )
        realtime_monitor.add_event(event)

    @staticmethod
    async def trigger_service_status_change(service_name: str, old_status: str, new_status: str):
        """Trigger a service status change event."""
        event = MonitorEvent(
            event_type=MonitorEventType.SERVICE_STATUS_CHANGE,
            timestamp=datetime.now(UTC),
            data={
                "service_name": service_name,
                "old_status": old_status,
                "new_status": new_status
            },
            severity="warning" if new_status == "unhealthy" else "info"
        )
        realtime_monitor.add_event(event)

    @staticmethod
    async def trigger_performance_degradation(metric_name: str, value: float, threshold: float):
        """Trigger a performance degradation event."""
        event = MonitorEvent(
            event_type=MonitorEventType.PERFORMANCE_DEGRADATION,
            timestamp=datetime.now(UTC),
            data={
                "metric_name": metric_name,
                "value": value,
                "threshold": threshold
            },
            severity="warning"
        )
        realtime_monitor.add_event(event)

# Start monitoring when module is imported
async def initialize_realtime_monitoring():
    """Initialize and start real-time monitoring."""
    await realtime_monitor.start_monitoring()
    logger.info("Real-time monitoring initialized")

# Cleanup function
async def cleanup_realtime_monitoring():
    """Cleanup real-time monitoring resources."""
    await realtime_monitor.stop_monitoring()
    logger.info("Real-time monitoring cleaned up")
