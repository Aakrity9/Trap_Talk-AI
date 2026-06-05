import httpx
from typing import Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from sqlmodel import Session as DBSession

from app.config import settings
from app.models import CallbackReport

# Configure tenacity retry for http post request errors
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError)),
    reraise=True
)
async def post_callback_with_retry(client: httpx.AsyncClient, url: str, payload: Dict[str, Any]) -> httpx.Response:
    """
    Sends callback HTTP POST. Retries on connection errors or 5xx status codes.
    """
    response = await client.post(url, json=payload, timeout=5.0)
    response.raise_for_status()
    return response

async def dispatch_callback(
    session_id: str,
    payload: Dict[str, Any],
    db: DBSession
) -> bool:
    """
    Assembles final session report and dispatches it to the configured CALLBACK_URL.
    Logs the callback attempt in the CallbackReport database table.
    """
    url = settings.CALLBACK_URL
    if not url:
        print("No CALLBACK_URL configured. Skipping dispatcher.")
        return False
        
    print(f"Dispatching callback to {url} for session {session_id}...")
    
    report = CallbackReport(
        session_id=session_id,
        callback_url=url,
        success=False
    )
    
    async with httpx.AsyncClient() as client:
        try:
            response = await post_callback_with_retry(client, url, payload)
            report.status_code = response.status_code
            report.success = True
            report.response_text = response.text[:1000]  # truncate to prevent excessive DB storage
            print(f"Callback successful. Status: {response.status_code}")
        except Exception as e:
            print(f"Callback dispatch failed after all retries: {e}")
            report.success = False
            report.response_text = str(e)[:1000]
            if isinstance(e, httpx.HTTPStatusError):
                report.status_code = e.response.status_code
                
    db.add(report)
    db.commit()
    return report.success
