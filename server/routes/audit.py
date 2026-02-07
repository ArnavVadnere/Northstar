"""
Audit endpoints - POST /api/run-audit
Uses the 3-agent pipeline for compliance analysis
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Literal
import os

from db.database import save_audit
from services.pipeline import run_audit_pipeline_from_upload
from services.pdf_extractor import PDFExtractionError

router = APIRouter()


def is_db_configured() -> bool:
    """Check if Supabase is configured."""
    return bool(os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_SERVICE_ROLE_KEY"))


@router.post("/run-audit")
async def run_audit(
    file: UploadFile = File(...),
    document_type: Literal["SOX 404", "10-K", "8-K", "Invoice"] = Form(...),
    user_id: str = Form(...)
):
    """
    Run a compliance audit on an uploaded PDF document.
    
    This endpoint:
    1. Extracts text from the uploaded PDF
    2. Runs the 3-agent pipeline (Researcher → Analyzer → Reporter)
    3. Saves results to Supabase (if configured)
    4. Returns the complete audit result
    
    Processing time: typically 10-60 seconds depending on document size.
    """
    # Validate file is a PDF
    if not file.filename or not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    try:
        # Run the full pipeline
        audit_data = await run_audit_pipeline_from_upload(
            upload_file=file,
            document_type=document_type,
            user_id=user_id,
            source="web"
        )
    except PDFExtractionError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Pipeline error: {e}")
        raise HTTPException(status_code=500, detail="Audit processing failed")
    
    # Save to Supabase if configured
    if is_db_configured():
        try:
            await save_audit(audit_data)
        except Exception as e:
            print(f"Warning: Failed to save audit to database: {e}")
            # Continue anyway - we still have the result
    
    # Remove internal fields before returning
    response = {k: v for k, v in audit_data.items() if k not in ["user_id", "source"]}
    
    return response
