from typing import Optional, BinaryIO
from pathlib import Path
import os
import uuid
from fastapi import UploadFile
from app.core.config import settings

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
ALLOWED_DOCUMENT_TYPES = {"application/pdf", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}
MAX_FILE_SIZE = settings.MAX_UPLOAD_SIZE

class FileStorage:
    def __init__(self):
        self.storage_type = settings.STORAGE_TYPE
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    async def save_upload(self, file: UploadFile, subdir: str = "general") -> str:
        if file.size and file.size > MAX_FILE_SIZE:
            raise ValueError(f"File size exceeds maximum {MAX_FILE_SIZE // 1024 // 1024}MB")
        
        ext = os.path.splitext(file.filename or "file")[1] if file.filename else ""
        filename = f"{uuid.uuid4().hex}{ext}"
        
        save_dir = self.upload_dir / subdir
        save_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = save_dir / filename
        content = await file.read()
        
        if self.storage_type == "s3":
            return self._save_to_s3(content, filename, subdir)
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        return str(file_path)

    async def save_image(self, file: UploadFile) -> str:
        if file.content_type not in ALLOWED_IMAGE_TYPES:
            raise ValueError(f"Invalid image type: {file.content_type}")
        return await self.save_upload(file, "images")

    async def save_document(self, file: UploadFile) -> str:
        if file.content_type not in ALLOWED_DOCUMENT_TYPES:
            raise ValueError(f"Invalid document type: {file.content_type}")
        return await self.save_upload(file, "documents")

    def _save_to_s3(self, content: bytes, filename: str, subdir: str) -> str:
        try:
            import boto3
            s3 = boto3.client(
                "s3",
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION,
            )
            key = f"{subdir}/{filename}"
            s3.put_object(Bucket=settings.AWS_S3_BUCKET, Key=key, Body=content)
            return f"https://{settings.AWS_S3_BUCKET}.s3.{settings.AWS_REGION}.amazonaws.com/{key}"
        except ImportError:
            raise ValueError("boto3 not installed")
        except Exception as e:
            raise ValueError(f"S3 upload failed: {str(e)}")

    def delete_file(self, file_path: str) -> bool:
        if self.storage_type == "s3":
            return self._delete_from_s3(file_path)
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
                return True
            return False
        except Exception:
            return False

    def _delete_from_s3(self, url: str) -> bool:
        try:
            import boto3
            s3 = boto3.client("s3")
            # Parse key from URL
            key = "/".join(url.split("/")[3:])
            s3.delete_object(Bucket=settings.AWS_S3_BUCKET, Key=key)
            return True
        except Exception:
            return False

file_storage = FileStorage()
