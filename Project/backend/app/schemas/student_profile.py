from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, HttpUrl, Field, ConfigDict, field_validator


class StudentProfileBase(BaseModel):
    """
    Base Pydantic schema for Student Profile data validation.
    """
    phone_number: Optional[str] = Field(None, max_length=50, description="Contact phone number")
    bio: Optional[str] = Field(None, max_length=2000, description="Short personal biography")
    target_role: str = Field("Software Engineer", max_length=100, description="Desired job title or role")
    experience_level: str = Field("Entry Level", max_length=50, description="Experience tier (e.g. Entry, Mid, Senior)")
    target_companies: Optional[List[str]] = Field(default_factory=list, description="List of target companies")
    skills: Optional[List[str]] = Field(default_factory=list, description="List of technical and soft skills")
    education: Optional[str] = Field(None, max_length=255, description="Degree or institution")
    graduation_year: Optional[int] = Field(None, ge=1970, le=2100, description="Graduation year")
    github_url: Optional[str] = Field(None, description="GitHub profile URL")
    linkedin_url: Optional[str] = Field(None, description="LinkedIn profile URL")
    portfolio_url: Optional[str] = Field(None, description="Personal portfolio website URL")

    @field_validator("github_url", "linkedin_url", "portfolio_url", mode="before")
    def validate_urls(cls, value: Optional[str]) -> Optional[str]:
        if value is None or value.strip() == "":
            return None
        url_str = value.strip()
        if not (url_str.startswith("http://") or url_str.startswith("https://")):
            url_str = "https://" + url_str
        return url_str


class StudentProfileCreate(StudentProfileBase):
    """
    Schema required for initial Student Profile creation.
    """
    pass


class StudentProfileUpdate(BaseModel):
    """
    Schema for updating an existing Student Profile. All fields optional.
    """
    phone_number: Optional[str] = None
    bio: Optional[str] = None
    target_role: Optional[str] = None
    experience_level: Optional[str] = None
    target_companies: Optional[List[str]] = None
    skills: Optional[List[str]] = None
    education: Optional[str] = None
    graduation_year: Optional[int] = None
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    portfolio_url: Optional[str] = None

    @field_validator("github_url", "linkedin_url", "portfolio_url", mode="before")
    def validate_urls(cls, value: Optional[str]) -> Optional[str]:
        if value is None or value.strip() == "":
            return None
        url_str = value.strip()
        if not (url_str.startswith("http://") or url_str.startswith("https://")):
            url_str = "https://" + url_str
        return url_str


class StudentProfileResponse(StudentProfileBase):
    """
    Response schema returning complete Student Profile data.
    """
    id: int
    user_id: int
    resume_filename: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
