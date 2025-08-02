from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Interval,
    String,
    Table,
    Text,
    UniqueConstraint,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from .database import Base

# Association table for roles and permissions
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column(
        "permission_id", Integer, ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True
    ),
)


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text)

    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")
    users = relationship("User", back_populates="role")


class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True, nullable=False)
    description = Column(Text)

    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")
    users = relationship("AccessRight", back_populates="permission")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(String)
    full_name = Column(String)
    role_id = Column(Integer, ForeignKey("roles.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    role = relationship("Role", back_populates="users")
    tasks_created = relationship("Task", back_populates="creator", foreign_keys="Task.created_by")
    tasks_assigned = relationship(
        "Task", back_populates="assignee", foreign_keys="Task.assigned_to"
    )
    events_created = relationship("Event", back_populates="creator")
    event_participations = relationship("EventParticipant", back_populates="user")
    time_entries = relationship("TimeTracking", back_populates="user")
    documents_created = relationship("Document", back_populates="creator")
    approvals = relationship("DocumentApproval", back_populates="approver")
    access_rights = relationship("AccessRight", back_populates="user")
    notifications = relationship("ChatNotification", back_populates="user")
    poll_responses = relationship("PollResponse", back_populates="user")


class AccessRight(Base):
    __tablename__ = "access_rights"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    permission_id = Column(Integer, ForeignKey("permissions.id", ondelete="CASCADE"))
    granted_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="access_rights")
    permission = relationship("Permission", back_populates="users")


class EventType(Base):
    __tablename__ = "event_types"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text)
    default_reminder_15min = Column(Boolean, default=True)
    default_reminder_1h = Column(Boolean, default=False)
    default_reminder_1d = Column(Boolean, default=False)

    events = relationship("Event", back_populates="type")


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    event_type_id = Column(Integer, ForeignKey("event_types.id"))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    location = Column(String)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    type = relationship("EventType", back_populates="events")
    creator = relationship("User", back_populates="events_created")
    participants = relationship("EventParticipant", back_populates="event")


class EventParticipant(Base):
    __tablename__ = "event_participants"

    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey("events.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    reminder_15min = Column(Boolean, default=True)
    reminder_1h = Column(Boolean, default=False)
    reminder_1d = Column(Boolean, default=False)

    event = relationship("Event", back_populates="participants")
    user = relationship("User", back_populates="event_participations")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    title = Column(Text, nullable=False)
    description = Column(Text)
    deadline = Column(DateTime)
    created_by = Column(Integer, ForeignKey("users.id"))
    assigned_to = Column(Integer, ForeignKey("users.id"))
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    creator = relationship("User", back_populates="tasks_created", foreign_keys=[created_by])
    assignee = relationship("User", back_populates="tasks_assigned", foreign_keys=[assigned_to])


class TimeTracking(Base):
    __tablename__ = "time_tracking"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    description = Column(Text)
    started_at = Column(DateTime)
    ended_at = Column(DateTime)
    duration = Column(Interval)

    user = relationship("User", back_populates="time_entries")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)
    title = Column(Text, nullable=False)
    description = Column(Text)
    status = Column(String, nullable=False, default="draft")
    file_url = Column(String)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    creator = relationship("User", back_populates="documents_created")
    approvals = relationship("DocumentApproval", back_populates="document")


class DocumentApproval(Base):
    __tablename__ = "document_approvals"

    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    approver_id = Column(Integer, ForeignKey("users.id"))
    approved = Column(Boolean, default=False)
    approved_at = Column(DateTime)
    order_index = Column(Integer)

    document = relationship("Document", back_populates="approvals")
    approver = relationship("User", back_populates="approvals")


class ChatNotification(Base):
    __tablename__ = "chat_notifications"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    event_id = Column(Integer, ForeignKey("events.id"))
    sent_at = Column(DateTime, default=datetime.utcnow)
    chat_type = Column(String, nullable=False)
    message = Column(Text)

    user = relationship("User", back_populates="notifications")
    event = relationship("Event")


class Poll(Base):
    __tablename__ = "polls"

    id = Column(Integer, primary_key=True)
    question = Column(Text, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    creator = relationship("User")
    options = relationship("PollOption", back_populates="poll")
    responses = relationship("PollResponse", back_populates="poll")


class PollOption(Base):
    __tablename__ = "poll_options"
    __table_args__ = (UniqueConstraint("poll_id", "option_text", name="uix_poll_option"),)

    id = Column(Integer, primary_key=True)
    poll_id = Column(Integer, ForeignKey("polls.id"))
    option_text = Column(Text, nullable=False)

    poll = relationship("Poll", back_populates="options")
    responses = relationship("PollResponse", back_populates="option")


class PollResponse(Base):
    __tablename__ = "poll_responses"

    id = Column(Integer, primary_key=True)
    poll_id = Column(Integer, ForeignKey("polls.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    option_id = Column(Integer, ForeignKey("poll_options.id"))
    responded_at = Column(DateTime, default=datetime.utcnow)

    poll = relationship("Poll", back_populates="responses")
    user = relationship("User", back_populates="poll_responses")
    option = relationship("PollOption", back_populates="responses")
