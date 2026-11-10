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

import asyncio
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn

from app.api import (
    router as api_router,
    ingest_pipeline,
    index_engine,
    google_service,
    stats_service,
)
from app.config import settings


async def background_google_docs_watcher():
    """
    Periodically poll Google Drive for new or modified Google Docs.

    Runs every 60 seconds when Google account authentication is active.
    """
    while True:
        try:
            await asyncio.sleep(60)
            token = google_service.get_token()
            if token and "access_token" in token:
                new_chunks = google_service.detect_and_sync_new_docs(max_files=30)
                if new_chunks:
                    index_engine.index_chunks(new_chunks)
                    stats_service.calculate_statistics(
                        index_engine.get_all_chunks(), index_engine.count()
                    )
        except asyncio.CancelledError:
            break
        except Exception:
            pass


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup and shutdown lifecycle manager.

    Execution steps:
      1. Step 1: Ensure persistent data directories exist.
      2. Step 2: Auto-index sample documents on startup if index is unpopulated.
      3. Step 3: Launch background Google Docs auto-sync watcher task.
      4. Step 4: Yield control to application runner.
      5. Step 5: Cancel watcher task upon server shutdown.
    """
    settings.ensure_directories()

    # Step 2: Auto-index sample documents if table is empty.
    if index_engine.count() == 0 and settings.sample_docs_dir.exists():
        chunks = ingest_pipeline.scan_directory(settings.sample_docs_dir)
        if chunks:
            index_engine.index_chunks(chunks)

    # Initialise statistics cache.
    stats_service.calculate_statistics(
        index_engine.get_all_chunks(), index_engine.count()
    )

    # Step 3: Launch background watcher task.
    watcher_task = asyncio.create_task(background_google_docs_watcher())

    yield

    # Step 5: Cancel watcher upon shutdown.
    watcher_task.cancel()
    try:
        await watcher_task
    except asyncio.CancelledError:
        pass


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
