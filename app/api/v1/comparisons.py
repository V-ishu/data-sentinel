"""Comparison job endpoints."""

from typing import List
from fastapi import APIRouter, BackgroundTasks, HTTPException, status, Depends
from sqlalchemy.orm import Session

from app.db.models import JobModel
from app.db.session import get_db

from app.schemas.comparison import(
    ComparisonRequest,
    ComparisonResponse,
    JobCreatedResponse,
    JobDetailResponse,
    JobListItem,
    JobStatus,
)
from app.services.comparison_runner import run_comparison_for_job
from app.services.job_store import (
    create_job,
    delete_job,
    get_job,
    list_jobs,
)

router = APIRouter()

def _to_detail(job: JobModel) -> JobDetailResponse:
    return JobDetailResponse(
        job_id=job.id,
        status=JobStatus(job.status),
        created_at=job.created_at,
        started_at=job.started_at,
        finished_at=job.finished_at,
        request=ComparisonRequest(**job.request),
        result=ComparisonResponse(**job.result) if job.result else None,
        error=job.error,
    )

@router.post(
    "/comparisons",
    response_model=JobCreatedResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def create_comparison(
    req: ComparisonRequest, 
    background_tasks: BackgroundTasks, 
    db: Session = Depends(get_db),
):
    job = create_job(db, req)
    background_tasks.add_task(run_comparison_for_job, job.id)
    return JobCreatedResponse(
        job_id=job.id,
        status=JobStatus(job.status),
        created_at=job.created_at,
    )

@router.get("/comparisons", response_model=List[JobListItem])
def list_comparisons(limit: int = 50, db: Session = Depends(get_db)):
    return[
        JobListItem(
            job_id=j.id,
            status=JobStatus(j.status),
            created_at=j.created_at,
            table=j.table_name,
        )
        for j in list_jobs(db, limit=limit)
    ]

@router.get("/comparisons/{job_id}", response_model=JobDetailResponse)
def get_comparisons(job_id: str, db: Session = Depends(get_db)):
    job = get_job(db, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    return _to_detail(job)

@router.delete("/comparisons/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comparison(job_id: str, db: Session = Depends(get_db)):
    if not delete_job(db, job_id):
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")