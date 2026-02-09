from fastapi import APIRouter, UploadFile, File, Form, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session
from app.services.file_service import FileService
from app.core.dependencies import get_db, require_admin
import os

router = APIRouter(prefix="/files", tags=["Files"])

@router.post("/upload/init", response_model=dict)
def init_upload(
    filename: str = Form(...),
):
    upload_id = FileService.init_upload(filename)
    return {
        "upload_id": upload_id,
        "filename": filename
    }

@router.post("/upload/chunk", response_model=dict)
async def upload_chunk(
    upload_id: str = Form(...),
    chunk_index: int = Form(...),
    total_chunks: int = Form(...),
    chunk: UploadFile = File(...),
):
    # Log for debugging 404
    print(f"[DEBUG] upload_chunk: upload_id={upload_id}, chunk_index={chunk_index}")
    
    success = await FileService.upload_chunk(upload_id, chunk_index, chunk)
    return {
        "chunk_index": chunk_index,
        "status": "ok"
    }

@router.post("/upload/complete", response_model=dict)
def complete_upload(
    upload_id: str = Form(...),
    total_chunks: int = Form(...),
    filename: str = Form(...),
    db: Session = Depends(get_db)
):
    file_record = FileService.complete_upload(db, upload_id, total_chunks, filename)
    return {
        "object_name": file_record.file_path,
        "url": file_record.file_url,
        "fileId": file_record.id,
        "fileName": file_record.file_name,
        "fileSize": file_record.file_size
    }

@router.get("/{file_id}")
def download_file(
    file_id: str,
    db: Session = Depends(get_db)
):
    file_record = FileService.get_file(db, file_id)
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")
    
    from fastapi.responses import StreamingResponse, Response
    from app.services.minio import get_object
    from app.core.redis import redis_client
    import io
    from PIL import Image

    # --- IMAGE OPTIMIZATION & CACHING ---
    if file_record.mime_type.startswith("image/"):
        cache_key = f"img_cache_60_{file_id}"
        try:
            cached_data = redis_client.get(cache_key)
            if cached_data:
                return Response(
                    content=cached_data,
                    media_type="image/webp",
                    headers={"Content-Disposition": f"inline; filename={file_record.id}.webp"}
                )
        except Exception as e:
            print(f"[REDIS ERROR] {e}")

        # Not in cache or Redis failed, generate WebP
        try:
            minio_response = get_object(file_record.file_path)
            img_data = minio_response.read()
            
            with Image.open(io.BytesIO(img_data)) as img:
                # Convert to RGB if necessary (WEBP quality lossy needs RGB/RGBA)
                if img.mode not in ("RGB", "RGBA"):
                    img = img.convert("RGBA")
                
                output = io.BytesIO()
                img.save(output, format="WEBP", quality=60)
                webp_bytes = output.getvalue()
                
                # Store in Redis (cache for 7 days)
                try:
                    redis_client.setex(cache_key, 604800, webp_bytes)
                except:
                    pass
                
                return Response(
                    content=webp_bytes,
                    media_type="image/webp",
                    headers={"Content-Disposition": f"inline; filename={file_record.id}.webp"}
                )
        except Exception as e:
            print(f"[IMAGE OPT ERROR] {e}")
            # Fallback to original below

    try:
        response = get_object(file_record.file_path)
        return StreamingResponse(
            response,
            media_type=file_record.mime_type,
            headers={"Content-Disposition": f"inline; filename={file_record.file_name}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{file_id}", response_model=dict)
def delete_file(
    file_id: str,
    db: Session = Depends(get_db),
    token: dict = Depends(require_admin) # As per spec
):
    success = FileService.delete_file(db, file_id)
    if not success:
         raise HTTPException(status_code=404, detail="File not found")
         
    return {
        "success": True,
        "message": "Đã xóa file thành công"
    }

# Legacy support if needed, but risky to keep old signatures if they conflict.
# Old: GET /files/download/{object_name}
# Old: GET /files/delete/{object_name}
# New DELETE is /files/:id which overlaps if ID looks like object_name.
# I'll omit legacy endpoints to ensure robust new implementation.
