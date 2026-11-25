import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class _Item(BaseModel):
    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True, from_attributes=True)


class SkillItem(_Item):
    name: str = Field(min_length=1, max_length=100)
    category: str = Field(default="", max_length=50)
    evidence: str = Field(default="", max_length=300)


class ProjectItem(_Item):
    name: str = Field(min_length=1, max_length=150)
    description: str = Field(default="", max_length=1500)
    technologies: str = Field(default="", max_length=300)


class ExperienceItem(_Item):
    company: str = Field(min_length=1, max_length=150)
    role: str = Field(default="", max_length=150)
    description: str = Field(default="", max_length=1500)


class EducationItem(_Item):
    institution: str = Field(min_length=1, max_length=150)
    degree: str = Field(default="", max_length=150)
    field: str = Field(default="", max_length=150)


class ResumeAnalysis(BaseModel):
    """Used both for model output validation and for user edits."""

    model_config = ConfigDict(extra="ignore")

    skills: list[SkillItem] = Field(default_factory=list, max_length=60)
    projects: list[ProjectItem] = Field(default_factory=list, max_length=15)
    experiences: list[ExperienceItem] = Field(default_factory=list, max_length=15)
    education: list[EducationItem] = Field(default_factory=list, max_length=10)


class AnalysisOut(ResumeAnalysis):
    is_confirmed: bool


class ResumeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    original_filename: str
    file_type: str
    file_size: int
    status: str
    status_message: str | None
    extraction_warnings: list[str]
    created_at: datetime
    updated_at: datetime