from .common import *
import uuid
def generate_uuid():
    return str(uuid.uuid4())

class File(Base):
    __tablename__ = "files"

    id = Column(String(50), primary_key=True, default=generate_uuid)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_url = Column(String(500), nullable=False)
    file_size = Column(BigInteger, nullable=False)
    mime_type = Column(String(100), nullable=False)
    file_type = Column(String(50), default='article', index=True)
    uploaded_by = Column(String(50), nullable=True)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)