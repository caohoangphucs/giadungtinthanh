from pydantic import BaseModel, ConfigDict

class FileInfo(BaseModel):
    id: str
    file_name: str
    file_url: str
    mime_type: str

    model_config = ConfigDict(from_attributes=True)
