from sqlalchemy import Boolean, String, ForeignKey, DateTime, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List
from datetime import datetime

from .base import Base, TimestampMixin

class UserModel(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False
    )
    email: Mapped[str] = mapped_column(
        String(255), 
        unique=True, 
        index=True, 
        nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_online: Mapped[bool] = mapped_column(Boolean, default=False)
    last_seen: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    messages: Mapped[List["MessageModel"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )

    owned_rooms: Mapped[List["RoomModel"]] = relationship(
        back_populates="owner"
    )
    room_associations: Mapped[List["UserRoomModel"]] = relationship(
        back_populates="user"
    )
    refresh_tokens: Mapped[List["RefreshTokenModel"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )


class RoomModel(Base, TimestampMixin):
    __tablename__ = "rooms"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500))
    is_private: Mapped[bool] = mapped_column(Boolean, default=False)
    max_participants: Mapped[int] = mapped_column(default=0)  # 0 = unlimited
    
    # Foreign keys
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # Relationships
    owner: Mapped["UserModel"] = relationship(back_populates="owned_rooms")
    messages: Mapped[List["MessageModel"]] = relationship(
        back_populates="room",
        cascade="all, delete-orphan",
        order_by="MessageModel.created_at.desc()"
    )
    user_associations: Mapped[List["UserRoomModel"]] = relationship(
        back_populates="room",
        cascade="all, delete-orphan"
    )
    
    # Property для получения участников
    @property
    def participants(self):
        return [assoc.user for assoc in self.user_associations]


class UserRoomModel(Base):
    __tablename__ = "user_rooms"
    
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    )
    room_id: Mapped[int] = mapped_column(
        ForeignKey("rooms.id", ondelete="CASCADE"),
        primary_key=True
    )
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    role: Mapped[str] = mapped_column(
        String(20),
        default="member"  # 'owner', 'admin', 'member'
    )
    notifications_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    muted_until: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    # Relationships
    user: Mapped["UserModel"] = relationship(back_populates="room_associations")
    room: Mapped["RoomModel"] = relationship(back_populates="user_associations")


class MessageModel(Base, TimestampMixin):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    message_type: Mapped[str] = mapped_column(
        String(20),
        default="text"  # 'text', 'image', 'file', 'system'
    )

    # Foreign keys
    room_id: Mapped[int] = mapped_column(
        ForeignKey("rooms.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    reply_to_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("messages.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Relationships
    room: Mapped["RoomModel"] = relationship(back_populates="messages")
    user: Mapped[Optional["UserModel"]] = relationship(back_populates="messages")

    # self-referential relationship: это уже не колонка, а отдельное отношение
    reply_to: Mapped[Optional["MessageModel"]] = relationship(
        remote_side=[id],
        backref="replies",
    )

    read_by_associations: Mapped[List["MessageReadModel"]] = relationship(
        back_populates="message",
        cascade="all, delete-orphan",
    )



class MessageReadModel(Base):
    __tablename__ = "message_reads"
    
    message_id: Mapped[int] = mapped_column(
        ForeignKey("messages.id", ondelete="CASCADE"),
        primary_key=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    )
    read_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    
    # Relationships
    message: Mapped["MessageModel"] = relationship(back_populates="read_by_associations")
    user: Mapped["UserModel"] = relationship()


class RefreshTokenModel(Base, TimestampMixin):
    __tablename__ = "refresh_tokens"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    token: Mapped[str] = mapped_column(String(512), unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Foreign key
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Relationships
    user: Mapped["UserModel"] = relationship(back_populates="refresh_tokens")