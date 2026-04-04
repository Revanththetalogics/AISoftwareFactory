"""
Comprehensive tests for CollaborationService to increase coverage.
"""

from unittest.mock import patch

import pytest
from backend.services.collaboration_service import (
    CollaborationService,
    Comment,
    EntityType,
    Notification,
    NotificationType,
    Team,
    User,
    UserRole,
)


class TestCollaborationService:
    """Comprehensive tests for CollaborationService."""

    @pytest.fixture
    def collaboration_service(self):
        """Create CollaborationService instance."""
        service = CollaborationService()
        # Clear existing data for clean tests
        service.comments.clear()
        service.notifications.clear()
        service.teams.clear()
        service.activity_logs.clear()
        return service

    def test_init(self, collaboration_service):
        """Test CollaborationService initialization."""
        assert collaboration_service is not None
        assert isinstance(collaboration_service.comments, dict)
        assert isinstance(collaboration_service.notifications, dict)
        assert isinstance(collaboration_service.teams, dict)
        assert isinstance(collaboration_service.activity_logs, list)
        assert isinstance(collaboration_service._connected_users, set)

    @pytest.mark.asyncio
    async def test_create_comment_success(self, collaboration_service):
        """Test successful comment creation."""
        comment = await collaboration_service.create_comment(
            entity_id="project123",
            entity_type=EntityType.PROJECT,
            author_id="user123",
            content="This is a great project!",
            mentions=["user456"],
        )

        assert isinstance(comment, Comment)
        assert comment.entity_id == "project123"
        assert comment.entity_type == EntityType.PROJECT
        assert comment.author_id == "user123"
        assert comment.content == "This is a great project!"
        assert comment.mentions == ["user456"]
        assert comment.id.startswith("comment_")
        assert "created_at" in comment.__dict__
        assert "updated_at" in comment.__dict__

        # Verify comment was stored
        assert comment.id in collaboration_service.comments
        assert collaboration_service.comments[comment.id] == comment

    @pytest.mark.asyncio
    async def test_get_comments_success(self, collaboration_service):
        """Test retrieving comments for an entity."""
        # Create multiple comments
        comment1 = await collaboration_service.create_comment(
            entity_id="project123", entity_type=EntityType.PROJECT, author_id="user123", content="First comment"
        )

        comment2 = await collaboration_service.create_comment(
            entity_id="project123", entity_type=EntityType.PROJECT, author_id="user456", content="Second comment"
        )

        # Get comments
        comments = await collaboration_service.get_comments(entity_id="project123", entity_type=EntityType.PROJECT)

        assert len(comments) == 2
        assert comments[0].id == comment1.id
        assert comments[1].id == comment2.id
        # Comments should be sorted by creation time (oldest first)
        assert comments[0].created_at <= comments[1].created_at

    @pytest.mark.asyncio
    async def test_update_comment_success(self, collaboration_service):
        """Test updating an existing comment."""
        # Create comment first
        comment = await collaboration_service.create_comment(
            entity_id="project123", entity_type=EntityType.PROJECT, author_id="user123", content="Original content"
        )

        # Update comment
        updated_comment = await collaboration_service.update_comment(
            comment_id=comment.id, content="Updated content", mentions=["user456"]
        )

        assert updated_comment.id == comment.id
        assert updated_comment.content == "Updated content"
        assert updated_comment.mentions == ["user456"]
        # Updated timestamp should be newer
        assert updated_comment.updated_at >= comment.updated_at

    @pytest.mark.asyncio
    async def test_delete_comment_success(self, collaboration_service):
        """Test deleting a comment."""
        # Create comment first
        comment = await collaboration_service.create_comment(
            entity_id="project123", entity_type=EntityType.PROJECT, author_id="user123", content="To be deleted"
        )

        # Verify comment exists
        assert comment.id in collaboration_service.comments

        # Delete comment
        result = await collaboration_service.delete_comment(comment.id)

        assert result is True
        # Verify comment was removed
        assert comment.id not in collaboration_service.comments

    @pytest.mark.asyncio
    async def test_get_session_messages_success(self, collaboration_service):
        """Test retrieving session messages."""
        # Create session and send messages
        with patch.object(collaboration_service, "_generate_session_id", return_value="sess123"):
            with patch.object(collaboration_service, "_create_session_token", return_value="token123"):
                await collaboration_service.create_collaboration_session(
                    project_id="proj123", creator_id="user123", participants=["user456"], session_type="code_review"
                )

        # Send multiple messages
        await collaboration_service.send_collaboration_message(
            session_id="sess123", sender_id="user123", message_type="text", content="First message"
        )

        await collaboration_service.send_collaboration_message(
            session_id="sess123", sender_id="user456", message_type="text", content="Second message"
        )

        # Get messages
        messages = await collaboration_service.get_session_messages("sess123")

        assert len(messages) == 2
        assert messages[0]["content"] == "First message"
        assert messages[1]["content"] == "Second message"
        # Messages should be ordered by timestamp (oldest first)
        assert messages[0]["timestamp"] <= messages[1]["timestamp"]

    @pytest.mark.asyncio
    async def test_end_collaboration_session_success(self, collaboration_service):
        """Test ending collaboration session."""
        # Create session
        with patch.object(collaboration_service, "_generate_session_id", return_value="sess123"):
            with patch.object(collaboration_service, "_create_session_token", return_value="token123"):
                await collaboration_service.create_collaboration_session(
                    project_id="proj123",
                    creator_id="user123",
                    participants=["user456"],
                    session_type="pair_programming",
                )

        # End session
        result = await collaboration_service.end_collaboration_session("sess123")

        assert result["session_id"] == "sess123"
        assert result["status"] == "ended"
        assert "ended_at" in result

        # Verify session is no longer active
        sessions = await collaboration_service.list_active_sessions("proj123")
        assert len(sessions) == 0

    @pytest.mark.asyncio
    async def test_list_active_sessions_success(self, collaboration_service):
        """Test listing active sessions."""
        # Create multiple sessions
        with patch.object(collaboration_service, "_generate_session_id") as mock_gen_id:
            with patch.object(collaboration_service, "_create_session_token", return_value="token123"):
                mock_gen_id.side_effect = ["sess1", "sess2", "sess3"]

                await collaboration_service.create_collaboration_session(
                    project_id="proj123", creator_id="user123", participants=["user456"], session_type="code_review"
                )

                await collaboration_service.create_collaboration_session(
                    project_id="proj123",
                    creator_id="user789",
                    participants=["user123"],
                    session_type="pair_programming",
                )

                # Create session for different project
                await collaboration_service.create_collaboration_session(
                    project_id="proj456", creator_id="user123", participants=["user456"], session_type="code_review"
                )

        # List sessions for specific project
        sessions = await collaboration_service.list_active_sessions("proj123")

        assert len(sessions) == 2
        session_ids = [s["session_id"] for s in sessions]
        assert "sess1" in session_ids
        assert "sess2" in session_ids
        assert "sess3" not in session_ids  # Different project

    @pytest.mark.asyncio
    async def test_invite_user_to_session_success(self, collaboration_service):
        """Test inviting user to collaboration session."""
        # Create session
        with patch.object(collaboration_service, "_generate_session_id", return_value="sess123"):
            with patch.object(collaboration_service, "_create_session_token", return_value="token123"):
                await collaboration_service.create_collaboration_session(
                    project_id="proj123", creator_id="user123", participants=[], session_type="code_review"
                )

        # Invite user
        invitation = await collaboration_service.invite_user_to_session(
            session_id="sess123",
            inviter_id="user123",
            invitee_id="user456",
            message="Please join my code review session",
        )

        assert invitation["session_id"] == "sess123"
        assert invitation["inviter_id"] == "user123"
        assert invitation["invitee_id"] == "user456"
        assert invitation["status"] == "pending"
        assert "invitation_token" in invitation
        assert "expires_at" in invitation

    @pytest.mark.asyncio
    async def test_respond_to_invitation_accept(self, collaboration_service):
        """Test accepting invitation."""
        # Create session and invite user
        with patch.object(collaboration_service, "_generate_session_id", return_value="sess123"):
            with patch.object(collaboration_service, "_create_session_token", return_value="token123"):
                await collaboration_service.create_collaboration_session(
                    project_id="proj123", creator_id="user123", participants=[], session_type="code_review"
                )

        invitation = await collaboration_service.invite_user_to_session(
            session_id="sess123", inviter_id="user123", invitee_id="user456", message="Join my session"
        )

        # Accept invitation
        result = await collaboration_service.respond_to_invitation(
            invitation_token=invitation["invitation_token"], invitee_id="user456", response="accept"
        )

        assert result["status"] == "accepted"
        assert result["invitee_id"] == "user456"

        # Verify user was added to session participants
        session = await collaboration_service.get_session_details("sess123")
        participant_ids = [p["user_id"] for p in session["participants"]]
        assert "user456" in participant_ids

    @pytest.mark.asyncio
    async def test_respond_to_invitation_decline(self, collaboration_service):
        """Test declining invitation."""
        # Create session and invite user
        with patch.object(collaboration_service, "_generate_session_id", return_value="sess123"):
            with patch.object(collaboration_service, "_create_session_token", return_value="token123"):
                await collaboration_service.create_collaboration_session(
                    project_id="proj123", creator_id="user123", participants=[], session_type="code_review"
                )

        invitation = await collaboration_service.invite_user_to_session(
            session_id="sess123", inviter_id="user123", invitee_id="user456", message="Join my session"
        )

        # Decline invitation
        result = await collaboration_service.respond_to_invitation(
            invitation_token=invitation["invitation_token"], invitee_id="user456", response="decline"
        )

        assert result["status"] == "declined"
        assert result["invitee_id"] == "user456"

    @pytest.mark.asyncio
    async def test_create_notification_success(self, collaboration_service):
        """Test creating notification."""
        notification = await collaboration_service.create_notification(
            recipient_id="user123",
            sender_id="user456",
            notification_type="session_invitation",
            title="Code Review Invitation",
            message="user456 has invited you to a code review session",
            related_session_id="sess123",
        )

        assert notification["recipient_id"] == "user123"
        assert notification["sender_id"] == "user456"
        assert notification["type"] == "session_invitation"
        assert notification["title"] == "Code Review Invitation"
        assert notification["status"] == "unread"
        assert "created_at" in notification
        assert notification["related_session_id"] == "sess123"

    @pytest.mark.asyncio
    async def test_list_user_notifications_success(self, collaboration_service):
        """Test listing user notifications."""
        # Create multiple notifications
        await collaboration_service.create_notification(
            recipient_id="user123",
            sender_id="user456",
            notification_type="session_invitation",
            title="Invitation 1",
            message="First invitation",
        )

        await collaboration_service.create_notification(
            recipient_id="user123",
            sender_id="user789",
            notification_type="session_started",
            title="Session Started",
            message="Session has started",
        )

        # Create notification for different user
        await collaboration_service.create_notification(
            recipient_id="user456",
            sender_id="user123",
            notification_type="message",
            title="New Message",
            message="You have a new message",
        )

        # List notifications for specific user
        notifications = await collaboration_service.list_user_notifications("user123")

        assert len(notifications) == 2
        assert all(n["recipient_id"] == "user123" for n in notifications)
        titles = [n["title"] for n in notifications]
        assert "Invitation 1" in titles
        assert "Session Started" in titles

    @pytest.mark.asyncio
    async def test_mark_notification_as_read_success(self, collaboration_service):
        """Test marking notification as read."""
        # Create notification
        notification = await collaboration_service.create_notification(
            recipient_id="user123",
            sender_id="user456",
            notification_type="session_invitation",
            title="Test Invitation",
            message="Test message",
        )

        # Mark as read
        result = await collaboration_service.mark_notification_as_read(
            notification_id=notification["id"], user_id="user123"
        )

        assert result["id"] == notification["id"]
        assert result["status"] == "read"
        assert "read_at" in result

    @pytest.mark.asyncio
    async def test_get_session_participants_success(self, collaboration_service):
        """Test getting session participants."""
        # Create session with participants
        with patch.object(collaboration_service, "_generate_session_id", return_value="sess123"):
            with patch.object(collaboration_service, "_create_session_token", return_value="token123"):
                await collaboration_service.create_collaboration_session(
                    project_id="proj123",
                    creator_id="user123",
                    participants=["user456", "user789"],
                    session_type="code_review",
                )

        # Join session
        await collaboration_service.join_collaboration_session(
            session_id="sess123", user_id="user456", token="token123"
        )

        # Get participants
        participants = await collaboration_service.get_session_participants("sess123")

        assert len(participants) == 3  # creator + 2 participants
        user_ids = [p["user_id"] for p in participants]
        assert "user123" in user_ids
        assert "user456" in user_ids
        assert "user789" in user_ids

        # Check that user456 has joined status
        user456_participant = next(p for p in participants if p["user_id"] == "user456")
        assert user456_participant["status"] == "joined"

    @pytest.mark.asyncio
    async def test_update_session_settings_success(self, collaboration_service):
        """Test updating session settings."""
        # Create session
        with patch.object(collaboration_service, "_generate_session_id", return_value="sess123"):
            with patch.object(collaboration_service, "_create_session_token", return_value="token123"):
                await collaboration_service.create_collaboration_session(
                    project_id="proj123", creator_id="user123", participants=["user456"], session_type="code_review"
                )

        # Update settings
        updated_session = await collaboration_service.update_session_settings(
            session_id="sess123", settings={"max_participants": 10, "allow_recording": True, "require_approval": False}
        )

        assert updated_session["session_id"] == "sess123"
        assert updated_session["settings"]["max_participants"] == 10
        assert updated_session["settings"]["allow_recording"] is True
        assert updated_session["settings"]["require_approval"] is False

    @pytest.mark.asyncio
    async def test_generate_session_report_success(self, collaboration_service):
        """Test generating session report."""
        # Create session and add some activity
        with patch.object(collaboration_service, "_generate_session_id", return_value="sess123"):
            with patch.object(collaboration_service, "_create_session_token", return_value="token123"):
                await collaboration_service.create_collaboration_session(
                    project_id="proj123", creator_id="user123", participants=["user456"], session_type="code_review"
                )

        # Add participants and messages
        await collaboration_service.join_collaboration_session(
            session_id="sess123", user_id="user456", token="token123"
        )

        await collaboration_service.send_collaboration_message(
            session_id="sess123", sender_id="user123", message_type="text", content="Review this code"
        )

        await collaboration_service.send_collaboration_message(
            session_id="sess123", sender_id="user456", message_type="text", content="Looks good to me"
        )

        # Generate report
        report = await collaboration_service.generate_session_report("sess123")

        assert report["session_id"] == "sess123"
        assert report["project_id"] == "proj123"
        assert report["session_type"] == "code_review"
        assert "duration" in report
        assert "participant_count" in report
        assert "message_count" in report
        assert report["message_count"] == 2
        assert "created_at" in report
        assert "ended_at" in report

    @pytest.mark.asyncio
    async def test_add_reaction_success(self, collaboration_service):
        """Test adding reaction to a comment."""
        # Create comment first
        comment = await collaboration_service.create_comment(
            entity_id="project123", entity_type=EntityType.PROJECT, author_id="user123", content="Nice work!"
        )

        # Add reaction
        reacted_comment = await collaboration_service.add_reaction(comment_id=comment.id, user_id="user456", emoji="👍")

        assert reacted_comment.id == comment.id
        assert "👍" in reacted_comment.reactions
        assert "user456" in reacted_comment.reactions["👍"]

        # Add another reaction from same user (should not duplicate)
        reacted_comment2 = await collaboration_service.add_reaction(
            comment_id=comment.id, user_id="user456", emoji="👍"
        )

        assert len(reacted_comment2.reactions["👍"]) == 1

        # Add reaction from different user
        reacted_comment3 = await collaboration_service.add_reaction(
            comment_id=comment.id, user_id="user789", emoji="👍"
        )

        assert len(reacted_comment3.reactions["👍"]) == 2
        assert "user789" in reacted_comment3.reactions["👍"]

    @pytest.mark.asyncio
    async def test_create_notification_with_entity_type(self, collaboration_service):
        """Test creating notification with entity type."""
        notification = await collaboration_service.create_notification(
            user_id="user123",
            type=NotificationType.COMMENT,
            title="New Comment",
            message="Someone commented on your project",
            entity_id="project123",
            entity_type=EntityType.PROJECT,
        )

        assert isinstance(notification, Notification)
        assert notification.user_id == "user123"
        assert notification.type == NotificationType.COMMENT
        assert notification.title == "New Comment"
        assert notification.message == "Someone commented on your project"
        assert notification.entity_id == "project123"
        assert notification.entity_type == EntityType.PROJECT
        assert notification.id.startswith("notif_")
        assert notification.read is False

        # Verify notification was stored
        assert notification.id in collaboration_service.notifications
        assert collaboration_service.notifications[notification.id] == notification

    @pytest.mark.asyncio
    async def test_get_user_notifications_success(self, collaboration_service):
        """Test getting user notifications."""
        # Create multiple notifications
        await collaboration_service.create_notification(
            user_id="user123",
            type=NotificationType.COMMENT,
            title="Comment 1",
            message="First comment notification",
            entity_id="project123",
            entity_type=EntityType.PROJECT,
        )

        await collaboration_service.create_notification(
            user_id="user123",
            type=NotificationType.MENTION,
            title="Mention 1",
            message="You were mentioned",
            entity_id="project123",
            entity_type=EntityType.PROJECT,
        )

        # Create notification for different user
        await collaboration_service.create_notification(
            user_id="user456",
            type=NotificationType.ASSIGNMENT,
            title="Assignment",
            message="You were assigned a task",
            entity_id="task123",
            entity_type=EntityType.TASK,
        )

        # Get notifications for specific user
        notifications = await collaboration_service.get_user_notifications("user123")

        assert len(notifications) == 2
        assert all(n.user_id == "user123" for n in notifications)
        titles = [n.title for n in notifications]
        assert "Comment 1" in titles
        assert "Mention 1" in titles
        # Should be sorted by newest first
        assert notifications[0].created_at >= notifications[1].created_at

    @pytest.mark.asyncio
    async def test_mark_notification_read_success(self, collaboration_service):
        """Test marking notification as read."""
        # Create notification
        notification = await collaboration_service.create_notification(
            user_id="user123",
            type=NotificationType.COMMENT,
            title="Test Notification",
            message="Test message",
            entity_id="project123",
            entity_type=EntityType.PROJECT,
        )

        # Verify it's initially unread
        assert notification.read is False

        # Mark as read
        result = await collaboration_service.mark_notification_read(notification.id)

        assert result is True
        # Verify it's now marked as read
        updated_notification = collaboration_service.notifications[notification.id]
        assert updated_notification.read is True

    @pytest.mark.asyncio
    async def test_create_team_success(self, collaboration_service):
        """Test creating team."""
        team = await collaboration_service.create_team(
            name="Test Team",
            owner_id="user123",
            description="A test team for collaboration",
            initial_members=[
                User("user456", "bob", "bob@example.com", role=UserRole.MEMBER),
                User("user789", "charlie", "charlie@example.com", role=UserRole.MEMBER),
            ],
        )

        assert isinstance(team, Team)
        assert team.name == "Test Team"
        assert team.owner_id == "user123"
        assert team.description == "A test team for collaboration"
        assert len(team.members) == 2
        assert team.id.startswith("team_")
        assert "created_at" in team.__dict__
        assert "updated_at" in team.__dict__

        # Verify team was stored
        assert team.id in collaboration_service.teams
        assert collaboration_service.teams[team.id] == team

    @pytest.mark.asyncio
    async def test_add_team_member_success(self, collaboration_service):
        """Test adding member to team."""
        # Create team first
        team = await collaboration_service.create_team(name="Test Team", owner_id="user123", description="A test team")

        # Add member
        new_member = User("user456", "bob", "bob@example.com", role=UserRole.MEMBER)
        updated_team = await collaboration_service.add_team_member(team_id=team.id, user=new_member)

        assert updated_team.id == team.id
        assert len(updated_team.members) == 1
        assert updated_team.members[0].id == "user456"
        assert updated_team.members[0].username == "bob"
        assert updated_team.updated_at >= team.updated_at

    @pytest.mark.asyncio
    async def test_log_activity_success(self, collaboration_service):
        """Test logging activity."""
        activity = await collaboration_service.log_activity(
            user_id="user123",
            action="comment_created",
            entity_id="project123",
            entity_type=EntityType.PROJECT,
            description="Created a comment",
            metadata={"comment_id": "comment123"},
        )

        assert activity.user_id == "user123"
        assert activity.action == "comment_created"
        assert activity.entity_id == "project123"
        assert activity.entity_type == EntityType.PROJECT
        assert activity.description == "Created a comment"
        assert activity.metadata["comment_id"] == "comment123"
        assert activity.id.startswith("activity_")
        assert "created_at" in activity.__dict__

        # Verify activity was stored
        assert activity in collaboration_service.activity_logs

    @pytest.mark.asyncio
    async def test_get_recent_activities_success(self, collaboration_service):
        """Test getting recent activities."""
        # Create multiple activities
        activity1 = await collaboration_service.log_activity(
            user_id="user123",
            action="comment_created",
            entity_id="project123",
            entity_type=EntityType.PROJECT,
            description="First activity",
            metadata={},
        )

        activity2 = await collaboration_service.log_activity(
            user_id="user456",
            action="comment_updated",
            entity_id="project123",
            entity_type=EntityType.PROJECT,
            description="Second activity",
            metadata={},
        )

        # Get recent activities
        activities = await collaboration_service.get_recent_activities(limit=5)

        assert len(activities) == 2
        # Should be sorted by newest first
        assert activities[0].created_at >= activities[1].created_at
        assert activities[0].id == activity2.id
        assert activities[1].id == activity1.id

    @pytest.mark.asyncio
    async def test_get_entity_activity_success(self, collaboration_service):
        """Test getting activities for specific entity."""
        # Create activities for different entities
        activity1 = await collaboration_service.log_activity(
            user_id="user123",
            action="comment_created",
            entity_id="project123",
            entity_type=EntityType.PROJECT,
            description="Activity for project123",
            metadata={},
        )

        await collaboration_service.log_activity(
            user_id="user456",
            action="comment_created",
            entity_id="project456",
            entity_type=EntityType.PROJECT,
            description="Activity for project456",
            metadata={},
        )

        # Get activities for specific entity
        activities = await collaboration_service.get_entity_activity(
            entity_id="project123", entity_type=EntityType.PROJECT
        )

        assert len(activities) == 1
        assert activities[0].entity_id == "project123"
        assert activities[0].id == activity1.id

    @pytest.mark.asyncio
    async def test_connect_disconnect_user(self, collaboration_service):
        """Test connecting and disconnecting users."""
        # Initially no connected users
        count = await collaboration_service.get_connected_users_count()
        assert count == 0

        # Connect users
        await collaboration_service.connect_user("user123")
        await collaboration_service.connect_user("user456")
        await collaboration_service.connect_user("user789")

        # Check count
        count = await collaboration_service.get_connected_users_count()
        assert count == 3

        # Disconnect one user
        await collaboration_service.disconnect_user("user456")
        count = await collaboration_service.get_connected_users_count()
        assert count == 2

        # Disconnect same user again (should not error)
        await collaboration_service.disconnect_user("user456")
        count = await collaboration_service.get_connected_users_count()
        assert count == 2

        # Disconnect remaining users
        await collaboration_service.disconnect_user("user123")
        await collaboration_service.disconnect_user("user789")
        count = await collaboration_service.get_connected_users_count()
        assert count == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
