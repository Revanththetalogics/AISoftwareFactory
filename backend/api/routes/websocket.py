"""
WebSocket Routes for Real-Time Updates.

This module provides WebSocket endpoints for real-time communication.
"""

import json
from datetime import datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from backend.api.dependencies import get_websocket_user
from backend.core.logging import get_logger
from backend.db.session import get_db_context
from backend.services.database_services import DatabaseProjectService, DatabaseWorkflowService

logger = get_logger(__name__)
router = APIRouter(prefix="/ws", tags=["websocket"])

# Service instances for real DB queries
_project_svc = DatabaseProjectService()
_workflow_svc = DatabaseWorkflowService()

# Connection managers for different channels
_project_connections: dict[str, set[WebSocket]] = {}
_workflow_connections: dict[str, set[WebSocket]] = {}
_global_connections: set[WebSocket] = set()


class ConnectionManager:
    """Manage WebSocket connections."""

    def __init__(self):
        self.active_connections: set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)

    async def broadcast(self, message: dict):
        """Broadcast message to all connections."""
        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.add(connection)

        # Clean up disconnected clients
        for conn in disconnected:
            self.active_connections.discard(conn)


# Global connection manager
global_manager = ConnectionManager()


@router.websocket("/global")
async def global_websocket(websocket: WebSocket):
    """
    Global WebSocket for system-wide updates.

    Receives:
        - subscribe: Subscribe to update types
        - ping: Keep connection alive

    Sends:
        - system_status: System health updates
        - notification: General notifications
    """
    user = await get_websocket_user(websocket)

    # SECURITY: Reject unauthenticated connections
    if user is None:
        await websocket.close(code=4001, reason="Authentication required")
        logger.warning(
            "WebSocket connection closed: authentication required",
            channel="global",
            client=websocket.client.host if websocket.client else "unknown",
        )
        return

    await global_manager.connect(websocket)
    _global_connections.add(websocket)

    logger.info(
        "WebSocket connected",
        channel="global",
        user=user.user_id if user else "anonymous",
    )

    try:
        await websocket.send_json(
            {
                "type": "connected",
                "payload": {
                    "channel": "global",
                    "user_id": user.user_id if user else "anonymous",
                    "timestamp": datetime.now().isoformat(),
                },
            }
        )

        while True:
            try:
                data = await websocket.receive_json()
                message_type = data.get("type")

                if message_type == "ping":
                    await websocket.send_json(
                        {
                            "type": "pong",
                            "payload": {"timestamp": datetime.now().isoformat()},
                        }
                    )

                elif message_type == "subscribe":
                    topics = data.get("payload", {}).get("topics", [])
                    await websocket.send_json(
                        {
                            "type": "subscribed",
                            "payload": {"topics": topics},
                        }
                    )

                else:
                    await websocket.send_json(
                        {
                            "type": "error",
                            "payload": {"message": f"Unknown message type: {message_type}"},
                        }
                    )

            except json.JSONDecodeError:
                await websocket.send_json(
                    {
                        "type": "error",
                        "payload": {"message": "Invalid JSON"},
                    }
                )

    except WebSocketDisconnect:
        global_manager.disconnect(websocket)
        _global_connections.discard(websocket)
        logger.info(
            "WebSocket disconnected",
            channel="global",
            user=user.user_id if user else "anonymous",
        )


@router.websocket("/projects/{project_id}")
async def project_websocket(websocket: WebSocket, project_id: str):
    """
    Project-specific WebSocket for real-time project updates.

    Receives:
        - subscribe: Subscribe to project events
        - get_status: Request current project status

    Sends:
        - phase_update: Current phase changes
        - progress_update: Progress percentage updates
        - log_message: Real-time log messages
        - completion: Project completion notification
    """
    user = await get_websocket_user(websocket)

    # SECURITY: Reject unauthenticated connections
    if user is None:
        await websocket.close(code=4001, reason="Authentication required")
        logger.warning(
            "WebSocket connection closed: authentication required",
            channel="project",
            project_id=project_id,
            client=websocket.client.host if websocket.client else "unknown",
        )
        return

    await websocket.accept()

    # Add to project-specific connections
    if project_id not in _project_connections:
        _project_connections[project_id] = set()
    _project_connections[project_id].add(websocket)

    logger.info(
        "WebSocket connected",
        channel="project",
        project_id=project_id,
        user=user.user_id if user else "anonymous",
    )

    try:
        await websocket.send_json(
            {
                "type": "connected",
                "payload": {
                    "channel": f"project:{project_id}",
                    "project_id": project_id,
                    "timestamp": datetime.now().isoformat(),
                },
            }
        )

        while True:
            try:
                data = await websocket.receive_json()
                message_type = data.get("type")

                if message_type == "ping":
                    await websocket.send_json(
                        {
                            "type": "pong",
                            "payload": {"timestamp": datetime.now().isoformat()},
                        }
                    )

                elif message_type == "get_status":
                    # Query real project status from database
                    async with get_db_context() as db:
                        project = await _project_svc.get_project(project_id, db=db)
                    if project:
                        await websocket.send_json(
                            {
                                "type": "status",
                                "payload": {
                                    "project_id": project_id,
                                    "status": project.status,
                                    "current_phase": project.current_phase,
                                    "progress_percent": project.progress_percent,
                                },
                            }
                        )
                    else:
                        await websocket.send_json(
                            {
                                "type": "error",
                                "payload": {"message": f"Project {project_id} not found"},
                            }
                        )

                else:
                    await websocket.send_json(
                        {
                            "type": "error",
                            "payload": {"message": f"Unknown message type: {message_type}"},
                        }
                    )

            except json.JSONDecodeError:
                await websocket.send_json(
                    {
                        "type": "error",
                        "payload": {"message": "Invalid JSON"},
                    }
                )

    except WebSocketDisconnect:
        _project_connections[project_id].discard(websocket)
        if not _project_connections[project_id]:
            del _project_connections[project_id]
        logger.info(
            "WebSocket disconnected",
            channel="project",
            project_id=project_id,
            user=user.user_id if user else "anonymous",
        )


@router.websocket("/workflows/{workflow_id}")
async def workflow_websocket(websocket: WebSocket, workflow_id: str):
    """
    Workflow-specific WebSocket for execution updates.

    Receives:
        - subscribe: Subscribe to workflow events
        - get_logs: Request recent logs

    Sends:
        - step_started: Step execution started
        - step_completed: Step execution completed
        - log_output: Real-time log output
        - status_change: Workflow status changes
    """
    user = await get_websocket_user(websocket)

    # SECURITY: Reject unauthenticated connections
    if user is None:
        await websocket.close(code=4001, reason="Authentication required")
        logger.warning(
            "WebSocket connection closed: authentication required",
            channel="workflow",
            workflow_id=workflow_id,
            client=websocket.client.host if websocket.client else "unknown",
        )
        return

    await websocket.accept()

    # Add to workflow-specific connections
    if workflow_id not in _workflow_connections:
        _workflow_connections[workflow_id] = set()
    _workflow_connections[workflow_id].add(websocket)

    logger.info(
        "WebSocket connected",
        channel="workflow",
        workflow_id=workflow_id,
        user=user.user_id if user else "anonymous",
    )

    try:
        await websocket.send_json(
            {
                "type": "connected",
                "payload": {
                    "channel": f"workflow:{workflow_id}",
                    "workflow_id": workflow_id,
                    "timestamp": datetime.now().isoformat(),
                },
            }
        )

        while True:
            try:
                data = await websocket.receive_json()
                message_type = data.get("type")

                if message_type == "ping":
                    await websocket.send_json(
                        {
                            "type": "pong",
                            "payload": {"timestamp": datetime.now().isoformat()},
                        }
                    )

                elif message_type == "get_logs":
                    # Query real workflow logs from database
                    async with get_db_context() as db:
                        workflow = await _workflow_svc.get_workflow(workflow_id, db=db)
                    payload_logs: list = []
                    if workflow and workflow.context:
                        payload_logs = workflow.context.get("logs", [])
                    await websocket.send_json(
                        {
                            "type": "logs",
                            "payload": {
                                "workflow_id": workflow_id,
                                "logs": payload_logs,
                            },
                        }
                    )

                else:
                    await websocket.send_json(
                        {
                            "type": "error",
                            "payload": {"message": f"Unknown message type: {message_type}"},
                        }
                    )

            except json.JSONDecodeError:
                await websocket.send_json(
                    {
                        "type": "error",
                        "payload": {"message": "Invalid JSON"},
                    }
                )

    except WebSocketDisconnect:
        _workflow_connections[workflow_id].discard(websocket)
        if not _workflow_connections[workflow_id]:
            del _workflow_connections[workflow_id]
        logger.info(
            "WebSocket disconnected",
            channel="workflow",
            workflow_id=workflow_id,
            user=user.user_id if user else "anonymous",
        )


async def broadcast_project_update(project_id: str, message: dict):
    """Broadcast update to all project subscribers."""
    if project_id in _project_connections:
        disconnected = set()
        for ws in _project_connections[project_id]:
            try:
                await ws.send_json(message)
            except Exception:
                disconnected.add(ws)

        for ws in disconnected:
            _project_connections[project_id].discard(ws)


async def broadcast_workflow_update(workflow_id: str, message: dict):
    """Broadcast update to all workflow subscribers."""
    if workflow_id in _workflow_connections:
        disconnected = set()
        for ws in _workflow_connections[workflow_id]:
            try:
                await ws.send_json(message)
            except Exception:
                disconnected.add(ws)

        for ws in disconnected:
            _workflow_connections[workflow_id].discard(ws)
