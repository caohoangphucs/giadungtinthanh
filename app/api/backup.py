import os
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from app.services.backup_service import BackupService

router = APIRouter(prefix="/backup", tags=["Backup"])

def cleanup_file(path: str):
    if os.path.exists(path):
        os.remove(path)

@router.post("/start")
async def start_backup(background_tasks: BackgroundTasks):
    progress = BackupService.get_progress()
    if progress["status"] == "running":
        return {"message": "Backup is already in progress"}
    
    # Reset progress and start
    background_tasks.add_task(BackupService.create_full_backup_zip)
    return {"message": "Backup started"}

@router.get("/status")
async def get_backup_status():
    return BackupService.get_progress()

@router.get("/download")
async def download_backup(background_tasks: BackgroundTasks):
    progress = BackupService.get_progress()
    if progress["status"] != "completed" or not progress["last_zip"]:
        raise HTTPException(status_code=400, detail="Backup not ready or not found")
    
    zip_path = progress["last_zip"]
    if not os.path.exists(zip_path):
        raise HTTPException(status_code=404, detail="Backup file missing")

    # Clear last_zip after starting download to prevent double usage and trigger cleanup later
    # Actually, we should cleanup after some time or another way. 
    # For simplicity, we'll schedule cleanup on download.
    background_tasks.add_task(cleanup_file, zip_path)
    
    # IMPORTANT: We need to reset the status so next backup can start
    # but only after download starts.
    progress["status"] = "idle"
    progress["last_zip"] = ""
    
    return FileResponse(
        path=zip_path,
        filename=os.path.basename(zip_path),
        media_type='application/zip'
    )
