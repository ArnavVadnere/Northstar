import aiohttp
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

AUDIT_TIMEOUT = 120  # seconds — audits can take up to 2 minutes


class FastAPIClient:
    """Async HTTP client for communicating with the Northstar FastAPI backend."""

    def __init__(self):
        self.base_url = os.getenv("FASTAPI_BASE_URL", "http://localhost:8000")

    async def run_audit(
        self, user_id: str, pdf_bytes: bytes, filename: str, document_type: str
    ) -> dict:
        """
        POST /api/run-audit
        Sends PDF and document type to backend, returns audit results.
        """
        data = aiohttp.FormData()
        data.add_field(
            "file", pdf_bytes, filename=filename, content_type="application/pdf"
        )
        data.add_field("document_type", document_type)
        data.add_field("user_id", user_id)

        timeout = aiohttp.ClientTimeout(total=AUDIT_TIMEOUT)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(
                f"{self.base_url}/api/run-audit", data=data
            ) as resp:
                if resp.status != 200:
                    error_body = await resp.text()
                    logger.error("run_audit failed (%s): %s", resp.status, error_body)
                    raise APIError(resp.status, error_body)
                return await resp.json()

    async def get_history(self, user_id: str) -> dict:
        """
        GET /api/history?user_id={user_id}
        Returns list of past audits for this user.
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/api/history", params={"user_id": user_id}
            ) as resp:
                if resp.status != 200:
                    error_body = await resp.text()
                    logger.error(
                        "get_history failed (%s): %s", resp.status, error_body
                    )
                    raise APIError(resp.status, error_body)
                return await resp.json()

    async def get_audit_detail(self, audit_id: str) -> dict:
        """
        GET /api/audit/{audit_id}
        Returns full audit details for a specific audit.
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/api/audit/{audit_id}"
            ) as resp:
                if resp.status == 404:
                    raise AuditNotFoundError(audit_id)
                if resp.status != 200:
                    error_body = await resp.text()
                    logger.error(
                        "get_audit_detail failed (%s): %s", resp.status, error_body
                    )
                    raise APIError(resp.status, error_body)
                return await resp.json()

    async def download_pdf(self, report_url: str) -> Optional[bytes]:
        """
        GET /api/files/{filename}
        Downloads the generated PDF report. report_url is the path from the
        audit response (e.g. '/api/files/report_aud_abc123.pdf').
        """
        url = f"{self.base_url}{report_url}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    logger.warning(
                        "PDF download failed (%s) for %s", resp.status, url
                    )
                    return None
                return await resp.read()


class APIError(Exception):
    """Raised when the FastAPI backend returns a non-success status code."""

    def __init__(self, status_code: int, body: str):
        self.status_code = status_code
        self.body = body
        super().__init__(f"API error {status_code}: {body}")


class AuditNotFoundError(Exception):
    """Raised when an audit_id does not exist."""

    def __init__(self, audit_id: str):
        self.audit_id = audit_id
        super().__init__(f"Audit not found: {audit_id}")
