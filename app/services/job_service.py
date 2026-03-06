import json
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.models import Job, JobStatus
from app.schemas import JobResponse


class JobService:
    @staticmethod
    def create_job(
            db: Session,
            user_id: int,
            input_data: dict,
            job_type: str = "default",
    ) -> JobResponse:
        job = Job(
            user_id=user_id,
            status=JobStatus.PENDING,
            input_data=json.dumps(input_data),
            job_type=job_type,
        )
        db.add(job)
        db.commit()
        db.refresh(job)

        return JobResponse.model_validate(job)

    @staticmethod
    def get_job(db: Session, job_id: int, user_id: int) -> type[Job] | None:
        job = (
            db.query(Job)
            .filter(
                Job.id == job_id,
                Job.user_id == user_id,
            )
            .first()
        )

        return job

    @staticmethod
    def get_user_jobs(
            db: Session,
            user_id: int,
            skip: int = 0,
            limit: int = 10,
    ) -> tuple[list[type[Job]], int]:
        total = db.query(Job).filter(Job.user_id == user_id).count()
        jobs = (
            db.query(Job)
            .filter(
                Job.user_id == user_id,
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

        return jobs, total

    @staticmethod
    def update_job_status(
            db: Session,
            job_id: int,
            status: JobStatus,
            result: dict = None,
            error: str = None,
            progress: int = None,
    ) -> type[Job] | None:
        job = db.query(Job).filter(Job.id == job_id).first()

        if job:
            job.status = status
            if result:
                job.result = json.dumps(result)
            if error:
                job.error = error
            if progress is not None:
                job.progress = progress
            if status == JobStatus.COMPLETED:
                job.completed_at = datetime.now()

            db.commit()
            db.refresh(job)

        return job

    @staticmethod
    def cancel_job(db: Session, job_id: int, user_id: int) -> bool:
        job = JobService.get_job(db, job_id, user_id)

        if job and job.status in [JobStatus.PENDING, JobStatus.RUNNING]:
            job.status = JobStatus.CANCELLED
            job.completed_at = datetime.now()
            db.commit()

            return True

        return False
