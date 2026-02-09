from app.core.minio import client
import os
from datetime import timedelta
from app.core.config import settings
import uuid
from minio.error import S3Error
MINIO_BUCKET = "files"
def ensure_bucket():
    if not client.bucket_exists(MINIO_BUCKET):
        client.make_bucket(MINIO_BUCKET)


def upload_file(file, content_type: str, length: int = -1) -> str:
    ensure_bucket()

    if hasattr(file, "filename"):
        filename = file.filename
        data = file.file
    else:
        filename = os.path.basename(getattr(file, "name", "unknown"))
        data = file

    object_name = f"{uuid.uuid4()}_{filename}"

    client.put_object(
        bucket_name=MINIO_BUCKET,
        object_name=object_name,
        data=data,
        length=length,
        part_size=10 * 1024 * 1024, # Use a standard 10MB part size, SDK will handle smaller files correctly
        content_type=content_type,
    )

    return object_name


def get_public_url(object_name: str) -> str:
    # Nếu dùng https thì protocol là https, ngược lại là http
    protocol = "https" if settings.MINIO_SECURE else "http"
    # Cấu trúc URL công khai: http(s)://domain/bucket/object_name
    return f"{protocol}://{settings.MINIO_ENDPOINT}/{MINIO_BUCKET}/{object_name}"


def get_presigned_url(object_name: str) -> str:
    # Theo yêu cầu mới, chúng ta dùng URL công khai vĩnh viễn
    return get_public_url(object_name)

def delete_object(name: str) -> bool:
    ensure_bucket()
    try:
        client.remove_object(
            bucket_name=MINIO_BUCKET,
            object_name=name
        )
        return True
    except S3Error as e:
        return False