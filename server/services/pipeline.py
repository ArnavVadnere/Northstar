"""
3-Agent Pipeline Orchestration

Orchestrates the full compliance audit flow:
1. Agent 1: Research compliance rules (Person 1)
2. Agent 2: Analyze PDF against rules (Person 2 - you)
3. Agent 3: Generate report and score (Person 3)

Owner: Person 2
"""
from pathlib import Path
from typing import Optional
from datetime import datetime, timezone
import uuid

from services.pdf_extractor import extract_text_from_pdf, PDFExtractionError
from agents.compliance_researcher import research_compliance_rules
from agents.pdf_analyzer import analyze_pdf, AnalysisResult
from agents.report_generator import generate_report


# Directory for generated reports
REPORTS_DIR = Path(__file__).parent.parent / "generated_reports"


async def run_audit_pipeline(
    pdf_content: bytes,
    document_name: str,
    document_type: str,
    user_id: str,
    source: str = "web"
) -> dict:
    """
    Run the full 3-agent compliance audit pipeline.
    
    Args:
        pdf_content: Raw PDF file bytes
        document_name: Original filename
        document_type: Type of document ('SOX 404', '10-K', '8-K', 'Invoice')
        user_id: User identifier (Discord ID or web session)
        source: Source of request ('discord' or 'web')
    
    Returns:
        Complete audit result matching CONTRACT.md schema
    """
    audit_id = f"aud_{uuid.uuid4().hex[:8]}"
    timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    
    # Ensure reports directory exists
    REPORTS_DIR.mkdir(exist_ok=True)
    
    # Step 1: Extract text from PDF
    try:
        extracted = extract_text_from_pdf(pdf_content)
        print(f"[Pipeline] Extracted {extracted['page_count']} pages, {len(extracted['full_text'])} characters")
    except PDFExtractionError as e:
        raise ValueError(f"PDF extraction failed: {e}")
    
    # Step 2: Research compliance rules (Agent 1 - Person 1's agent)
    print(f"[Pipeline] Researching {document_type} compliance rules...")
    compliance_research = await research_compliance_rules(document_type)
    rules_text = compliance_research.get("rules", "")
    print(f"[Pipeline] Got {len(rules_text)} chars of compliance rules")
    
    # Step 3: Analyze PDF against rules (Agent 2 - your agent)
    print(f"[Pipeline] Analyzing document against compliance rules...")
    analysis: AnalysisResult = await analyze_pdf(
        extracted_text=extracted,
        document_type=document_type,
        compliance_rules=rules_text
    )
    
    # Convert Pydantic models to dicts for Agent 3
    gaps_dict = [
        {
            "severity": gap.severity,
            "title": gap.title,
            "description": gap.description,
            "regulation": gap.regulation,
            "locations": [
                {"page": loc.page, "quote": loc.quote, "context": loc.context}
                for loc in gap.locations
            ]
        }
        for gap in analysis.gaps
    ]
    print(f"[Pipeline] Found {len(gaps_dict)} compliance gaps")
    
    # Step 4: Generate report (Agent 3 - Person 3's agent)
    print(f"[Pipeline] Generating compliance report...")
    report = await generate_report(
        audit_id=audit_id,
        document_name=document_name,
        document_type=document_type,
        gaps=gaps_dict,
        output_dir=REPORTS_DIR
    )
    
    # Build final response matching CONTRACT.md
    result = {
        "audit_id": audit_id,
        "user_id": user_id,
        "source": source,
        "score": report["score"],
        "grade": report["grade"],
        "document_name": document_name,
        "document_type": document_type,
        "timestamp": timestamp,
        "gaps": gaps_dict,
        "remediation": report["remediation"],
        "executive_summary": report["executive_summary"],
        "report_pdf_url": f"/api/files/report_{audit_id}.pdf"
    }
    
    print(f"[Pipeline] Audit {audit_id} complete. Score: {report['score']}, Grade: {report['grade']}")
    
    return result


async def run_audit_pipeline_from_upload(
    upload_file,
    document_type: str,
    user_id: str,
    source: str = "web"
) -> dict:
    """
    Run pipeline from a FastAPI UploadFile.
    
    Convenience wrapper that reads the file content first.
    """
    content = await upload_file.read()
    await upload_file.seek(0)  # Reset for potential reuse
    
    return await run_audit_pipeline(
        pdf_content=content,
        document_name=upload_file.filename,
        document_type=document_type,
        user_id=user_id,
        source=source
    )
