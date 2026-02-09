import os
import shutil
import subprocess
import zipfile
from datetime import datetime
from app.core.config import settings
from app.core.minio import client
from app.services.minio import MINIO_BUCKET

# Multi-step progress tracking
backup_progress = {
    "status": "idle",
    "percentage": 0,
    "current_step": "",
    "last_zip": ""
}

class BackupService:
    @staticmethod
    def create_full_backup_zip() -> str:
        global backup_progress
        try:
            backup_progress["status"] = "running"
            backup_progress["percentage"] = 0
            backup_progress["current_step"] = "Khởi tạo thư mục tạm..."
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_{timestamp}"
            
            temp_root = os.path.join(settings.ROOT_DIR, "tmp_backup")
            os.makedirs(temp_root, exist_ok=True)
            
            work_dir = os.path.join(temp_root, backup_name)
            os.makedirs(work_dir, exist_ok=True)
            
            # --- 1. DB Dump ---
            backup_progress["current_step"] = "Đang dump Database (SQL)..."
            backup_progress["percentage"] = 10
            
            db_file = os.path.join(work_dir, "db_dump.sql")
            clean_url = settings.DATABASE_URL.replace("+psycopg2", "").replace("+psycopg", "").replace("+asyncpg", "")
            
            subprocess.run(
                ["pg_dump", "-d", clean_url, "-f", db_file],
                check=True,
                capture_output=True,
                text=True
            )
            
            # --- 2. MinIO Files ---
            backup_progress["current_step"] = "Đang tải ảnh/video từ MinIO..."
            backup_progress["percentage"] = 30
            
            files_dir = os.path.join(work_dir, "files")
            os.makedirs(files_dir, exist_ok=True)
            
            objects = list(client.list_objects(MINIO_BUCKET, recursive=True))
            total_objs = len(objects)
            
            for idx, obj in enumerate(objects):
                dest_path = os.path.join(files_dir, obj.object_name)
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                client.fget_object(MINIO_BUCKET, obj.object_name, dest_path)
                
                # Update progress during file download (scaling 30% to 70%)
                if total_objs > 0:
                    current_pct = 30 + int((idx + 1) / total_objs * 40)
                    backup_progress["percentage"] = current_pct
                    backup_progress["current_step"] = f"Đang tải file ({idx+1}/{total_objs})..."

            # --- 3. Create Zip ---
            backup_progress["current_step"] = "Đang nén toàn bộ dữ liệu (ZIP)..."
            backup_progress["percentage"] = 80
            
            zip_path = os.path.join(temp_root, f"{backup_name}.zip")
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                file_list = []
                for root, dirs, files in os.walk(work_dir):
                    for file in files:
                        file_list.append(os.path.join(root, file))
                
                total_files = len(file_list)
                for idx, fpath in enumerate(file_list):
                    zipf.write(fpath, os.path.relpath(fpath, work_dir))
                    # Scale 80% to 100%
                    if total_files > 0:
                        backup_progress["percentage"] = 80 + int((idx+1)/total_files * 20)

            backup_progress["status"] = "completed"
            backup_progress["current_step"] = "Hoàn tất!"
            backup_progress["percentage"] = 100
            backup_progress["last_zip"] = zip_path
            
            return zip_path
            
        except Exception as e:
            backup_progress["status"] = "failed"
            backup_progress["current_step"] = f"Lỗi: {str(e)}"
            raise e
        finally:
            if os.path.exists(work_dir):
                shutil.rmtree(work_dir)

    @staticmethod
    def get_progress():
        return backup_progress
