import os
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "uploads")).resolve()
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE_BYTES", str(100 * 1024 * 1024)))  # 100 MB

app = FastAPI(title="File Upload API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_file_path(filename: str) -> Path:
    """Resolve a user-supplied filename to a safe path strictly within UPLOAD_DIR."""
    name = Path(filename).name
    if not name or name.startswith("."):
        raise HTTPException(status_code=400, detail="Invalid filename.")
    resolved = (UPLOAD_DIR / name).resolve()
    if not resolved.is_relative_to(UPLOAD_DIR):
        raise HTTPException(status_code=400, detail="Invalid filename.")
    return resolved


@app.post("/upload")
async def upload_files(files: list[UploadFile] = File(...)):
    """Upload one or more files."""
    saved = []
    for file in files:
        path = get_file_path(file.filename or "")

        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File '{path.name}' exceeds the {MAX_FILE_SIZE // (1024 * 1024)} MB limit.",
            )

        path.write_bytes(content)
        saved.append({"filename": path.name, "size": path.stat().st_size})
    return {"uploaded": saved}


@app.get("/files")
def list_files():
    """List all uploaded files."""
    files = [
        {"filename": p.name, "size": p.stat().st_size}
        for p in sorted(UPLOAD_DIR.iterdir())
        if p.is_file()
    ]
    return {"files": files}


@app.get("/files/{filename}")
def download_file(filename: str):
    """Download a specific file by name."""
    path = get_file_path(filename)
    if not path.exists() or not path.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path, filename=path.name)


@app.delete("/files/{filename}")
def delete_file(filename: str):
    """Delete a specific uploaded file."""
    path = get_file_path(filename)
    if not path.exists() or not path.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    path.unlink()
    return {"deleted": path.name}

