from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.security import get_current_user, require_role
from app.services import JobService
from app.schemas import JobCreate, JobResponse, JobListResponse
from app.models import User, UserRole, Job

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("/", response_model=JobResponse)
def create_job(
    job_create: JobCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Submit a new ML job"""
    job = JobService.create_job(
        db=db,
        user_id=current_user.id,
        input_data=job_create.input_data,
        job_type=job_create.job_type,
    )
    return job


@router.get("/", response_model=JobListResponse)
def list_user_jobs(
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    jobs, total = JobService.get_user_jobs(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
    )

    return JobListResponse(
        items=[JobResponse.model_validate(job) for job in jobs],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{job_id}", response_model=JobResponse)
def get_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job = JobService.get_job(db, job_id, current_user.id)

    if not job:
        existing_job = db.query(Job).filter(Job.id == job_id).first()
        if existing_job:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this job",
            )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    return JobResponse.from_orm(job)


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    success = JobService.cancel_job(db, job_id, current_user.id)

    if not success:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found",
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job cannot be cancelled in its current state",
        )


@router.get("/admin/all", response_model=JobListResponse)
def list_all_jobs(
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    total = db.query(Job).count()
    jobs = db.query(Job).offset(skip).limit(limit).all()

    return JobListResponse(
        items=[JobResponse.model_validate(job) for job in jobs],
        total=total,
        skip=skip,
        limit=limit,
    )
