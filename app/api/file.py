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
    # Spec says: Response Headers: Content-Type, Content-Disposition
    # And binary body.
    # But FileService uploads to MinIO and stores URL.
    # If the file is public (MinIO), we can redirect or proxy.
    # Spec says: "Client fetch file từ fileUrl".
    # But also "GET /files/:fileId" -> "Binary file content".
    # If fileUrl is "https://storage...", client can fetch directly.
    # But if endpoint is `/files/:fileId`, it acts as proxy or redirect.
    # I'll implement a RedirectResponse to the MinIO URL if possible, or stream it.
    # Streaming is heavier. Redirect is better if MinIO is public.
    
    file_record = FileService.get_file(db, file_id)
    if not file_record:
        # Fallback to check if it's an object name (legacy support)
        # But for now strictly follow ID.
        raise HTTPException(status_code=404, detail="File not found")
    
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url=file_record.file_url)

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
