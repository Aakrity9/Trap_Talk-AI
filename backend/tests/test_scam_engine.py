# pyrefly: ignore [missing-import]
import pytest
from app.services.scam_engine import analyze_scam_heuristics, analyze_scam_intent

def test_analyze_scam_heuristics_clean():
    risk, category = analyze_scam_heuristics("Hello, hope you are having a nice day.")
    assert risk <= 10.0
    assert category == "clean"

def test_analyze_scam_heuristics_bank_threat():
    risk, category = analyze_scam_heuristics("Your bank account is blocked, please verify immediately!")
    assert risk >= 70.0
    assert category == "bank threat"

def test_analyze_scam_heuristics_upi_fraud():
    risk, category = analyze_scam_heuristics("Please pay UPI transfer scanner reward")
    assert risk >= 50.0
    assert category == "upi fraud"

@pytest.mark.anyio
async def test_analyze_scam_intent_async():
    result = await analyze_scam_intent("Lottery cash back! You won a crore!")
    assert result["risk_score"] >= 70.0
    assert result["scam_category"] == "fake offer"
