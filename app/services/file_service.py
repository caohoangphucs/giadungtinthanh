import os
import shutil
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from app.services.minio import upload_file, get_public_url, delete_object
from app.services.clean import cleanup_tmp_chunks # Assuming this exists
from app.models.file import File
from datetime import datetime
import mimetypes

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CHUNK_TMP_DIR = os.path.join(BASE_DIR, "tmp_chunks")
from .common import *


    


class FileService:
    @staticmethod
    def init_upload(filename: str) -> str:
        import uuid
        upload_id = str(uuid.uuid4())
        upload_dir = os.path.join(CHUNK_TMP_DIR, upload_id)
        os.makedirs(upload_dir, exist_ok=True)
        return upload_id

    @staticmethod
    async def upload_chunk(upload_id: str, chunk_index: int, chunk: UploadFile):
        upload_dir = os.path.join(CHUNK_TMP_DIR, upload_id)
        if not os.path.exists(upload_dir):
            raise HTTPException(status_code=404, detail="Upload session not found")
        
        chunk_path = os.path.join(upload_dir, f"{chunk_index}.part")
        
        content = await chunk.read()
        with open(chunk_path, "wb") as f:
            f.write(content)
            
        return True

    @staticmethod
    def complete_upload(db: Session, upload_id: str, total_chunks: int, filename: str) -> File:
        upload_dir = os.path.join(CHUNK_TMP_DIR, upload_id)
        if not os.path.exists(upload_dir):
            raise HTTPException(status_code=404, detail="Upload session not found")
            
        merged_path = os.path.join(upload_dir, filename)
        
        # Merge chunks
        with open(merged_path, "wb") as merged:
            for i in range(total_chunks):
                part_path = os.path.join(upload_dir, f"{i}.part")
                if not os.path.exists(part_path):
                    raise HTTPException(status_code=400, detail=f"Missing chunk {i}")
                
                with open(part_path, "rb") as part:
                    shutil.copyfileobj(part, merged)
        
        # Get file size
        file_size = os.path.getsize(merged_path)
        
        # Guess mime type
        mime_type, _ = mimetypes.guess_type(filename)
        if not mime_type:
            mime_type = "application/octet-stream"
            
        # Upload to MinIO
        with open(merged_path, "rb") as f:
            object_name = upload_file(f, content_type=mime_type, length=file_size)
        
        preview_path = None
        # Generate WebP Preview for images
        if mime_type.startswith("image/"):
            try:
                from PIL import Image, ImageOps
                import io
                with Image.open(merged_path) as img:
                    # Fix orientation based on EXIF data
                    img = ImageOps.exif_transpose(img)
                    
                    # Convert to RGB if necessary
                    if img.mode not in ("RGB", "RGBA"):
                        img = img.convert("RGBA")
                    
                    output = io.BytesIO()
                    img.save(output, format="WEBP", quality=60)
                    webp_bytes = output.getvalue()
                    
                    # Upload preview to MinIO
                    preview_object_name = f"previews/{upload_id}.webp"
                    preview_data = io.BytesIO(webp_bytes)
                    upload_file(preview_data, content_type="image/webp", length=len(webp_bytes), custom_name=preview_object_name)
                    preview_path = preview_object_name
            except Exception as e:
                print(f"[PREVIEW GEN ERROR] {e}")

        file_url = f"/api/files/{upload_id}"
        
        # Save to DB
        new_file = File(
            id=upload_id, 
            file_name=filename,
            file_path=object_name,
            preview_path=preview_path,
            file_url=file_url,
            file_size=file_size,
            mime_type=mime_type,
            file_type="article"
        )
        db.add(new_file)
        db.commit()
        db.refresh(new_file)
        
        # Cleanup
        try:
            shutil.rmtree(upload_dir, ignore_errors=True)
        except:
            pass
        
        return new_file

    @staticmethod
    def get_file(db: Session, file_id: str) -> File:
        return db.query(File).filter(File.id == file_id).first()

    @staticmethod
    def delete_file(db: Session, file_id: str) -> bool:
        file_record = db.query(File).filter(File.id == file_id).first()
        if not file_record:
            return False
        
        # Delete from MinIO
        delete_object(file_record.file_path)
        if file_record.preview_path:
            delete_object(file_record.preview_path)
        
        # Delete from DB
        db.delete(file_record)
        db.commit()
        return True
