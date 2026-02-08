"""
Supabase Database Client and CRUD Operations
"""
import os
from datetime import datetime, timezone
from typing import Optional
from supabase import create_async_client, AsyncClient
from dotenv import load_dotenv

load_dotenv()

# Supabase client singleton
_supabase_client: Optional[AsyncClient] = None


async def get_supabase() -> AsyncClient:
    """Get or create Supabase client singleton."""
    global _supabase_client
    if _supabase_client is None:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")
        _supabase_client = await create_async_client(url, key)
    return _supabase_client


async def ensure_user_exists(user_id: str, source: str = "web") -> dict:
    """
    Ensure a user exists in the database, create if not.
    
    Args:
        user_id: Discord user ID or web session ID
        source: 'discord' or 'web'
    
    Returns:
        User record
    """
    supabase = await get_supabase()
    
    # Check if user exists
    result = await supabase.table("users").select("*").eq("id", user_id).execute()
    
    if result.data:
        return result.data[0]
    
    # Create new user
    new_user = {
        "id": user_id,
        "source": source
    }
    result = await supabase.table("users").insert(new_user).execute()
    return result.data[0]


async def save_audit(audit_data: dict) -> dict:
    """
    Save a complete audit result to the database.
    
    Args:
        audit_data: Full audit response including gaps and remediation
    
    Returns:
        The saved audit record
    """
    supabase = await get_supabase()
    
    # Ensure user exists
    user_id = audit_data.get("user_id", "anonymous")
    source = audit_data.get("source", "web")
    await ensure_user_exists(user_id, source)
    
    # Insert main audit record
    audit_record = {
        "audit_id": audit_data["audit_id"],
        "user_id": user_id,
        "document_name": audit_data["document_name"],
        "document_type": audit_data["document_type"],
        "score": audit_data["score"],
        "grade": audit_data["grade"],
        "executive_summary": audit_data.get("executive_summary", ""),
        "report_pdf_url": audit_data.get("report_pdf_url", "")
    }
    
    result = await supabase.table("audits").insert(audit_record).execute()
    
    # Insert gaps with locations
    for gap in audit_data.get("gaps", []):
        gap_record = {
            "audit_id": audit_data["audit_id"],
            "severity": gap["severity"],
            "title": gap["title"],
            "description": gap["description"],
            "regulation": gap["regulation"]
        }
        gap_result = await supabase.table("audit_gaps").insert(gap_record).execute()
        gap_id = gap_result.data[0]["id"]
        
        # Insert locations for this gap
        for location in gap.get("locations", []):
            location_record = {
                "gap_id": gap_id,
                "page": location["page"],
                "quote": location["quote"],
                "context": location.get("context", "")
            }
            await supabase.table("gap_locations").insert(location_record).execute()
    
    # Insert remediation steps
    for i, step in enumerate(audit_data.get("remediation", []), start=1):
        remediation_record = {
            "audit_id": audit_data["audit_id"],
            "step_number": i,
            "description": step
        }
        await supabase.table("audit_remediations").insert(remediation_record).execute()
    
    return result.data[0]


async def get_history(user_id: str) -> list:
    """
    Get audit history for a user.
    
    Args:
        user_id: Discord user ID or web session ID
    
    Returns:
        List of audit summaries
    """
    supabase = await get_supabase()
    
    result = await supabase.table("audits")\
        .select("audit_id, document_name, document_type, score, grade, created_at")\
        .eq("user_id", user_id)\
        .order("created_at", desc=True)\
        .execute()
    
    # Format timestamps
    audits = []
    for audit in result.data:
        audits.append({
            "audit_id": audit["audit_id"],
            "document_name": audit["document_name"],
            "document_type": audit["document_type"],
            "score": audit["score"],
            "grade": audit["grade"],
            "timestamp": audit["created_at"]
        })
    
    return audits


async def get_audit(audit_id: str) -> Optional[dict]:
    """
    Get full audit details by ID.
    
    Args:
        audit_id: Audit ID (e.g., 'aud_abc123')
    
    Returns:
        Full audit record with gaps and remediation, or None if not found
    """
    supabase = await get_supabase()
    
    # Get main audit record
    audit_result = await supabase.table("audits")\
        .select("*")\
        .eq("audit_id", audit_id)\
        .execute()
    
    if not audit_result.data:
        return None
    
    audit = audit_result.data[0]
    
    # Get gaps with locations
    gaps_result = await supabase.table("audit_gaps")\
        .select("*")\
        .eq("audit_id", audit_id)\
        .execute()
    
    gaps = []
    for gap in gaps_result.data:
        # Get locations for this gap
        locations_result = await supabase.table("gap_locations")\
            .select("page, quote, context")\
            .eq("gap_id", gap["id"])\
            .execute()
        
        gaps.append({
            "severity": gap["severity"],
            "title": gap["title"],
            "description": gap["description"],
            "regulation": gap["regulation"],
            "locations": locations_result.data
        })
    
    # Get remediation steps
    remediation_result = await supabase.table("audit_remediations")\
        .select("description")\
        .eq("audit_id", audit_id)\
        .order("step_number")\
        .execute()
    
    remediation = [r["description"] for r in remediation_result.data]
    
    # Build full response
    return {
        "audit_id": audit["audit_id"],
        "score": audit["score"],
        "grade": audit["grade"],
        "document_name": audit["document_name"],
        "document_type": audit["document_type"],
        "timestamp": audit["created_at"],
        "gaps": gaps,
        "remediation": remediation,
        "executive_summary": audit["executive_summary"],
        "report_pdf_url": audit["report_pdf_url"]
    }
