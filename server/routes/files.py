"""
File serving endpoint - GET /api/files/{filename}
Serves generated PDF reports from the generated_reports directory
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path

router = APIRouter()

# Directory where generated reports are stored
REPORTS_DIR = Path(__file__).parent.parent / "generated_reports"


@router.get("/files/{filename}")
async def get_file(filename: str):
    """
    Serve generated PDF report files.
    
    Returns the PDF file if it exists, otherwise returns 404.
    """
    # Security: prevent directory traversal
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    file_path = REPORTS_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=filename
    )
