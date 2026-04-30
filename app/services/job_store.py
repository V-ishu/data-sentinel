"""In-memory job store. Replaced by Postgres in Week 2."""
"""This is now a Job repository - DB operation for the JobModel."""


from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import JobModel
from app.schemas.comparison import ComparisonRequest, JobStatus

def create_job(db: Session, req: ComparisonRequest) -> JobModel:
    job = JobModel(
        id=str(uuid4()),
        status=JobStatus.QUEUED.value,
        table_name=req.table,
        request=req.model_dump(),
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job

def get_job(db: Session, job_id: str) -> Optional[JobModel]:
    return db.get(JobModel, job_id)

def list_jobs(db: Session, limit: int = 50) -> List[JobModel]:
    stmt = select(JobModel).order_by(JobModel.created_at.desc()).limit(limit)
    return list(db.scalars(stmt))

def delete_job(db: Session, job_id: str) -> bool:
    job = db.get(JobModel, job_id)
    if job is None:
        return False
    db.delete(job)
    db.commit()
    return True

def update_job_status(
    db: Session,
    job_id: str,
    status: str,
    started_at: Optional[datetime] = None,
    finished_at: Optional[datetime] = None,
    result: Optional[dict] = None,
    error: Optional[str] = None,
) -> None:
    job = db.get(JobModel, job_id)
    if job is None:
        return
    job.status = status
    if started_at is not None:
        job.started_at = started_at
    if finished_at is not None:
        job.finished_at = finished_at
    if result is not None:
        job.result = result
    if error is not None:
        job.error = error
    db.commit()


