import os
import shutil
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CHUNK_TMP_DIR = os.path.join(BASE_DIR, "tmp_chunks")
CHUNK_EXPIRE_SECONDS = 30 * 60  # 30 phút


def cleanup_tmp_chunks():
    if not os.path.exists(CHUNK_TMP_DIR):
        return

    now = time.time()

    for upload_id in os.listdir(CHUNK_TMP_DIR):
        upload_path = os.path.join(CHUNK_TMP_DIR, upload_id)

        if not os.path.isdir(upload_path):
            continue

        last_modified = os.path.getmtime(upload_path)

        if now - last_modified > CHUNK_EXPIRE_SECONDS:
            shutil.rmtree(upload_path, ignore_errors=True)
            print(f"[CLEANUP] Removed tmp upload {upload_id}")
