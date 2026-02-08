"""
Audit endpoints - POST /api/run-audit
Uses the 3-agent pipeline for compliance analysis
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Literal
import os

from db.database import save_audit
from services.pipeline import run_audit_pipeline_from_upload

router = APIRouter()


def is_db_configured() -> bool:
    """Check if Supabase is configured."""
    return bool(os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_SERVICE_ROLE_KEY"))


@router.post("/run-audit")
async def run_audit(
    file: UploadFile = File(...),
    document_type: str = Form(...),
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

    # Normalize document_type for case-insensitivity
    doc_type_map = {
        "sox 404": "SOX 404",
        "10-k": "10-K",
        "8-k": "8-K",
        "invoice": "Invoice"
    }
    document_type_clean = doc_type_map.get(document_type.lower())
    if not document_type_clean:
        allowed = ", ".join([f"'{v}'" for v in doc_type_map.values()])
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid document_type. Expected one of: {allowed}"
        )

    try:
        # Run the full pipeline
        audit_data = await run_audit_pipeline_from_upload(
            upload_file=file,
            document_type=document_type_clean,
            user_id=user_id,
            source="web"
        )
    except ValueError as e:
        error_msg = str(e)
        if error_msg.startswith("Invalid document:"):
            error_code = "NOT_FINANCIAL_DOCUMENT"
        elif error_msg.startswith("PDF extraction failed:"):
            error_code = "PDF_EXTRACTION_FAILED"
        else:
            error_code = "VALIDATION_ERROR"
        raise HTTPException(status_code=400, detail={"error_code": error_code, "message": error_msg})
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
