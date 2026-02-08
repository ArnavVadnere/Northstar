"""
Agent 0: Document Classifier (Gatekeeper)

Validates if an uploaded PDF is a legitimate financial document
before the full audit pipeline runs.
"""

import json
import os
import re
from typing import Optional
from pydantic import BaseModel
from dedalus_labs import AsyncDedalus, DedalusRunner

class ClassificationResult(BaseModel):
    """Result of the document validation check."""
    is_financial_document: bool
    detected_type: Optional[str] = None
    reason: str

async def classify_document(
    extracted_text: dict,
    expected_type: str
) -> ClassificationResult:
    """
    Classify a document to ensure it's a legitimate financial document.

    Args:
        extracted_text: Output from pdf_extractor (contains full_text and pages)
        expected_type: The type the user selected (10-K, 8-K, etc.) — logged but not gated on.
    """
    if not os.getenv("DEDALUS_API_KEY"):
        return ClassificationResult(
            is_financial_document=True,
            reason="Skipping validation (no API key)"
        )

    client = AsyncDedalus(timeout=300)
    runner = DedalusRunner(client)

    # Use first ~3000 chars for classification (enough to identify doc type)
    doc_preview = extracted_text.get("full_text", "")[:3000]

    prompt = f"""You are a document intake specialist. Your task is to verify whether the following document text is from a real financial document.

DOCUMENT TEXT (first portion):
---
{doc_preview}
---

### RULES ###
1. Classify based ONLY on the document text above.
2. Is this a financial/regulatory document (e.g. SEC filing, annual report, invoice, audit report)? A resume, essay, or random PDF is NOT financial.
3. Your final answer MUST be a raw JSON object. Do not include markdown blocks or conversational text.

Provide your result as structured JSON:
{{
  "is_financial_document": boolean,
  "detected_type": "what type of document this appears to be (e.g. 10-K, 8-K, Invoice, Resume, etc.)",
  "reason": "Brief explanation of what you saw in the document."
}}
"""

    try:
        print(f"[Agent 0] Classifying uploaded document (expected: {expected_type})...")
        result = await runner.run(
            input=prompt,
            model="openai/gpt-4o",
            max_steps=1,
        )

        # Parse the response
        if hasattr(result, 'final_output') and result.final_output:
            output = result.final_output

            clean_json = str(output).strip()
            if clean_json.startswith("```"):
                match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", clean_json, re.DOTALL)
                if match:
                    clean_json = match.group(1)

            try:
                data = json.loads(clean_json)
                res = ClassificationResult(**data)
                if res.is_financial_document:
                    print(f"[Agent 0] >>> SUCCESS: Financial document detected — {res.detected_type} (Reason: {res.reason})")
                else:
                    print(f"[Agent 0] >>> REJECTED: Not a financial document — {res.detected_type} (Reason: {res.reason})")
                return res
            except (json.JSONDecodeError, TypeError, ValueError) as exc:
                print(f"[Agent 0] >>> ERROR: JSON Parse failed: {exc}")

        return ClassificationResult(
            is_financial_document=False,
            reason="Validation failed: Agent returned unparseable or empty output."
        )

    except Exception as e:
        print(f"[Agent 0] >>> ERROR: Classification failed: {e}")
        return ClassificationResult(
            is_financial_document=False,
            detected_type=None,
            reason=f"Classification unavailable due to an internal error. Please retry."
        )
