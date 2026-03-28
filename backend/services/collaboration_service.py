"""
Collaboration Features Service

Provides real-time collaboration capabilities including comments, mentions, 
notifications, and team workflow management.
"""

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from backend.core.logging import get_logger

logger = get_logger(__name__)


class EntityType(str, Enum):
    """Types of entities that can be commented on."""
    PROJECT = "project"
    TASK = "task"
    DOCUMENT = "document"
    CODE = "code"
    DESIGN = "design"


class NotificationType(str, Enum):
    """Types of notifications."""
    COMMENT = "comment"
    MENTION = "mention"
    ASSIGNMENT = "assignment"
    STATUS_CHANGE = "status_change"
    DEADLINE = "deadline"


class UserRole(str, Enum):
    """User roles in collaboration context."""
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


@dataclass
class User:
    """Represents a user in the collaboration system."""
    id: str
    username: str
    email: str
    avatar_url: str | None = None
    role: UserRole = UserRole.MEMBER


@dataclass
class Comment:
    """Represents a comment on an entity."""
    id: str
    entity_id: str
    entity_type: EntityType
    author_id: str
    content: str
    created_at: str
    updated_at: str
    parent_id: str | None = None
    mentions: list[str] = None
    reactions: dict[str, list[str]] = None  # emoji -> [user_ids]

    def __post_init__(self):
        if self.mentions is None:
            self.mentions = []
        if self.reactions is None:
            self.reactions = {}


@dataclass
class Notification:
    """Represents a notification for a user."""
    id: str
    user_id: str
    type: NotificationType
    title: str
    message: str
    entity_id: str
    entity_type: EntityType
    read: bool = False
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(UTC).isoformat()


@dataclass
class Team:
    """Represents a team/collaboration group."""
    id: str
    name: str
    description: str | None
    members: list[User]
    owner_id: str
    created_at: str
    updated_at: str


@dataclass
class ActivityLog:
    """Represents a logged activity/event."""
    id: str
    user_id: str
    action: str
    entity_id: str
    entity_type: EntityType
    description: str
    metadata: dict[str, Any]
    created_at: str


class CollaborationService:
    """Main collaboration service handling comments, notifications, and team workflows."""

    def __init__(self):
        self.comments: dict[str, Comment] = {}
        self.notifications: dict[str, Notification] = {}
        self.teams: dict[str, Team] = {}
        self.activity_logs: list[ActivityLog] = []
        self._connected_users: set[str] = set()
        self._initialize_sample_data()

    def _initialize_sample_data(self):
        """Initialize with sample collaboration data."""
        # Sample users
        users = [
            User("user_1", "alice_dev", "alice@example.com", role=UserRole.OWNER),
            User("user_2", "bob_eng", "bob@example.com", role=UserRole.ADMIN),
            User("user_3", "charlie_qa", "charlie@example.com", role=UserRole.MEMBER),
            User("user_4", "diana_pm", "diana@example.com", role=UserRole.MEMBER)
        ]

        # Sample team
        team = Team(
            id="team_1",
            name="ThetaAI Development Team",
            description="Core development team for ThetaAI platform",
            members=users,
            owner_id="user_1",
            created_at=datetime.now(UTC).isoformat(),
            updated_at=datetime.now(UTC).isoformat()
        )
        self.teams[team.id] = team

        # Sample comments
        comment1 = Comment(
            id="comment_1",
            entity_id="project_thetaai",
            entity_type=EntityType.PROJECT,
            author_id="user_1",
            content="Great progress on the architecture! The microservices design looks solid.",
            created_at=datetime.now(UTC).isoformat(),
            updated_at=datetime.now(UTC).isoformat(),
            mentions=["user_2"]
        )

        comment2 = Comment(
            id="comment_2",
            entity_id="project_thetaai",
            entity_type=EntityType.PROJECT,
            author_id="user_2",
            content="Thanks Alice! I've updated the database schema based on our discussion.",
            created_at=datetime.now(UTC).isoformat(),
            updated_at=datetime.now(UTC).isoformat(),
            parent_id="comment_1"
        )

        self.comments[comment1.id] = comment1
        self.comments[comment2.id] = comment2

        # Sample notifications
        notification = Notification(
            id="notif_1",
            user_id="user_2",
            type=NotificationType.MENTION,
            title="New mention in project",
            message="Alice mentioned you in a comment about the ThetaAI project",
            entity_id="project_thetaai",
            entity_type=EntityType.PROJECT
        )
        self.notifications[notification.id] = notification

    async def create_comment(
        self,
        entity_id: str,
        entity_type: EntityType,
        author_id: str,
        content: str,
        parent_id: str | None = None,
        mentions: list[str] | None = None
    ) -> Comment:
        """Create a new comment on an entity."""
        try:
            comment_id = f"comment_{uuid.uuid4().hex[:8]}"

            comment = Comment(
                id=comment_id,
                entity_id=entity_id,
                entity_type=entity_type,
                author_id=author_id,
                content=content,
                parent_id=parent_id,
                mentions=mentions or [],
                created_at=datetime.now(UTC).isoformat(),
                updated_at=datetime.now(UTC).isoformat()
            )

            self.comments[comment_id] = comment

            # Create notifications for mentions
            if mentions:
                for mentioned_user in mentions:
                    await self.create_notification(
                        user_id=mentioned_user,
                        type=NotificationType.MENTION,
                        title="You were mentioned",
                        message=f"{self._get_username(author_id)} mentioned you in a comment",
                        entity_id=entity_id,
                        entity_type=entity_type
                    )

            # Log activity
            await self.log_activity(
                user_id=author_id,
                action="comment_created",
                entity_id=entity_id,
                entity_type=entity_type,
                description=f"Commented on {entity_type.value}",
                metadata={"comment_id": comment_id, "parent_id": parent_id}
            )

            logger.info(f"Created comment on {entity_type.value} {entity_id}", comment_id=comment_id)
            return comment

        except Exception as e:
            logger.error("Failed to create comment", error=str(e))
            raise

    async def get_comments(
        self,
        entity_id: str,
        entity_type: EntityType,
        limit: int = 50
    ) -> list[Comment]:
        """Get comments for an entity."""
        try:
            entity_comments = [
                comment for comment in self.comments.values()
                if comment.entity_id == entity_id and comment.entity_type == entity_type
            ]

            # Sort by creation time (oldest first)
            entity_comments.sort(key=lambda x: x.created_at)

            return entity_comments[:limit]

        except Exception as e:
            logger.error("Failed to get comments", error=str(e))
            raise

    async def update_comment(
        self,
        comment_id: str,
        content: str | None = None,
        mentions: list[str] | None = None
    ) -> Comment:
        """Update an existing comment."""
        try:
            comment = self.comments.get(comment_id)
            if not comment:
                raise ValueError(f"Comment {comment_id} not found")

            if content is not None:
                comment.content = content
            if mentions is not None:
                comment.mentions = mentions

            comment.updated_at = datetime.now(UTC).isoformat()

            # Handle new mentions for notifications
            if mentions:
                existing_mentions = set(comment.mentions or [])
                new_mentions = set(mentions) - existing_mentions
                for mentioned_user in new_mentions:
                    await self.create_notification(
                        user_id=mentioned_user,
                        type=NotificationType.MENTION,
                        title="You were mentioned",
                        message=f"{self._get_username(comment.author_id)} mentioned you in an updated comment",
                        entity_id=comment.entity_id,
                        entity_type=comment.entity_type
                    )

            await self.log_activity(
                user_id=comment.author_id,
                action="comment_updated",
                entity_id=comment.entity_id,
                entity_type=comment.entity_type,
                description="Updated comment",
                metadata={"comment_id": comment_id}
            )

            logger.info(f"Updated comment {comment_id}")
            return comment

        except Exception as e:
            logger.error("Failed to update comment", error=str(e), comment_id=comment_id)
            raise

    async def delete_comment(self, comment_id: str) -> bool:
        """Delete a comment."""
        try:
            comment = self.comments.get(comment_id)
            if not comment:
                return False

            del self.comments[comment_id]

            await self.log_activity(
                user_id=comment.author_id,
                action="comment_deleted",
                entity_id=comment.entity_id,
                entity_type=comment.entity_type,
                description="Deleted comment",
                metadata={"comment_id": comment_id}
            )

            logger.info(f"Deleted comment {comment_id}")
            return True

        except Exception as e:
            logger.error("Failed to delete comment", error=str(e), comment_id=comment_id)
            raise

    async def add_reaction(
        self,
        comment_id: str,
        user_id: str,
        emoji: str
    ) -> Comment:
        """Add a reaction to a comment."""
        try:
            comment = self.comments.get(comment_id)
            if not comment:
                raise ValueError(f"Comment {comment_id} not found")

            if emoji not in comment.reactions:
                comment.reactions[emoji] = []

            if user_id not in comment.reactions[emoji]:
                comment.reactions[emoji].append(user_id)

            await self.log_activity(
                user_id=user_id,
                action="reaction_added",
                entity_id=comment.entity_id,
                entity_type=comment.entity_type,
                description=f"Reacted with {emoji}",
                metadata={"comment_id": comment_id, "emoji": emoji}
            )

            logger.info(f"Added reaction {emoji} to comment {comment_id}", user_id=user_id)
            return comment

        except Exception as e:
            logger.error("Failed to add reaction", error=str(e))
            raise

    async def create_notification(
        self,
        user_id: str,
        type: NotificationType,
        title: str,
        message: str,
        entity_id: str,
        entity_type: EntityType
    ) -> Notification:
        """Create a new notification for a user."""
        try:
            notification_id = f"notif_{uuid.uuid4().hex[:8]}"

            notification = Notification(
                id=notification_id,
                user_id=user_id,
                type=type,
                title=title,
                message=message,
                entity_id=entity_id,
                entity_type=entity_type
            )

            self.notifications[notification_id] = notification

            logger.info(f"Created notification for user {user_id}", notification_id=notification_id)
            return notification

        except Exception as e:
            logger.error("Failed to create notification", error=str(e))
            raise

    async def get_user_notifications(
        self,
        user_id: str,
        unread_only: bool = False,
        limit: int = 20
    ) -> list[Notification]:
        """Get notifications for a user."""
        try:
            user_notifications = [
                notif for notif in self.notifications.values()
                if notif.user_id == user_id
            ]

            if unread_only:
                user_notifications = [n for n in user_notifications if not n.read]

            # Sort by creation time (newest first)
            user_notifications.sort(key=lambda x: x.created_at, reverse=True)

            return user_notifications[:limit]

        except Exception as e:
            logger.error("Failed to get user notifications", error=str(e))
            raise

    async def mark_notification_read(self, notification_id: str) -> bool:
        """Mark a notification as read."""
        try:
            notification = self.notifications.get(notification_id)
            if not notification:
                return False

            notification.read = True
            return True

        except Exception as e:
            logger.error("Failed to mark notification as read", error=str(e))
            raise

    async def create_team(
        self,
        name: str,
        owner_id: str,
        description: str | None = None,
        initial_members: list[User] | None = None
    ) -> Team:
        """Create a new team."""
        try:
            team_id = f"team_{uuid.uuid4().hex[:8]}"

            team = Team(
                id=team_id,
                name=name,
                description=description,
                members=initial_members or [],
                owner_id=owner_id,
                created_at=datetime.now(UTC).isoformat(),
                updated_at=datetime.now(UTC).isoformat()
            )

            self.teams[team_id] = team

            await self.log_activity(
                user_id=owner_id,
                action="team_created",
                entity_id=team_id,
                entity_type=EntityType.PROJECT,  # Teams are treated as projects for logging
                description=f"Created team '{name}'",
                metadata={}
            )

            logger.info(f"Created team: {name}", team_id=team_id)
            return team

        except Exception as e:
            logger.error("Failed to create team", error=str(e))
            raise

    async def add_team_member(
        self,
        team_id: str,
        user: User
    ) -> Team:
        """Add a member to a team."""
        try:
            team = self.teams.get(team_id)
            if not team:
                raise ValueError(f"Team {team_id} not found")

            # Check if user already exists
            if any(member.id == user.id for member in team.members):
                raise ValueError(f"User {user.id} is already a member")

            team.members.append(user)
            team.updated_at = datetime.now(UTC).isoformat()

            await self.log_activity(
                user_id=team.owner_id,
                action="member_added",
                entity_id=team_id,
                entity_type=EntityType.PROJECT,
                description=f"Added {user.username} to team",
                metadata={"added_user_id": user.id}
            )

            logger.info(f"Added member {user.username} to team {team_id}")
            return team

        except Exception as e:
            logger.error("Failed to add team member", error=str(e))
            raise

    async def log_activity(
        self,
        user_id: str,
        action: str,
        entity_id: str,
        entity_type: EntityType,
        description: str,
        metadata: dict[str, Any]
    ) -> ActivityLog:
        """Log an activity/event."""
        try:
            activity_id = f"activity_{uuid.uuid4().hex[:8]}"

            activity = ActivityLog(
                id=activity_id,
                user_id=user_id,
                action=action,
                entity_id=entity_id,
                entity_type=entity_type,
                description=description,
                metadata=metadata,
                created_at=datetime.now(UTC).isoformat()
            )

            self.activity_logs.append(activity)

            # Keep only last 1000 activities to prevent memory issues
            if len(self.activity_logs) > 1000:
                self.activity_logs = self.activity_logs[-1000:]

            logger.info(f"Logged activity: {action}", activity_id=activity_id)
            return activity

        except Exception as e:
            logger.error("Failed to log activity", error=str(e))
            raise

    async def get_recent_activities(
        self,
        limit: int = 50
    ) -> list[ActivityLog]:
        """Get recent activities."""
        try:
            # Sort by creation time (newest first)
            sorted_activities = sorted(
                self.activity_logs,
                key=lambda x: x.created_at,
                reverse=True
            )

            return sorted_activities[:limit]

        except Exception as e:
            logger.error("Failed to get recent activities", error=str(e))
            raise

    async def get_entity_activity(
        self,
        entity_id: str,
        entity_type: EntityType,
        limit: int = 20
    ) -> list[ActivityLog]:
        """Get activities for a specific entity."""
        try:
            entity_activities = [
                activity for activity in self.activity_logs
                if activity.entity_id == entity_id and activity.entity_type == entity_type
            ]

            # Sort by creation time (newest first)
            entity_activities.sort(key=lambda x: x.created_at, reverse=True)

            return entity_activities[:limit]

        except Exception as e:
            logger.error("Failed to get entity activities", error=str(e))
            raise

    async def connect_user(self, user_id: str):
        """Register a user as connected (for real-time features)."""
        self._connected_users.add(user_id)
        logger.info(f"User {user_id} connected", connected_users=len(self._connected_users))

    async def disconnect_user(self, user_id: str):
        """Unregister a user as connected."""
        self._connected_users.discard(user_id)
        logger.info(f"User {user_id} disconnected", connected_users=len(self._connected_users))

    async def get_connected_users_count(self) -> int:
        """Get count of currently connected users."""
        return len(self._connected_users)

    # Private helper methods
    def _get_username(self, user_id: str) -> str:
        """Get username for a user ID (simplified lookup)."""
        # In a real implementation, this would query a user service
        user_map = {
            "user_1": "Alice",
            "user_2": "Bob",
            "user_3": "Charlie",
            "user_4": "Diana"
        }
        return user_map.get(user_id, f"User {user_id}")


# Global service instance
collaboration_service = CollaborationService()
