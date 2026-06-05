import re
from typing import Dict, Any, Tuple
from app.config import settings
# pyrefly: ignore [missing-import]
import httpx

SCAM_KEYWORDS = {
    "bank threat": [
        r"\bbank\b", r"\bblock(ed)?\b", r"\bsuspend(ed)?\b", r"\bverify\b", 
        r"\baccount\b", r"\bcard\b", r"\bkyc\b", r"\balert\b", r"\bimmediately\b"
    ],
    "upi fraud": [
        r"\bupi\b", r"\bpay\b", r"\btransfer\b", r"\brequest\b", r"\bpin\b", 
        r"\bscanner\b", r"\breceive money\b", r"\bpayment\b", r"\bgoogle pay\b", r"\bgpay\b", r"\bphonepe\b", r"\bpaytm\b"
    ],
    "phishing": [
        r"\blink\b", r"\bclick\b", r"\burl\b", r"https?://", r"\blogin\b", 
        r"\bcredentials\b", r"\bpassword\b", r"\bupdate\b", r"\bverify here\b"
    ],
    "fake offer": [
        r"\blottery\b", r"\bcash back\b", r"\bwon\b", r"\bprize\b", r"\breward\b", 
        r"\bfree\b", r"\bgift\b", r"\bcongratulations\b", r"\bearned\b", r"\bcrore\b", r"\blakh\b"
    ]
}

def analyze_scam_heuristics(text: str) -> Tuple[float, str]:
    """
    Scam intent analysis using rules and heuristics.
    Returns:
        risk_score (float, 0-100)
        scam_category (str)
    """
    text_lower = text.lower()
    matches = {}
    total_matches = 0

    for category, patterns in SCAM_KEYWORDS.items():
        cat_matches = 0
        for pattern in patterns:
            if re.search(pattern, text_lower):
                cat_matches += 1
        matches[category] = cat_matches
        total_matches += cat_matches

    # Find category with most matches
    max_cat = "none"
    max_matches = 0
    for category, count in matches.items():
        if count > max_matches:
            max_matches = count
            max_cat = category

    # Calculate risk score
    # Base risk is higher if we match keywords.
    if total_matches == 0:
        # Check general scam-like behaviors: urgency, threat, money, numbers
        urgency_words = ["now", "today", "quick", "hurry", "expire"]
        urgency_count = sum(1 for w in urgency_words if w in text_lower)
        if urgency_count > 0:
            return 35.0, "suspicious outreach"
        return 10.0, "clean"
    
    # Calculate score based on intensity of matches
    risk_score = min(40.0 + (total_matches * 15.0), 100.0)
    return risk_score, max_cat

async def analyze_scam_intent(text: str) -> Dict[str, Any]:
    """
    Analyzes scam intent using rules or LLM based on configuration.
    """
    # Default fallback to heuristics
    risk_score, category = analyze_scam_heuristics(text)
    
    if settings.LLM_PROVIDER == "gemini" and settings.GEMINI_API_KEY:
        try:
            # We call Gemini API via HTTP post request
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={settings.GEMINI_API_KEY}"
            prompt = (
                "You are a scam analysis engine. Analyze the following incoming message for scam/fraud intent. "
                "Classify the message and calculate a risk score from 0 (completely safe) to 100 (confirmed scam). "
                "Classify into one of: 'bank threat', 'upi fraud', 'phishing', 'fake offer', 'clean'.\n"
                f"Message: \"{text}\"\n"
                "Return JSON exactly in this format:\n"
                "{\n"
                "  \"risk_score\": <number 0-100>,\n"
                "  \"scam_category\": \"<category>\"\n"
                "}"
            )
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"responseMimeType": "application/json"}
            }
            async with httpx.AsyncClient() as client:
                res = await client.post(url, json=payload, timeout=5.0)
                if res.status_code == 200:
                    data = res.json()
                    # Parse the text response which is JSON
                    import json
                    text_response = data["candidates"][0]["content"]["parts"][0]["text"]
                    parsed = json.loads(text_response.strip())
                    return {
                        "risk_score": float(parsed.get("risk_score", risk_score)),
                        "scam_category": parsed.get("scam_category", category)
                    }
        except Exception as e:
            print(f"Gemini Scam Detection API Error, falling back to heuristics: {e}")
            
    elif settings.LLM_PROVIDER == "openai" and settings.OPENAI_API_KEY:
        try:
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                "Content-Type": "application/json"
            }
            prompt = (
                "Analyze the following incoming message for scam/fraud intent. "
                "Classify the message and calculate a risk score from 0 (completely safe) to 100 (confirmed scam). "
                "Classify into one of: 'bank threat', 'upi fraud', 'phishing', 'fake offer', 'clean'.\n"
                f"Message: \"{text}\"\n"
                "Return JSON exactly in this format:\n"
                "{\n"
                "  \"risk_score\": <number 0-100>,\n"
                "  \"scam_category\": \"<category>\"\n"
                "}"
            )
            payload = {
                "model": "gpt-4o-mini",
                "response_format": {"type": "json_object"},
                "messages": [{"role": "user", "content": prompt}]
            }
            async with httpx.AsyncClient() as client:
                res = await client.post(url, json=payload, headers=headers, timeout=5.0)
                if res.status_code == 200:
                    data = res.json()
                    import json
                    text_response = data["choices"][0]["message"]["content"]
                    parsed = json.loads(text_response.strip())
                    return {
                        "risk_score": float(parsed.get("risk_score", risk_score)),
                        "scam_category": parsed.get("scam_category", category)
                    }
        except Exception as e:
            print(f"OpenAI Scam Detection API Error, falling back to heuristics: {e}")

    return {
        "risk_score": risk_score,
        "scam_category": category
    }
