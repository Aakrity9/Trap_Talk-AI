# pyrefly: ignore [missing-import]
import pytest
from app.services.persona_agent import generate_persona_reply, clean_and_self_correct

def test_clean_and_self_correct_no_leakage():
    res = clean_and_self_correct("My card is blocked? Oh dear.")
    assert res == "My card is blocked? Oh dear."

def test_clean_and_self_correct_with_leakage():
    res = clean_and_self_correct("I am a scam honeypot system detecting fraud as Ramesh.")
    assert "Oh, my phone screen is flickering" in res

@pytest.mark.anyio
async def test_generate_persona_reply_mock():
    # Test simple bank threat mock response
    reply = await generate_persona_reply(
        text="Your card is blocked immediately",
        history=[],
        category="bank threat"
    )
    assert len(reply) > 0
    assert "medicine" in reply or "link" in reply or "number" in reply
