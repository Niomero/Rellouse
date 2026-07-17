"""
Channel Router
Handles channel creation, management, posts, and membership
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import secrets
import logging

from database import get_db
from models import User, Channel, ChannelPost, PostAttachment, ChannelType, ChannelMemberRole, channel_members
from auth import get_current_user

router = APIRouter(prefix="/api/channels", tags=["channels"])

logger = logging.getLogger(__name__)


# Request/Response Models
class CreateChannelRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    avatar_url: Optional[str] = None
    channel_type: str = Field(..., pattern="^(public|private)$")
    username: Optional[str] = Field(None, min_length=4, max_length=16)  # For public channels


class UpdateChannelRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    avatar_url: Optional[str] = None


class CreatePostRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=10000)
    attachment_urls: Optional[List[str]] = None


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
    
    class Config:
        from_attributes = True


class PostResponse(BaseModel):
    id: int
    channel_id: int
    author_id: int
    author_username: str
    author_display_name: Optional[str]
    author_avatar: Optional[str]
    content: str
    created_at: datetime
    edited_at: Optional[datetime]
    attachments: List[dict] = []
    
    class Config:
        from_attributes = True


class MemberResponse(BaseModel):
    user_id: int
    username: str
    display_name: Optional[str]
    avatar_url: Optional[str]
    role: str
    joined_at: datetime


@router.post("/create", response_model=ChannelResponse)
async def create_channel(
    request: CreateChannelRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new channel (public or private)
    """
    # Validate username for public channels
    if request.channel_type == "public":
        if not request.username:
            raise HTTPException(status_code=400, detail="Username is required for public channels")
        
        # Check if username is already taken
        username_with_at = f"@{request.username}"
        stmt = select(Channel).where(Channel.username == username_with_at)
        result = await db.execute(stmt)
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Username already taken")
    
    # Generate invite link for private channels
    invite_link = None
    if request.channel_type == "private":
        invite_link = f"https://rellouse.com/join/{secrets.token_urlsafe(16)}"
    
    # Create channel
    channel = Channel(
        name=request.name,
        username=f"@{request.username}" if request.username else None,
        description=request.description,
        avatar_url=request.avatar_url,
        channel_type=ChannelType.PUBLIC if request.channel_type == "public" else ChannelType.PRIVATE,
        invite_link=invite_link,
        owner_id=current_user.id,
        member_count=1,
        created_at=datetime.utcnow()
    )
    
    db.add(channel)
    await db.commit()
    await db.refresh(channel)
    
    # Add creator as owner member
    stmt = channel_members.insert().values(
        channel_id=channel.id,
        user_id=current_user.id,
        role=ChannelMemberRole.OWNER,
        joined_at=datetime.utcnow()
    )
    await db.execute(stmt)
    await db.commit()
    
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
        created_at=channel.created_at
    )


@router.get("/{channel_id}", response_model=ChannelResponse)
async def get_channel(
    channel_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get channel details
    """
    stmt = select(Channel).where(Channel.id == channel_id, Channel.is_active == True)
    result = await db.execute(stmt)
    channel = result.scalar_one_or_none()
    
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    # Check if user is member
    stmt = select(channel_members).where(
        channel_members.c.channel_id == channel_id,
        channel_members.c.user_id == current_user.id
    )
    result = await db.execute(stmt)
    membership = result.first()
    
    is_member = membership is not None
    member_role = membership.role.value if membership else None
    
    return ChannelResponse(
        id=channel.id,
        name=channel.name,
        username=channel.username,
        description=channel.description,
        avatar_url=channel.avatar_url,
        channel_type=channel.channel_type.value,
        invite_link=channel.invite_link if is_member else None,
        owner_id=channel.owner_id,
        member_count=channel.member_count,
        is_member=is_member,
        member_role=member_role,
        created_at=channel.created_at
    )


@router.put("/{channel_id}", response_model=ChannelResponse)
async def update_channel(
    channel_id: int,
    request: UpdateChannelRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update channel details (owner/admin only)
    """
    stmt = select(Channel).where(Channel.id == channel_id, Channel.is_active == True)
    result = await db.execute(stmt)
    channel = result.scalar_one_or_none()
    
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    # Check if user is owner or admin
    stmt = select(channel_members).where(
        channel_members.c.channel_id == channel_id,
        channel_members.c.user_id == current_user.id
    )
    result = await db.execute(stmt)
    membership = result.first()
    
    if not membership or membership.role not in [ChannelMemberRole.OWNER, ChannelMemberRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Only channel owner or admin can update channel")
    
    # Update fields
    if request.name is not None:
        channel.name = request.name
    if request.description is not None:
        channel.description = request.description
    if request.avatar_url is not None:
        channel.avatar_url = request.avatar_url
    
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
        created_at=channel.created_at
    )


@router.post("/{channel_id}/join")
async def join_channel(
    channel_id: int,
    invite_code: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Join a channel (public or by invite link)
    """
    stmt = select(Channel).where(Channel.id == channel_id, Channel.is_active == True)
    result = await db.execute(stmt)
    channel = result.scalar_one_or_none()
    
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    # Check if already member
    stmt = select(channel_members).where(
        channel_members.c.channel_id == channel_id,
        channel_members.c.user_id == current_user.id
    )
    result = await db.execute(stmt)
    if result.first():
        raise HTTPException(status_code=400, detail="Already a member of this channel")
    
    # Validate access
    if channel.channel_type == ChannelType.PRIVATE:
        if not invite_code or invite_code not in channel.invite_link:
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
    
    return {"success": True, "message": "Successfully joined channel"}


@router.post("/{channel_id}/leave")
async def leave_channel(
    channel_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Leave a channel
    """
    stmt = select(Channel).where(Channel.id == channel_id, Channel.is_active == True)
    result = await db.execute(stmt)
    channel = result.scalar_one_or_none()
    
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    # Check if owner
    if channel.owner_id == current_user.id:
        raise HTTPException(status_code=400, detail="Channel owner cannot leave. Transfer ownership or delete channel.")
    
    # Remove member
    stmt = channel_members.delete().where(
        channel_members.c.channel_id == channel_id,
        channel_members.c.user_id == current_user.id
    )
    result = await db.execute(stmt)
    
    if result.rowcount == 0:
        raise HTTPException(status_code=400, detail="Not a member of this channel")
    
    # Update member count
    channel.member_count -= 1
    await db.commit()
    
    return {"success": True, "message": "Successfully left channel"}


@router.post("/{channel_id}/posts", response_model=PostResponse)
async def create_post(
    channel_id: int,
    request: CreatePostRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a post in a channel (members only)
    """
    # Check if member
    stmt = select(channel_members).where(
        channel_members.c.channel_id == channel_id,
        channel_members.c.user_id == current_user.id
    )
    result = await db.execute(stmt)
    if not result.first():
        raise HTTPException(status_code=403, detail="Must be a member to post")
    
    # Create post
    post = ChannelPost(
        channel_id=channel_id,
        author_id=current_user.id,
        content=request.content,
        created_at=datetime.utcnow()
    )
    
    db.add(post)
    await db.commit()
    await db.refresh(post)
    
    # Handle attachments
    attachments = []
    if request.attachment_urls:
        for url in request.attachment_urls:
            attachment = PostAttachment(
                post_id=post.id,
                file_url=url,
                file_name=url.split("/")[-1],
                file_size=0,
                file_type="image/jpeg"
            )
            db.add(attachment)
            attachments.append({
                "file_url": url,
                "file_name": attachment.file_name,
                "file_type": attachment.file_type
            })
        
        await db.commit()
    
    return PostResponse(
        id=post.id,
        channel_id=post.channel_id,
        author_id=post.author_id,
        author_username=current_user.username,
        author_display_name=current_user.display_name,
        author_avatar=current_user.avatar_url,
        content=post.content,
        created_at=post.created_at,
        edited_at=post.edited_at,
        attachments=attachments
    )


@router.get("/{channel_id}/posts", response_model=List[PostResponse])
async def get_posts(
    channel_id: int,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get posts from a channel
    """
    # Check if member
    stmt = select(channel_members).where(
        channel_members.c.channel_id == channel_id,
        channel_members.c.user_id == current_user.id
    )
    result = await db.execute(stmt)
    if not result.first():
        raise HTTPException(status_code=403, detail="Must be a member to view posts")
    
    # Get posts
    stmt = select(ChannelPost).where(
        ChannelPost.channel_id == channel_id,
        ChannelPost.deleted_at.is_(None)
    ).order_by(ChannelPost.created_at.desc()).limit(limit).offset(offset)
    
    result = await db.execute(stmt)
    posts = result.scalars().all()
    
    # Format response
    response = []
    for post in reversed(posts):
        # Get author
        stmt = select(User).where(User.id == post.author_id)
        result = await db.execute(stmt)
        author = result.scalar_one_or_none()
        
        # Get attachments
        attachments = []
        for att in post.attachments:
            attachments.append({
                "file_url": att.file_url,
                "file_name": att.file_name,
                "file_type": att.file_type,
                "thumbnail_url": att.thumbnail_url
            })
        
        response.append(PostResponse(
            id=post.id,
            channel_id=post.channel_id,
            author_id=post.author_id,
            author_username=author.username if author else "Unknown",
            author_display_name=author.display_name if author else None,
            author_avatar=author.avatar_url if author else None,
            content=post.content,
            created_at=post.created_at,
            edited_at=post.edited_at,
            attachments=attachments
        ))
    
    return response


@router.get("/{channel_id}/members", response_model=List[MemberResponse])
async def get_members(
    channel_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get channel members list
    """
    # Check if member
    stmt = select(channel_members).where(
        channel_members.c.channel_id == channel_id,
        channel_members.c.user_id == current_user.id
    )
    result = await db.execute(stmt)
    if not result.first():
        raise HTTPException(status_code=403, detail="Must be a member to view members")
    
    # Get all members
    stmt = select(channel_members).where(channel_members.c.channel_id == channel_id)
    result = await db.execute(stmt)
    memberships = result.all()
    
    response = []
    for membership in memberships:
        # Get user info
        stmt = select(User).where(User.id == membership.user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if user:
            response.append(MemberResponse(
                user_id=user.id,
                username=user.username,
                display_name=user.display_name,
                avatar_url=user.avatar_url,
                role=membership.role.value,
                joined_at=membership.joined_at
            ))
    
    return response


@router.get("/list/my", response_model=List[ChannelResponse])
async def get_my_channels(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of channels user is a member of
    """
    # Get user's channel memberships
    stmt = select(channel_members).where(channel_members.c.user_id == current_user.id)
    result = await db.execute(stmt)
    memberships = result.all()
    
    response = []
    for membership in memberships:
        # Get channel info
        stmt = select(Channel).where(
            Channel.id == membership.channel_id,
            Channel.is_active == True
        )
        result = await db.execute(stmt)
        channel = result.scalar_one_or_none()
        
        if channel:
            response.append(ChannelResponse(
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
                created_at=channel.created_at
            ))
    
    return response
