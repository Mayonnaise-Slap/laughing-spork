from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import get_settings
from app.database import Base, engine
from app.middleware import LoggingMiddleware
from app.worker import start_worker, stop_worker
from app.routes import auth, users, jobs, health

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    print("Database tables created")

    if settings.worker_enabled:
        start_worker(
            poll_interval=settings.worker_poll_interval,
            num_workers=settings.worker_threads,
        )
        print(f"Job worker started ({settings.worker_threads} threads)")

    yield

    if settings.worker_enabled:
        stop_worker()
    print("Shutting down application")


app = FastAPI(
    title=settings.app_name,
    description="ML Backend API",
    version="0.1.0",
    lifespan=lifespan,
    debug=settings.debug,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # todo figure
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(LoggingMiddleware)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(jobs.router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )
