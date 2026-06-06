# pyrefly: ignore [missing-import]
import pytest
from unittest.mock import AsyncMock, patch
# pyrefly: ignore [missing-import]
import httpx
from app.services.callback import dispatch_callback, post_callback_with_retry
from app.database import engine
# pyrefly: ignore [missing-import]
from sqlmodel import Session

@pytest.mark.anyio
async def test_post_callback_retry_success():
    request = httpx.Request("POST", "http://mock-url.com/callback")
    mock_response = httpx.Response(200, json={"status": "success"}, request=request)
    
    # We mock the post method of the httpx client
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.post.return_value = mock_response
    
    response = await post_callback_with_retry(
        client=mock_client,
        url="http://mock-url.com/callback",
        payload={"test": "data"}
    )
    assert response.status_code == 200
    assert mock_client.post.call_count == 1

@pytest.mark.anyio
async def test_post_callback_retry_with_transient_failure():
    request = httpx.Request("POST", "http://mock-url.com/callback")
    mock_fail = httpx.Response(500, text="Internal Server Error", request=request)
    mock_success = httpx.Response(200, json={"status": "success"}, request=request)
    
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    # Return 500 error first, then 200 success
    mock_client.post.side_effect = [
        httpx.HTTPStatusError("500 Internal Error", request=request, response=mock_fail),
        mock_success
    ]
    
    with patch("time.sleep", return_value=None):  # speed up tests by bypassing wait
        response = await post_callback_with_retry(
            client=mock_client,
            url="http://mock-url.com/callback",
            payload={"test": "data"}
        )
        
    assert response.status_code == 200
    assert mock_client.post.call_count == 2
