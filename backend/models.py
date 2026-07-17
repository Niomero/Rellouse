"""
Database Models
Defines all SQLAlchemy models for the application
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum as SQLEnum, Table
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()


class UserRole(str, enum.Enum):
    """User role enumeration"""
    USER = "user"
    VERIFIED = "verified"
    ADMINISTRATOR = "administrator"
    OWNER = "owner"


class ChannelType(str, enum.Enum):
    """Channel type enumeration"""
    PUBLIC = "public"
    PRIVATE = "private"


class ChannelMemberRole(str, enum.Enum):
    """Channel member role enumeration"""
    MEMBER = "member"
    ADMIN = "admin"
    OWNER = "owner"


# Association table for channel members
channel_members = Table(
    'channel_members',
    Base.metadata,
    Column('channel_id', Integer, ForeignKey('channels.id'), primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('role', SQLEnum(ChannelMemberRole), default=ChannelMemberRole.MEMBER, nullable=False),
    Column('joined_at', DateTime, default=datetime.utcnow, nullable=False)
)


class User(Base):
    """User model - represents regular users, admins, and system bots"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    login = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=True)  # Nullable for system bots
    username = Column(String(17), unique=True, nullable=False, index=True)  # @username (4-16 chars + @)
    display_name = Column(String(255), nullable=True)  # Full name for display
    additional_usernames = Column(Text, nullable=True)  # JSON array of additional usernames (max 4)
    avatar_url = Column(String(512), nullable=True)
    bio = Column(Text, nullable=True)
    role = Column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_bot = Column(Boolean, default=False, nullable=False)  # True for system bots
    is_online = Column(Boolean, default=False, nullable=False)
    last_seen = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    sent_messages = relationship("Message", foreign_keys="Message.sender_id", back_populates="sender")
    received_messages = relationship("Message", foreign_keys="Message.recipient_id", back_populates="recipient")
    verification_requests = relationship("VerificationRequest", foreign_keys="VerificationRequest.user_id", back_populates="user")
    owned_channels = relationship("Channel", back_populates="owner")
    channels = relationship("Channel", secondary=channel_members, back_populates="members")
    channel_posts = relationship("ChannelPost", back_populates="author")
    
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, role={self.role}, is_bot={self.is_bot})>"


class Bot(Base):
    """Bot model - DEPRECATED - Use User with is_bot=True instead"""
    __tablename__ = "bots"
    
    id = Column(String(50), primary_key=True, index=True)  # ~1, ~2, ~3, etc.
    username = Column(String(17), unique=True, nullable=False, index=True)  # @botname
    display_name = Column(String(255), nullable=False)
    avatar_url = Column(String(512), nullable=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    sent_messages = relationship("Message", foreign_keys="Message.bot_sender_id", back_populates="bot_sender")
    
    def __repr__(self):
        return f"<Bot(id={self.id}, username={self.username})>"


class Channel(Base):
    """Channel model - represents public or private channels"""
    __tablename__ = "channels"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    username = Column(String(17), unique=True, nullable=True, index=True)  # @channelname for public channels
    description = Column(Text, nullable=True)
    avatar_url = Column(String(512), nullable=True)
    channel_type = Column(SQLEnum(ChannelType), default=ChannelType.PUBLIC, nullable=False)
    invite_link = Column(String(255), unique=True, nullable=True)  # For private channels
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    member_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    owner = relationship("User", back_populates="owned_channels")
    members = relationship("User", secondary=channel_members, back_populates="channels")
    posts = relationship("ChannelPost", back_populates="channel")
    
    def __repr__(self):
        return f"<Channel(id={self.id}, name={self.name}, type={self.channel_type})>"


class ChannelPost(Base):
    """Channel post model - represents posts in channels"""
    __tablename__ = "channel_posts"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    channel_id = Column(Integer, ForeignKey("channels.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    edited_at = Column(DateTime, nullable=True)
    deleted_at = Column(DateTime, nullable=True)
    
    # Relationships
    channel = relationship("Channel", back_populates="posts")
    author = relationship("User", back_populates="channel_posts")
    attachments = relationship("PostAttachment", back_populates="post")
    
    def __repr__(self):
        return f"<ChannelPost(id={self.id}, channel_id={self.channel_id}, author_id={self.author_id})>"


class PostAttachment(Base):
    """Post attachment model - represents files attached to channel posts"""
    __tablename__ = "post_attachments"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    post_id = Column(Integer, ForeignKey("channel_posts.id"), nullable=False)
    file_url = Column(String(512), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)  # Size in bytes
    file_type = Column(String(100), nullable=False)  # MIME type
    thumbnail_url = Column(String(512), nullable=True)  # For images/videos
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    post = relationship("ChannelPost", back_populates="attachments")
    
    def __repr__(self):
        return f"<PostAttachment(id={self.id}, post_id={self.post_id}, file_name={self.file_name})>"


class Message(Base):
    """Message model - represents encrypted messages between users"""
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    bot_sender_id = Column(String(50), ForeignKey("bots.id"), nullable=True)
    recipient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    encrypted_content = Column(Text, nullable=False)  # End-to-end encrypted message
    encryption_key_id = Column(String(255), nullable=False)  # Key identifier for decryption
    is_read = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    edited_at = Column(DateTime, nullable=True)
    deleted_at = Column(DateTime, nullable=True)
    
    # Relationships
    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_messages")
    bot_sender = relationship("Bot", foreign_keys=[bot_sender_id], back_populates="sent_messages")
    recipient = relationship("User", foreign_keys=[recipient_id], back_populates="received_messages")
    attachments = relationship("MessageAttachment", back_populates="message")
    
    def __repr__(self):
        return f"<Message(id={self.id}, sender_id={self.sender_id}, recipient_id={self.recipient_id})>"


class MessageAttachment(Base):
    """Message attachment model - represents files attached to messages"""
    __tablename__ = "message_attachments"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    message_id = Column(Integer, ForeignKey("messages.id"), nullable=False)
    file_url = Column(String(512), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)  # Size in bytes
    file_type = Column(String(100), nullable=False)  # MIME type
    thumbnail_url = Column(String(512), nullable=True)  # For images/videos
    encrypted = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    message = relationship("Message", back_populates="attachments")
    
    def __repr__(self):
        return f"<MessageAttachment(id={self.id}, message_id={self.message_id}, file_name={self.file_name})>"


class VerificationRequest(Base):
    """Verification request model - represents user verification applications"""
    __tablename__ = "verification_requests"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    description = Column(Text, nullable=False)
    telegram_links = Column(Text, nullable=True)  # JSON array
    social_links = Column(Text, nullable=True)  # JSON array
    website_links = Column(Text, nullable=True)  # JSON array
    additional_materials = Column(Text, nullable=True)
    status = Column(String(50), default="pending", nullable=False)  # pending, approved, rejected
    admin_comment = Column(Text, nullable=True)
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    reviewed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="verification_requests")
    reviewer = relationship("User", foreign_keys=[reviewed_by])
    
    def __repr__(self):
        return f"<VerificationRequest(id={self.id}, user_id={self.user_id}, status={self.status})>"


class SecurityLog(Base):
    """Security log model - tracks security events and suspicious activity"""
    __tablename__ = "security_logs"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    event_type = Column(String(100), nullable=False)  # login, failed_login, password_change, etc.
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent = Column(String(512), nullable=True)
    details = Column(Text, nullable=True)  # JSON with additional details
    severity = Column(String(20), default="info", nullable=False)  # info, warning, critical
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def __repr__(self):
        return f"<SecurityLog(id={self.id}, event_type={self.event_type}, severity={self.severity})>"


class Session(Base):
    """Session model - tracks active user sessions"""
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String(512), unique=True, nullable=False, index=True)
    refresh_token = Column(String(512), unique=True, nullable=False, index=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(512), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    last_activity = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<Session(id={self.id}, user_id={self.user_id}, is_active={self.is_active})>"