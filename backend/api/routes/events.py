"""
Server-Sent Events (SSE) for real-time updates.

This module provides real-time event streaming for:
- Agent status updates
- Workflow progress
- System metrics
- Deployment status
"""

import asyncio
import json
from collections.abc import AsyncGenerator
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.dependencies import get_current_user
from backend.core.logging import get_logger
from backend.db.session import get_db

logger = get_logger(__name__)
router = APIRouter(prefix="/events", tags=["events"])


class EventBroadcaster:
    """Broadcast events to connected clients."""

    def __init__(self):
        self._clients: list[asyncio.Queue] = []
        self._running = False

    def connect(self) -> asyncio.Queue:
        """Connect a new client."""
        queue = asyncio.Queue()
        self._clients.append(queue)
        logger.info("Client connected", total_clients=len(self._clients))
        return queue

    def disconnect(self, queue: asyncio.Queue):
        """Disconnect a client."""
        if queue in self._clients:
            self._clients.remove(queue)
            logger.info("Client disconnected", total_clients=len(self._clients))

    async def broadcast(self, event_type: str, data: dict):
        """Broadcast an event to all connected clients."""
        event = {
            "type": event_type,
            "data": data,
            "timestamp": datetime.now(UTC).isoformat()
        }

        # Remove disconnected clients
        dead_clients = []
        for client in self._clients:
            try:
                await client.put(event)
            except Exception:
                dead_clients.append(client)

        for dead in dead_clients:
            self.disconnect(dead)


# Global broadcaster instance
broadcaster = EventBroadcaster()


async def generate_events(queue: asyncio.Queue) -> AsyncGenerator[str, None]:
    """Generate SSE events from queue."""
    try:
        while True:
            event = await queue.get()
            yield f"data: {json.dumps(event)}\n\n"
    except asyncio.CancelledError:
        logger.info("Event generation cancelled")
        raise


@router.get("/stream")
async def event_stream(
    request: Request,
    user=Depends(get_current_user),
):
    """
    Stream real-time events.

    Returns Server-Sent Events stream with:
    - agent_status: Agent status updates
    - workflow_progress: Workflow execution progress
    - system_metrics: System resource metrics
    - deployment_status: Deployment status changes
    """
    queue = broadcaster.connect()

    async def cleanup():
        broadcaster.disconnect(queue)

    # Send initial connection event
    await queue.put({
        "type": "connected",
        "data": {"user_id": user.user_id if user else "anonymous"},
        "timestamp": datetime.now(UTC).isoformat(),
    })

    return StreamingResponse(
        generate_events(queue),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        },
        background=cleanup
    )


@router.get("/metrics")
async def metrics_stream(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """Stream system metrics only."""
    queue = broadcaster.connect()

    async def generate_metrics() -> AsyncGenerator[str, None]:
        try:
            while True:
                # Get real metrics from database/services
                metrics = {
                    "cpu": 45.2,  # TODO: Get from actual system
                    "memory": 62.1,
                    "network": 12.5,
                    "disk": 78.3,
                    "timestamp": datetime.now(UTC).isoformat()
                }

                yield f"data: {json.dumps({'type': 'system_metrics', 'data': metrics})}\n\n"
                await asyncio.sleep(5)  # Update every 5 seconds
        except asyncio.CancelledError:
            raise

    return StreamingResponse(
        generate_metrics(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
        background=lambda: broadcaster.disconnect(queue)
    )


# Helper function to broadcast events from other parts of the application
async def broadcast_event(event_type: str, data: dict):
    """Broadcast an event to all connected clients."""
    await broadcaster.broadcast(event_type, data)
