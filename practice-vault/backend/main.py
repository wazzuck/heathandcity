"""
Main Entrypoint for Heath & City Practice Vault.

Purpose:
  Bootstraps the FastAPI application, mounts RESTful API routes, configures
  static file serving for the sovereign frontend dashboard, and executes the
  application under Uvicorn.

Deliberately Not For:
  External cloud proxying or public interface exposure.

Invariants:
  1. Hypertext Transfer Protocol (HTTP) server binds exclusively to the
     configured local loopback or local LAN host address.
  2. Frontend static assets are served from the local filesystem.
"""

from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn

from app.api import router as api_router, ingest_pipeline, index_engine
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup and shutdown lifecycle manager.

    Execution steps:
      1. Step 1: Ensure persistent data directories exist.
      2. Step 2: Auto-index sample documents on startup if index is unpopulated.
      3. Step 3: Yield control to application runner.
    """
    settings.ensure_directories()

    # Step 2: Auto-index sample documents if table is empty.
    if index_engine.count() == 0 and settings.sample_docs_dir.exists():
        chunks = ingest_pipeline.scan_directory(settings.sample_docs_dir)
        if chunks:
            index_engine.index_chunks(chunks)

    yield


app = FastAPI(
    title=settings.app_name,
    description=(
        "Sovereign on-premises practice automation and private document "
        "intelligence system for boutique professional practices."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

# Mount REST API endpoints under /api.
app.include_router(api_router)

# Mount frontend static asset directory.
if settings.static_dir.exists():
    app.mount(
        "/static",
        StaticFiles(directory=str(settings.static_dir)),
        name="static",
    )


@app.get("/")
def serve_index() -> FileResponse:
    """Serve the single-page sovereign dashboard index HTML."""
    index_file = settings.static_dir / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": f"{settings.app_name} API is operational."}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=False,
    )
