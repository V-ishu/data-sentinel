"""Pydantic models for the comparison endpoints."""

from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

class ComparisonRequest(BaseModel):
    """What the client sends to start a comparison."""

    source_db: str = Field(
        ...,
        description="Source DB connection string (SQLAlchemy URL).",
        examples=["sqlite:///source.db"],
    )
    target_db: str = Field(
        ...,
        description="Target DB connection string (SQLAlchemy URL).",
        examples=["sqlite:///target.db"],
    )
    table: str = Field(
        ...,
        description="Table name to compare.",
        examples=["employees"],
    )
    pk: Optional[str] = Field(
        None,
        description="Prmary key column. Auto-detected if omitted.",
    )
    composite_keys: Optional[List[str]] = Field(
        None,
        description="Composite key columns, used if no single PK.",
    )
    where: Optional[str] = Field(
        None,
        description='Optional WHERE clause filter, e.g. "department = \'Engineering\'"',
    )

class ComparisonSummary(BaseModel):
    """High-level numbers from a comparison run."""

    strategy_used: str
    total_source_rows: int
    total_target_rows: int
    missing_in_target_count: int
    missing_in_source_count: int
    mismatched_rows_count: int
    total_issues: int
    
class ComparisonResponse(BaseModel):
    """Full comparison result returned to the client."""

    table: str
    summary: ComparisonSummary
    missing_in_target: List[dict]
    missing_in_source: List[dict]
    mismatched_rows: List[dict]

class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class JobCreatedResponse(BaseModel):
    """Returned immediately when a job is submitted."""

    job_id: str
    status: JobStatus
    created_at: datetime

class JobDetailResponse(BaseModel):
    """Returned by GET /comparisons/{job_id} - full snapshot of a job."""

    job_id: str
    status: JobStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    request: ComparisonRequest
    result: Optional[ComparisonResponse] = None
    error: Optional[str] = None

class JobListItem(BaseModel):
    """One row in the GET / comparisons listing."""

    job_id: str
    status: JobStatus
    created_at: datetime
    table: str