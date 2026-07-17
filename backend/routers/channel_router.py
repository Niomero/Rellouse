"""
Channel Router
Handles channel-related endpoints: create, update, join, leave, posts
"""
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func, and_, delete
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import json
import secrets
import string

from database import get_db
from models import User, Channel, ChannelType, ChannelMemberRole, ChannelPost, PostAttachment, MessageType, AttachmentType, channel_members
from auth import get_current_user

router = APIRouter(prefix="/api/channels", tags=["channels"])


# Pydantic models
class CreateChannelRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    avatar_url: Optional[str] = None
    channel_type: ChannelType
    username: Optional[str] = Field(None, min_length=5, max_length=16)  # For public channels


class UpdateChannelRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    avatar_url: Optional[str] = None
    username: Optional[str] = Field(None, min_length=5, max_length=16)


class ChannelMemberResponse(BaseModel):
    id: int
    username: str
    display_name: Optional[str]
    avatar_url: Optional[str]
    role: str
    is_online: bool
    joined_at: datetime

    class Config:
        from_attributes = True


class ChannelResponse(BaseModel):
    id: int
    name: str
    username: Optional[str]
    description: Optional[str]
    avatar_url: Optional[str]
    channel_type: str
    invite_link: Optional[str]
    owner_id: int
    member_count: int
    is_member: bool
    member_role: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CreatePostRequest(BaseModel):
    content: str = Field(..., min_length=1)
    message_type: MessageType = MessageType.TEXT


class PostAttachmentResponse(BaseModel):
    id: int
    file_url: str
    file_name: str
    file_size: int
    file_type: str
    attachment_type: str
    thumbnail_url: Optional[str]
    width: Optional[int]
    height: Optional[int]
    duration: Optional[int]

    class Config:
        from_attributes = True


class PostResponse(BaseModel):
    id: int
    channel_id: int
    author_id: int
    author_username: str
    author_display_name: Optional[str]
    author_avatar_url: Optional[str]
    content: str
    message_type: str
    attachments: List[PostAttachmentResponse]
    created_at: datetime
    edited_at: Optional[datetime]

    class Config:
        from_attributes = True


def generate_invite_link() -> str:
    """Generate a unique invite link for private channels"""
    chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(16))


@router.post("/", response_model=ChannelResponse)
async def create_channel(
    channel_data: CreateChannelRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new channel (public or private)
    """
    # Validate username for public channels
    if channel_data.channel_type == ChannelType.PUBLIC:
        if not channel_data.username:
            raise HTTPException(status_code=400, detail="Public channels require a username")
        
        # Check if username is already taken
        username = f"@{channel_data.username}" if not channel_data.username.startswith("@") else channel_data.username
        stmt = select(Channel).where(Channel.username == username)
        result = await db.execute(stmt)
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Username already taken")
    else:
        username = None
    
    # Generate invite link for private channels
    invite_link = None
    if channel_data.channel_type == ChannelType.PRIVATE:
        invite_link = generate_invite_link()
    
    # Create channel
    channel = Channel(
        name=channel_data.name,
        username=username,
        description=channel_data.description,
        avatar_url=channel_data.avatar_url,
        channel_type=channel_data.channel_type,
        invite_link=invite_link,
        owner_id=current_user.id,
        member_count=1
    )
    
    db.add(channel)
    await db.flush()
    
    # Add owner as member with OWNER role
    stmt = channel_members.insert().values(
        channel_id=channel.id,
        user_id=current_user.id,
        role=ChannelMemberRole.OWNER,
        joined_at=datetime.utcnow()
    )
    await db.execute(stmt)
    await db.commit()
    await db.refresh(channel)
    
    return ChannelResponse(
        id=channel.id,
        name=channel.name,
        username=channel.username,
        description=channel.description,
        avatar_url=channel.avatar_url,
        channel_type=channel.channel_type.value,
        invite_link=channel.invite_link,
        owner_id=channel.owner_id,
        member_count=channel.member_count,
        is_member=True,
        member_role=ChannelMemberRole.OWNER.value,
        created_at=channel.created_at,
        updated_at=channel.updated_at
    )


@router.get("/{channel_id}", response_model=ChannelResponse)
async def get_channel(
    channel_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get channel details by ID
    """
    stmt = select(Channel).where(Channel.id == channel_id, Channel.is_active == True)
    result = await db.execute(stmt)
    channel = result.scalar_one_or_none()
    
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    # Check if user is a member
    stmt = select(channel_members).where(
        channel_members.c.channel_id == channel_id,
        channel_members.c.user_id == current_user.id
    )
    result = await db.execute(stmt)
    membership = result.first()
    
    is_member = membership is not None
    member_role = membership.role.value if membership else None
    
    # Hide invite link if not a member
    invite_link = channel.invite_link if is_member else None
    
    return ChannelResponse(
        id=channel.id,
        name=channel.name,
        username=channel.username,
        description=channel.description,
        avatar_url=channel.avatar_url,
        channel_type=channel.channel_type.value,
        invite_link=invite_link,
        owner_id=channel.owner_id,
        member_count=channel.member_count,
        is_member=is_member,
        member_role=member_role,
        created_at=channel.created_at,
        updated_at=channel.updated_at
    )


@router.get("/username/{username}", response_model=ChannelResponse)
async def get_channel_by_username(
    username: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get channel by username (@channelname)
    """
    # Remove @ if present
    if username.startswith("@"):
        username = username[1:]
    
    stmt = select(Channel).where(
        Channel.username == f"@{username}",
        Channel.is_active == True
    )
    result = await db.execute(stmt)
    channel = result.scalar_one_or_none()
    
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    # Check if user is a member
    stmt = select(channel_members).where(
        channel_members.c.channel_id == channel.id,
        channel_members.c.user_id == current_user.id
    )
    result = await db.execute(stmt)
    membership = result.first()
    
    is_member = membership is not None
    member_role = membership.role.value if membership else None
    
    # Hide invite link if not a member
    invite_link = channel.invite_link if is_member else None
    
    return ChannelResponse(
        id=channel.id,
        name=channel.name,
        username=channel.username,
        description=channel.description,
        avatar_url=channel.avatar_url,
        channel_type=channel.channel_type.value,
        invite_link=invite_link,
        owner_id=channel.owner_id,
        member_count=channel.member_count,
        is_member=is_member,
        member_role=member_role,
        created_at=channel.created_at,
        updated_at=channel.updated_at
    )


@router.put("/{channel_id}", response_model=ChannelResponse)
async def update_channel(
    channel_id: int,
    update_data: UpdateChannelRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update channel information (owner or admin only)
    """
    # Get channel
    stmt = select(Channel).where(Channel.id == channel_id, Channel.is_active == True)
    result = await db.execute(stmt)
    channel = result.scalar_one_or_none()
    
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    # Check permissions
    stmt = select(channel_members).where(
        channel_members.c.channel_id == channel_id,
        channel_members.c.user_id == current_user.id
    )
    result = await db.execute(stmt)
    membership = result.first()
    
    if not membership or membership.role not in [ChannelMemberRole.OWNER, ChannelMemberRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    # Update fields
    if update_data.name is not None:
        channel.name = update_data.name
    
    if update_data.description is not None:
        channel.description = update_data.description
    
    if update_data.avatar_url is not None:
        channel.avatar_url = update_data.avatar_url
    
    if update_data.username is not None and channel.channel_type == ChannelType.PUBLIC:
        username = f"@{update_data.username}" if not update_data.username.startswith("@") else update_data.username
        # Check if username is already taken
        stmt = select(Channel).where(Channel.username == username, Channel.id != channel_id)
        result = await db.execute(stmt)
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Username already taken")
        channel.username = username
    
    channel.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(channel)
    
    return ChannelResponse(
        id=channel.id,
        name=channel.name,
        username=channel.username,
        description=channel.description,
        avatar_url=channel.avatar_url,
        channel_type=channel.channel_type.value,
        invite_link=channel.invite_link,
        owner_id=channel.owner_id,
        member_count=channel.member_count,
        is_member=True,
        member_role=membership.role.value,
        created_at=channel.created_at,
        updated_at=channel.updated_at
    )


@router.post("/{channel_id}/join", response_model=ChannelResponse)
async def join_channel(
    channel_id: int,
    invite_code: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Join a channel (public or via invite link)
    """
    # Get channel
    stmt = select(Channel).where(Channel.id == channel_id, Channel.is_active == True)
    result = await db.execute(stmt)
    channel = result.scalar_one_or_none()
    
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    # Check if already a member
    stmt = select(channel_members).where(
        channel_members.c.channel_id == channel_id,
        channel_members.c.user_id == current_user.id
    )
    result = await db.execute(stmt)
    if result.first():
        raise HTTPException(status_code=400, detail="Already a member")
    
    # Validate access
    if channel.channel_type == ChannelType.PRIVATE:
        if not invite_code or invite_code != channel.invite_link:
            raise HTTPException(status_code=403, detail="Invalid invite code")
    
    # Add member
    stmt = channel_members.insert().values(
        channel_id=channel_id,
        user_id=current_user.id,
        role=ChannelMemberRole.MEMBER,
        joined_at=datetime.utcnow()
    )
    await db.execute(stmt)
    
    # Update member count
    channel.member_count += 1
    await db.commit()
    await db.refresh(channel)
    
    return ChannelResponse(
        id=channel.id,
        name=channel.name,
        username=channel.username,
        description=channel.description,
        avatar_url=channel.avatar_url,
        channel_type=channel.channel_type.value,
        invite_link=channel.invite_link,
        owner_id=channel.owner_id,
        member_count=channel.member_count,
        is_member=True,
        member_role=ChannelMemberRole.MEMBER.value,
        created_at=channel.created_at,
        updated_at=channel.updated_at
    )


@router.post("/{channel_id}/leave")
async def leave_channel(
    channel_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Leave a channel
    """
    # Get channel
    stmt = select(Channel).where(Channel.id == channel_id, Channel.is_active == True)
    result = await db.execute(stmt)
    channel = result.scalar_one_or_none()
    
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    # Check if member
    stmt = select(channel_members).where(
        channel_members.c.channel_id == channel_id,
        channel_members.c.user_id == current_user.id
    )
    result = await db.execute(stmt)
    membership = result.first()
    
    if not membership:
        raise HTTPException(status_code=400, detail="Not a member")
    
    # Owner cannot leave
    if membership.role == ChannelMemberRole.OWNER:
        raise HTTPException(status_code=400, detail="Owner cannot leave channel")
    
    # Remove member
    stmt = delete(channel_members).where(
        channel_members.c.channel_id == channel_id,
        channel_members.c.user_id == current_user.id
    )
    await db.execute(stmt)
    
    # Update member count
    channel.member_count -= 1
    await db.commit()
    
    return {"message": "Left channel successfully"}


@router.get("/{channel_id}/members", response_model=List[ChannelMemberResponse])
async def get_channel_members(
    channel_id: int,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get channel members list
    """
    # Check if user is a member
    stmt = select(channel_members).where(
        channel_members.c.channel_id == channel_id,
        channel_members.c.user_id == current_user.id
    )
    result = await db.execute(stmt)
    if not result.first():
        raise HTTPException(status_code=403, detail="Not a member of this channel")
    
    # Get members
    stmt = (
        select(User, channel_members.c.role, channel_members.c.joined_at)
        .join(channel_members, User.id == channel_members.c.user_id)
        .where(channel_members.c.channel_id == channel_id)
        .order_by(channel_members.c.joined_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(stmt)
    members = result.all()
    
    return [
        ChannelMemberResponse(
            id=user.id,
            username=user.username,
            display_name=user.display_name,
            avatar_url=user.avatar_url,
            role=role.value,
            is_online=user.is_online,
            joined_at=joined_at
        )
        for user, role, joined_at in members
    ]


@router.post("/{channel_id}/posts", response_model=PostResponse)
async def create_post(
    channel_id: int,
    post_data: CreatePostRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new post in a channel
    """
    # Check if user is a member with posting permissions
    stmt = select(channel_members).where(
        channel_members.c.channel_id == channel_id,
        channel_members.c.user_id == current_user.id
    )
    result = await db.execute(stmt)
    membership = result.first()
    
    if not membership:
        raise HTTPException(status_code=403, detail="Not a member of this channel")
    
    # Only admins and owners can post
    if membership.role not in [ChannelMemberRole.OWNER, ChannelMemberRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Insufficient permissions to post")
    
    # Create post
    post = ChannelPost(
        channel_id=channel_id,
        author_id=current_user.id,
        content=post_data.content,
        message_type=post_data.message_type
    )
    
    db.add(post)
    await db.commit()
    await db.refresh(post)
    
    return PostResponse(
        id=post.id,
        channel_id=post.channel_id,
        author_id=post.author_id,
        author_username=current_user.username,
        author_display_name=current_user.display_name,
        author_avatar_url=current_user.avatar_url,
        content=post.content,
        message_type=post.message_type.value,
        attachments=[],
        created_at=post.created_at,
        edited_at=post.edited_at
    )


@router.get("/{channel_id}/posts", response_model=List[PostResponse])
async def get_channel_posts(
    channel_id: int,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get posts from a channel
    """
    # Check if user is a member
    stmt = select(channel_members).where(
        channel_members.c.channel_id == channel_id,
        channel_members.c.user_id == current_user.id
    )
    result = await db.execute(stmt)
    if not result.first():
        raise HTTPException(status_code=403, detail="Not a member of this channel")
    
    # Get posts
    stmt = (
        select(ChannelPost, User)
        .join(User, ChannelPost.author_id == User.id)
        .where(
            ChannelPost.channel_id == channel_id,
            ChannelPost.deleted_at.is_(None)
        )
        .order_by(ChannelPost.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(stmt)
    posts = result.all()
    
    # Get attachments for all posts
    post_ids = [post.id for post, _ in posts]
    stmt = select(PostAttachment).where(PostAttachment.post_id.in_(post_ids))
    result = await db.execute(stmt)
    attachments_dict = {}
    for attachment in result.scalars().all():
        if attachment.post_id not in attachments_dict:
            attachments_dict[attachment.post_id] = []
        attachments_dict[attachment.post_id].append(attachment)
    
    return [
        PostResponse(
            id=post.id,
            channel_id=post.channel_id,
            author_id=post.author_id,
            author_username=author.username,
            author_display_name=author.display_name,
            author_avatar_url=author.avatar_url,
            content=post.content,
            message_type=post.message_type.value,
            attachments=[
                PostAttachmentResponse(
                    id=att.id,
                    file_url=att.file_url,
                    file_name=att.file_name,
                    file_size=att.file_size,
                    file_type=att.file_type,
                    attachment_type=att.attachment_type.value,
                    thumbnail_url=att.thumbnail_url,
                    width=att.width,
                    height=att.height,
                    duration=att.duration
                )
                for att in attachments_dict.get(post.id, [])
            ],
            created_at=post.created_at,
            edited_at=post.edited_at
        )
        for post, author in posts
    ]


@router.get("/", response_model=List[ChannelResponse])
async def get_my_channels(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all channels the current user is a member of
    """
    stmt = (
        select(Channel, channel_members.c.role)
        .join(channel_members, Channel.id == channel_members.c.channel_id)
        .where(
            channel_members.c.user_id == current_user.id,
            Channel.is_active == True
        )
        .order_by(Channel.updated_at.desc())
    )
    result = await db.execute(stmt)
    channels = result.all()
    
    return [
        ChannelResponse(
            id=channel.id,
            name=channel.name,
            username=channel.username,
            description=channel.description,
            avatar_url=channel.avatar_url,
            channel_type=channel.channel_type.value,
            invite_link=channel.invite_link,
            owner_id=channel.owner_id,
            member_count=channel.member_count,
            is_member=True,
            member_role=role.value,
            created_at=channel.created_at,
            updated_at=channel.updated_at
        )
        for channel, role in channels
    ]