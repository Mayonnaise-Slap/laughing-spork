import json
import logging
import threading
import time
from datetime import datetime
from typing import Callable, Optional

from app.database import SessionLocal
from app.models import Job, JobStatus

logger = logging.getLogger(__name__)


class JobProcessor:
    def __init__(self):
        self.processors: dict[str, Callable] = {
            "default": self.process_ml_job,
        }

    def register(self, job_type: str, processor: Callable):
        self.processors[job_type] = processor

    def process_ml_job(self, job_id: int, input_data: dict) -> dict:
        try:
            logger.info(f"Processing job {job_id} with input: {input_data}")

            # todo real processing
            time.sleep(2)

            result = {
                "input": input_data,
                "prediction": "sample_result",
                "confidence": 0.95,
                "timestamp": datetime.now().isoformat(),
            }

            return {"status": "success", "result": result}

        except Exception as e:
            logger.error(f"Error processing job {job_id}: {str(e)}")
            return {"status": "error", "error": str(e)}

    def process(self, job: Job) -> dict:
        """Process a job based on its type"""
        processor = self.processors.get(job.job_type, self.processors["default"])
        input_data = json.loads(job.input_data) if job.input_data else {}
        return processor(job.id, input_data)


class JobWorker:
    def __init__(
            self,
            poll_interval: int = 2,
            num_workers: int = 4,
            processor: Optional[JobProcessor] = None,
    ):
        self.poll_interval = poll_interval
        self.num_workers = num_workers
        self.processor = processor or JobProcessor()
        self.running = False
        self.worker_threads: list[threading.Thread] = []

    def start(self):
        if self.running:
            logger.warning("Worker already running")
            return

        self.running = True
        logger.info(
            f"Starting worker with {self.num_workers} threads, {self.poll_interval}s poll interval"
        )

        for i in range(self.num_workers):
            thread = threading.Thread(
                target=self._worker_loop,
                name=f"JobWorker-{i}",
                daemon=True,
            )
            thread.start()
            self.worker_threads.append(thread)

    def stop(self):
        logger.info("Stopping worker...")
        self.running = False

        for thread in self.worker_threads:
            thread.join(timeout=5)

        self.worker_threads.clear()
        logger.info("Worker stopped")

    def _worker_loop(self):
        logger.debug(f"Worker loop started: {threading.current_thread().name}")

        while self.running:
            try:
                self._process_pending_job()
            except Exception as e:
                logger.error(f"Error in worker loop: {str(e)}", exc_info=True)

            time.sleep(self.poll_interval)

    def _process_pending_job(self):
        db = SessionLocal()

        try:
            job = (
                db.query(Job)
                .filter(Job.status == JobStatus.PENDING)
                .order_by(Job.created_at.asc())
                .first()
            )

            if not job:
                return

            logger.info(f"Processing job {job.id} (type: {job.job_type})")

            job.status = JobStatus.RUNNING
            job.started_at = datetime.now()
            job.progress = 0
            db.commit()

            # Process job
            result = self.processor.process(job)

            job.progress = 100
            if result["status"] == "success":
                job.status = JobStatus.COMPLETED
                job.result = json.dumps(result["result"])
                logger.info(f"Job {job.id} completed successfully")
            else:
                job.status = JobStatus.FAILED
                job.error = result.get("error", "Unknown error")
                logger.error(f"Job {job.id} failed: {job.error}")

            job.completed_at = datetime.utcnow()
            db.commit()

        except Exception as e:
            try:
                if job:
                    job.status = JobStatus.FAILED
                    job.error = str(e)
                    job.completed_at = datetime.utcnow()
                    db.commit()
            except Exception as db_error:
                logger.error(f"Failed to update job status: {db_error}")

            logger.error(f"Job processing error: {str(e)}", exc_info=True)

        finally:
            db.close()


_worker: Optional[JobWorker] = None


def get_worker() -> JobWorker:
    global _worker
    if _worker is None:
        _worker = JobWorker()
    return _worker


def start_worker(poll_interval: int = 2, num_workers: int = 4):
    worker = get_worker()
    worker.poll_interval = poll_interval
    worker.num_workers = num_workers
    worker.start()


def stop_worker():
    global _worker
    if _worker and _worker.running:
        _worker.stop()
