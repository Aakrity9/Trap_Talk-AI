import pytest
from app.services.extractor import extract_entities_regex, extract_intelligence

def test_extract_entities_regex():
    sample_text = (
        "Hey verify your wallet, transfer 500 INR to scammer@okaxis. "
        "Also call +919876543210 immediately or click http://verify-block.alert/login"
    )
    res = extract_entities_regex(sample_text)
    
    assert "scammer@okaxis" in res["upiIds"]
    assert "+919876543210" in res["phoneNumbers"]
    assert "http://verify-block.alert/login" in res["phishingLinks"]
    assert "verify" in res["suspiciousKeywords"]
    assert "blocked" not in res["suspiciousKeywords"]

@pytest.mark.anyio
async def test_extract_intelligence_incremental():
    existing = {
        "bankAccounts": [],
        "upiIds": ["old@upi"],
        "phishingLinks": [],
        "phoneNumbers": [],
        "suspiciousKeywords": ["blocked"]
    }
    
    merged = await extract_intelligence(
        text="Send to scammer@okicici and click http://scam.link",
        conversation_history=[],
        existing_data=existing
    )
    
    # Check that it merged values correctly without deleting existing ones
    assert "old@upi" in merged["upiIds"]
    assert "scammer@okicici" in merged["upiIds"]
    assert "http://scam.link" in merged["phishingLinks"]
    assert "blocked" in merged["suspiciousKeywords"]
    assert len(merged["upiIds"]) == 2
