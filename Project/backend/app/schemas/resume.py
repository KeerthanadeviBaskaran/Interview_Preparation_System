from pydantic import BaseModel


class ResumeUploadResponse(BaseModel):
    filename: str
    filepath: str
    size_bytes: int
    content_type: str
    message: str = "Resume uploaded successfully"
