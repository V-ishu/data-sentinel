"""Orchestrates the existing comparison engine for the API layer."""

from datetime import datetime
from sentinel.comparator import Comparator
from sentinel.connector import DatabaseConnector

from app.db.session import SessionLocal

from app.schemas.comparison import (
    ComparisonRequest,
    ComparisonResponse,
    ComparisonSummary,
    JobStatus,
)
from app.services.job_store import get_job, update_job_status

ROW_LIMIT = 200

def run_comparison(req: ComparisonRequest) -> ComparisonResponse:
    source_conn = DatabaseConnector(req.source_db, label="source")
    target_conn = DatabaseConnector(req.target_db, label="target")

    source_conn.connect()
    target_conn.connect()

    try:
        pk = req.pk
        if not pk and not req.composite_keys:
            pk = source_conn.get_primary_key(req.table)
        
        source_data = source_conn.fetch_table(req.table, where_clause=req.where)
        target_data = target_conn.fetch_table(req.table, where_clause=req.where)
    finally:
        source_conn.disconnect()
        target_conn.disconnect()
    
    comparator = Comparator(
        source_data=source_data,
        target_data=target_data,
        pk_column=pk,
        composite_keys=req.composite_keys,
    )
    results = comparator.compare()

    total_issues = (
        len(results["missing_in_target"]) +
        len(results["missing_in_source"]) + 
        len(results["mismatched_rows"])
    )

    summary = ComparisonSummary(
        strategy_used=results["strategy_used"],
        total_source_rows=results["total_source_rows"],
        total_target_rows=results["total_target_rows"],
        missing_in_target_count=len(results["missing_in_target"]),
        missing_in_source_count=len(results["missing_in_source"]),
        mismatched_rows_count=len(results["mismatched_rows"]),
        total_issues=total_issues,
    )

    return ComparisonResponse(
        table=req.table,
        summary=summary,
        missing_in_target=results["missing_in_target"][:ROW_LIMIT],
        missing_in_source=results["missing_in_source"][:ROW_LIMIT],
        mismatched_rows=results["mismatched_rows"][:ROW_LIMIT],
    )

def run_comparison_for_job(job_id: str) -> None:
    """

    Background-task version. Looks up the job, runs the comparison, and writes the result (or error) back into the job store.
    """

    db = SessionLocal()
    try:
        job = get_job(db, job_id)
        if job is None:
            return
        update_job_status(db, job_id, JobStatus.RUNNING.value, started_at=datetime.utcnow(),)

        try:
            req = ComparisonRequest(**job.request)
            result = run_comparison(req)
            update_job_status(
                db,
                job_id,
                JobStatus.COMPLETED.value,
                finished_at=datetime.utcnow(),
                result=result.model_dump(mode="json"),
            )
        except Exception as exc:
            update_job_status(
                db,
                job_id,
                JobStatus.FAILED.value,
                finished_at=datetime.utcnow(),
                error=f"{type(exc).__name__}: {str(exc)}",
            )      
    finally:
        db.close()