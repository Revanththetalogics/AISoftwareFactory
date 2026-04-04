"""
Collaboration API Routes

Provides REST endpoints for collaboration features including comments, notifications,
teams, and activity logging.
"""

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.api.models import APIResponse
from backend.core.logging import get_logger
from backend.services.collaboration_service import EntityType, User, UserRole, collaboration_service

router = APIRouter(prefix="/collaboration", tags=["Collaboration"])
logger = get_logger(__name__)


class CommentCreate(BaseModel):
    """Comment creation request model."""

    entity_id: str
    entity_type: str
    content: str
    parent_id: str | None = None
    mentions: list[str] | None = None


class CommentUpdate(BaseModel):
    """Comment update request model."""

    content: str | None = None
    mentions: list[str] | None = None


class ReactionAdd(BaseModel):
    """Reaction addition request model."""

    emoji: str


class NotificationMarkRead(BaseModel):
    """Notification mark as read request model."""

    read: bool = True


class TeamCreate(BaseModel):
    """Team creation request model."""

    name: str
    description: str | None = None
    initial_members: list[dict[str, Any]] | None = None


class TeamMemberAdd(BaseModel):
    """Team member addition request model."""

    user_id: str
    username: str
    email: str
    role: str = "member"


@router.post("/comments/", response_model=APIResponse)
async def create_comment(comment_data: CommentCreate):
    """
    Create a new comment on an entity.

    Args:
        comment_data: Comment creation data

    Returns:
        APIResponse with created comment
    """
    try:
        # For demo purposes, using a fixed user ID
        author_id = "user_1"

        comment = await collaboration_service.create_comment(
            entity_id=comment_data.entity_id,
            entity_type=EntityType(comment_data.entity_type),
            author_id=author_id,
            content=comment_data.content,
            parent_id=comment_data.parent_id,
            mentions=comment_data.mentions,
        )

        return APIResponse(success=True, data=comment.__dict__, message="Comment created successfully")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Failed to create comment", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to create comment: {str(e)}")


@router.get("/comments/{entity_type}/{entity_id}", response_model=APIResponse)
async def get_comments(entity_type: str, entity_id: str, limit: int = 50):
    """
    Get comments for an entity.

    Args:
        entity_type: Type of entity (project, task, etc.)
        entity_id: ID of the entity
        limit: Maximum number of comments to return

    Returns:
        APIResponse with list of comments
    """
    try:
        comments = await collaboration_service.get_comments(
            entity_id=entity_id, entity_type=EntityType(entity_type), limit=limit
        )

        comments_data = [comment.__dict__ for comment in comments]

        return APIResponse(success=True, data=comments_data, message=f"Retrieved {len(comments_data)} comments")
    except Exception as e:
        logger.error("Failed to get comments", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get comments: {str(e)}")


@router.put("/comments/{comment_id}", response_model=APIResponse)
async def update_comment(comment_id: str, update_data: CommentUpdate):
    """
    Update an existing comment.

    Args:
        comment_id: ID of the comment to update
        update_data: Comment update data

    Returns:
        APIResponse with updated comment
    """
    try:
        comment = await collaboration_service.update_comment(
            comment_id=comment_id, content=update_data.content, mentions=update_data.mentions
        )

        return APIResponse(success=True, data=comment.__dict__, message="Comment updated successfully")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("Failed to update comment", error=str(e), comment_id=comment_id)
        raise HTTPException(status_code=500, detail=f"Failed to update comment: {str(e)}")


@router.delete("/comments/{comment_id}", response_model=APIResponse)
async def delete_comment(comment_id: str):
    """
    Delete a comment.

    Args:
        comment_id: ID of the comment to delete

    Returns:
        APIResponse confirming deletion
    """
    try:
        success = await collaboration_service.delete_comment(comment_id)

        if success:
            return APIResponse(success=True, message="Comment deleted successfully")
        else:
            raise HTTPException(status_code=404, detail="Comment not found")

    except Exception as e:
        logger.error("Failed to delete comment", error=str(e), comment_id=comment_id)
        raise HTTPException(status_code=500, detail=f"Failed to delete comment: {str(e)}")


@router.post("/comments/{comment_id}/reactions", response_model=APIResponse)
async def add_reaction(comment_id: str, reaction_data: ReactionAdd):
    """
    Add a reaction to a comment.

    Args:
        comment_id: ID of the comment
        reaction_data: Reaction data

    Returns:
        APIResponse with updated comment
    """
    try:
        # For demo purposes, using a fixed user ID
        user_id = "user_2"

        comment = await collaboration_service.add_reaction(
            comment_id=comment_id, user_id=user_id, emoji=reaction_data.emoji
        )

        return APIResponse(success=True, data=comment.__dict__, message="Reaction added successfully")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("Failed to add reaction", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to add reaction: {str(e)}")


@router.get("/notifications/", response_model=APIResponse)
async def get_user_notifications(unread_only: bool = False, limit: int = 20):
    """
    Get notifications for the current user.

    Args:
        unread_only: Whether to return only unread notifications
        limit: Maximum number of notifications to return

    Returns:
        APIResponse with list of notifications
    """
    try:
        # For demo purposes, using a fixed user ID
        user_id = "user_2"

        notifications = await collaboration_service.get_user_notifications(
            user_id=user_id, unread_only=unread_only, limit=limit
        )

        notifications_data = [notif.__dict__ for notif in notifications]

        return APIResponse(
            success=True, data=notifications_data, message=f"Retrieved {len(notifications_data)} notifications"
        )
    except Exception as e:
        logger.error("Failed to get notifications", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get notifications: {str(e)}")


@router.put("/notifications/{notification_id}/read", response_model=APIResponse)
async def mark_notification_read(notification_id: str, read_data: NotificationMarkRead):
    """
    Mark a notification as read/unread.

    Args:
        notification_id: ID of the notification
        read_data: Read status data

    Returns:
        APIResponse confirming update
    """
    try:
        success = await collaboration_service.mark_notification_read(notification_id)

        if success:
            status = "read" if read_data.read else "unread"
            return APIResponse(success=True, message=f"Notification marked as {status}")
        else:
            raise HTTPException(status_code=404, detail="Notification not found")

    except Exception as e:
        logger.error("Failed to mark notification", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to mark notification: {str(e)}")


@router.post("/teams/", response_model=APIResponse)
async def create_team(team_data: TeamCreate):
    """
    Create a new team.

    Args:
        team_data: Team creation data

    Returns:
        APIResponse with created team
    """
    try:
        # For demo purposes, using a fixed owner ID
        owner_id = "user_1"

        # Convert initial members to User objects
        initial_members = []
        if team_data.initial_members:
            for member_data in team_data.initial_members:
                user = User(
                    id=member_data["id"],
                    username=member_data["username"],
                    email=member_data["email"],
                    role=UserRole(member_data.get("role", "member")),
                )
                initial_members.append(user)

        team = await collaboration_service.create_team(
            name=team_data.name, owner_id=owner_id, description=team_data.description, initial_members=initial_members
        )

        team_dict = team.__dict__.copy()
        team_dict["members"] = [member.__dict__ for member in team.members]

        return APIResponse(success=True, data=team_dict, message=f"Team '{team_data.name}' created successfully")
    except Exception as e:
        logger.error("Failed to create team", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to create team: {str(e)}")


@router.post("/teams/{team_id}/members", response_model=APIResponse)
async def add_team_member(team_id: str, member_data: TeamMemberAdd):
    """
    Add a member to a team.

    Args:
        team_id: ID of the team
        member_data: Member data

    Returns:
        APIResponse with updated team
    """
    try:
        user = User(
            id=member_data.user_id,
            username=member_data.username,
            email=member_data.email,
            role=UserRole(member_data.role),
        )

        team = await collaboration_service.add_team_member(team_id, user)

        team_dict = team.__dict__.copy()
        team_dict["members"] = [member.__dict__ for member in team.members]

        return APIResponse(success=True, data=team_dict, message=f"Added {member_data.username} to team")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Failed to add team member", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to add team member: {str(e)}")


@router.get("/teams/", response_model=APIResponse)
async def list_teams():
    """
    List all teams.

    Returns:
        APIResponse with list of teams
    """
    try:
        teams = list(collaboration_service.teams.values())
        teams_data = []

        for team in teams:
            team_dict = team.__dict__.copy()
            team_dict["members"] = [member.__dict__ for member in team.members]
            teams_data.append(team_dict)

        return APIResponse(success=True, data=teams_data, message=f"Retrieved {len(teams_data)} teams")
    except Exception as e:
        logger.error("Failed to list teams", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to list teams: {str(e)}")


@router.get("/activities/recent", response_model=APIResponse)
async def get_recent_activities(limit: int = 50):
    """
    Get recent activities across the system.

    Args:
        limit: Maximum number of activities to return

    Returns:
        APIResponse with list of activities
    """
    try:
        activities = await collaboration_service.get_recent_activities(limit)
        activities_data = [activity.__dict__ for activity in activities]

        return APIResponse(
            success=True, data=activities_data, message=f"Retrieved {len(activities_data)} recent activities"
        )
    except Exception as e:
        logger.error("Failed to get recent activities", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get recent activities: {str(e)}")


@router.get("/activities/{entity_type}/{entity_id}", response_model=APIResponse)
async def get_entity_activities(entity_type: str, entity_id: str, limit: int = 20):
    """
    Get activities for a specific entity.

    Args:
        entity_type: Type of entity
        entity_id: ID of the entity
        limit: Maximum number of activities to return

    Returns:
        APIResponse with list of activities
    """
    try:
        activities = await collaboration_service.get_entity_activity(
            entity_id=entity_id, entity_type=EntityType(entity_type), limit=limit
        )

        activities_data = [activity.__dict__ for activity in activities]

        return APIResponse(
            success=True, data=activities_data, message=f"Retrieved {len(activities_data)} activities for entity"
        )
    except Exception as e:
        logger.error("Failed to get entity activities", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get entity activities: {str(e)}")


@router.get("/stats", response_model=APIResponse)
async def get_collaboration_stats():
    """
    Get collaboration statistics.

    Returns:
        APIResponse with collaboration statistics
    """
    try:
        stats = {
            "total_comments": len(collaboration_service.comments),
            "total_notifications": len(collaboration_service.notifications),
            "total_teams": len(collaboration_service.teams),
            "total_activities": len(collaboration_service.activity_logs),
            "connected_users": await collaboration_service.get_connected_users_count(),
            "unread_notifications": len([n for n in collaboration_service.notifications.values() if not n.read]),
        }

        return APIResponse(success=True, data=stats, message="Retrieved collaboration statistics")
    except Exception as e:
        logger.error("Failed to get collaboration stats", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get collaboration stats: {str(e)}")


@router.post("/connect", response_model=APIResponse)
async def connect_user():
    """
    Register user as connected (for real-time features).

    Returns:
        APIResponse confirming connection
    """
    try:
        # For demo purposes, using a fixed user ID
        user_id = "user_1"

        await collaboration_service.connect_user(user_id)

        return APIResponse(success=True, message="User connected successfully")
    except Exception as e:
        logger.error("Failed to connect user", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to connect user: {str(e)}")


@router.post("/disconnect", response_model=APIResponse)
async def disconnect_user():
    """
    Unregister user as connected.

    Returns:
        APIResponse confirming disconnection
    """
    try:
        # For demo purposes, using a fixed user ID
        user_id = "user_1"

        await collaboration_service.disconnect_user(user_id)

        return APIResponse(success=True, message="User disconnected successfully")
    except Exception as e:
        logger.error("Failed to disconnect user", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to disconnect user: {str(e)}")
