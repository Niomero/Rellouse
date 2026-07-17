"""
Upload Router
Handles file uploads: images, videos, audio, files
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from pydantic import BaseModel
import os
import uuid
import mimetypes
from pathlib import Path
from PIL import Image
import io

from database import get_db
from models import User, AttachmentType
from auth import get_current_user

router = APIRouter(prefix="/api/upload", tags=["upload"])

# Configuration
UPLOAD_DIR = Path("uploads")
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
ALLOWED_VIDEO_TYPES = {"video/mp4", "video/webm", "video/quicktime"}
ALLOWED_AUDIO_TYPES = {"audio/mpeg", "audio/ogg", "audio/wav", "audio/webm"}
ALLOWED_FILE_TYPES = {
    "application/pdf",
    "application/zip",
    "application/x-rar-compressed",
    "text/plain",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}

# Ensure upload directories exist
for subdir in ["images", "videos", "audio", "files", "thumbnails"]:
    (UPLOAD_DIR / subdir).mkdir(parents=True, exist_ok=True)


class UploadResponse(BaseModel):
    file_url: str
    file_name: str
    file_size: int
    file_type: str
    attachment_type: str
    thumbnail_url: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    duration: Optional[int] = None


def get_attachment_type(mime_type: str) -> AttachmentType:
    """Determine attachment type from MIME type"""
    if mime_type in ALLOWED_IMAGE_TYPES:
        return AttachmentType.IMAGE
    elif mime_type in ALLOWED_VIDEO_TYPES:
        return AttachmentType.VIDEO
    elif mime_type in ALLOWED_AUDIO_TYPES:
        return AttachmentType.AUDIO
    else:
        return AttachmentType.FILE


def generate_thumbnail(image_path: Path, thumbnail_path: Path, size=(300, 300)):
    """Generate thumbnail for image"""
    try:
        with Image.open(image_path) as img:
            # Convert RGBA to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # Create thumbnail
            img.thumbnail(size, Image.Resampling.LANCZOS)
            img.save(thumbnail_path, "JPEG", quality=85, optimize=True)
            return True
    except Exception as e:
        print(f"Error generating thumbnail: {e}")
        return False


@router.post("/image", response_model=UploadResponse)
async def upload_image(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload an image file
    """
    # Validate file type
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail="Invalid image type")
    
    # Read file content
    content = await file.read()
    file_size = len(content)
    
    # Validate file size
    if file_size > MAX_IMAGE_SIZE:
        raise HTTPException(status_code=400, detail="Image too large (max 10MB)")
    
    # Generate unique filename
    file_extension = Path(file.filename).suffix or ".jpg"
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = UPLOAD_DIR / "images" / unique_filename
    
    # Save file
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Get image dimensions
    width, height = None, None
    try:
        with Image.open(file_path) as img:
            width, height = img.size
    except Exception as e:
        print(f"Error reading image dimensions: {e}")
    
    # Generate thumbnail
    thumbnail_filename = f"thumb_{unique_filename}"
    thumbnail_path = UPLOAD_DIR / "thumbnails" / thumbnail_filename
    thumbnail_url = None
    
    if generate_thumbnail(file_path, thumbnail_path):
        thumbnail_url = f"/uploads/thumbnails/{thumbnail_filename}"
    
    return UploadResponse(
        file_url=f"/uploads/images/{unique_filename}",
        file_name=file.filename,
        file_size=file_size,
        file_type=file.content_type,
        attachment_type=AttachmentType.IMAGE.value,
        thumbnail_url=thumbnail_url,
        width=width,
        height=height
    )


@router.post("/video", response_model=UploadResponse)
async def upload_video(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a video file
    """
    # Validate file type
    if file.content_type not in ALLOWED_VIDEO_TYPES:
        raise HTTPException(status_code=400, detail="Invalid video type")
    
    # Read file content
    content = await file.read()
    file_size = len(content)
    
    # Validate file size
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="Video too large (max 50MB)")
    
    # Generate unique filename
    file_extension = Path(file.filename).suffix or ".mp4"
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = UPLOAD_DIR / "videos" / unique_filename
    
    # Save file
    with open(file_path, "wb") as f:
        f.write(content)
    
    return UploadResponse(
        file_url=f"/uploads/videos/{unique_filename}",
        file_name=file.filename,
        file_size=file_size,
        file_type=file.content_type,
        attachment_type=AttachmentType.VIDEO.value
    )


@router.post("/audio", response_model=UploadResponse)
async def upload_audio(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload an audio file
    """
    # Validate file type
    if file.content_type not in ALLOWED_AUDIO_TYPES:
        raise HTTPException(status_code=400, detail="Invalid audio type")
    
    # Read file content
    content = await file.read()
    file_size = len(content)
    
    # Validate file size
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="Audio too large (max 50MB)")
    
    # Generate unique filename
    file_extension = Path(file.filename).suffix or ".mp3"
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = UPLOAD_DIR / "audio" / unique_filename
    
    # Save file
    with open(file_path, "wb") as f:
        f.write(content)
    
    return UploadResponse(
        file_url=f"/uploads/audio/{unique_filename}",
        file_name=file.filename,
        file_size=file_size,
        file_type=file.content_type,
        attachment_type=AttachmentType.AUDIO.value
    )


@router.post("/file", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a general file
    """
    # Validate file type
    if file.content_type not in ALLOWED_FILE_TYPES:
        raise HTTPException(status_code=400, detail="File type not allowed")
    
    # Read file content
    content = await file.read()
    file_size = len(content)
    
    # Validate file size
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large (max 50MB)")
    
    # Generate unique filename
    file_extension = Path(file.filename).suffix or ".bin"
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = UPLOAD_DIR / "files" / unique_filename
    
    # Save file
    with open(file_path, "wb") as f:
        f.write(content)
    
    return UploadResponse(
        file_url=f"/uploads/files/{unique_filename}",
        file_name=file.filename,
        file_size=file_size,
        file_type=file.content_type,
        attachment_type=AttachmentType.FILE.value
    )


@router.post("/avatar", response_model=UploadResponse)
async def upload_avatar(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload user avatar (optimized for profile pictures)
    """
    # Validate file type
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail="Invalid image type")
    
    # Read file content
    content = await file.read()
    file_size = len(content)
    
    # Validate file size
    if file_size > MAX_IMAGE_SIZE:
        raise HTTPException(status_code=400, detail="Image too large (max 10MB)")
    
    # Generate unique filename
    unique_filename = f"avatar_{current_user.id}_{uuid.uuid4()}.jpg"
    file_path = UPLOAD_DIR / "images" / unique_filename
    
    # Process and save avatar
    try:
        with Image.open(io.BytesIO(content)) as img:
            # Convert to RGB
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # Resize to square (max 512x512)
            size = min(img.size)
            left = (img.width - size) // 2
            top = (img.height - size) // 2
            img = img.crop((left, top, left + size, top + size))
            
            if size > 512:
                img = img.resize((512, 512), Image.Resampling.LANCZOS)
            
            # Save optimized
            img.save(file_path, "JPEG", quality=90, optimize=True)
            
            width, height = img.size
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing image: {str(e)}")
    
    # Generate thumbnail
    thumbnail_filename = f"thumb_{unique_filename}"
    thumbnail_path = UPLOAD_DIR / "thumbnails" / thumbnail_filename
    thumbnail_url = None
    
    if generate_thumbnail(file_path, thumbnail_path, size=(150, 150)):
        thumbnail_url = f"/uploads/thumbnails/{thumbnail_filename}"
    
    return UploadResponse(
        file_url=f"/uploads/images/{unique_filename}",
        file_name=file.filename,
        file_size=os.path.getsize(file_path),
        file_type="image/jpeg",
        attachment_type=AttachmentType.IMAGE.value,
        thumbnail_url=thumbnail_url,
        width=width,
        height=height
    )
