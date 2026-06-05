import re
from typing import List, Dict, Any
from app.config import settings
import httpx

# Regex Patterns for extraction
UPI_REGEX = r"\b[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}\b"
URL_REGEX = r"\bhttps?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}(?:/[a-zA-Z0-9.\-_~%&?#=]*)?\b"
PHONE_REGEX = r"\+?91[6789]\d{9}\b|\b[6789]\d{9}\b|\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b"
BANK_REGEX = r"\b\d{9,18}\b|\b\d{4}[- ]\d{4}[- ]\d{4}[- ]\d{4}\b"

KEYWORDS_LIST = [
    "verify", "blocked", "suspended", "urgent", "immediately", "lottery",
    "cashback", "crore", "lakh", "atm pin", "otp", "password", "aadhaar", "pan card"
]

def extract_entities_regex(text: str) -> Dict[str, Any]:
    """
    Regex-based entity extraction.
    """
    upi_ids = re.findall(UPI_REGEX, text)
    links = re.findall(URL_REGEX, text)
    phones = re.findall(PHONE_REGEX, text)
    
    # Simple bank account search (digits of length 9 to 18 or card pattern)
    raw_bank = re.findall(BANK_REGEX, text)
    bank_accounts = []
    for val in raw_bank:
        clean_val = val.replace("-", "").replace(" ", "")
        # Filter out phone numbers matching bank account patterns
        if clean_val not in [p.replace("+", "") for p in phones]:
            bank_accounts.append(val)

    # Keyword check
    text_lower = text.lower()
    suspicious_keywords = []
    for kw in KEYWORDS_LIST:
        if kw in text_lower:
            suspicious_keywords.append(kw)

    return {
        "bankAccounts": list(set(bank_accounts)),
        "upiIds": list(set(upi_ids)),
        "phishingLinks": list(set(links)),
        "phoneNumbers": list(set(phones)),
        "suspiciousKeywords": list(set(suspicious_keywords)),
        "agentNotes": ""
    }

async def extract_intelligence(
    text: str, 
    conversation_history: List[Dict[str, Any]], 
    existing_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Incremental intelligence extraction engine.
    Compares existing data with new text extracts and merges them without duplicates.
    """
    # 1. Start with Regex extraction on the new message
    new_extracted = extract_entities_regex(text)

    # 2. Merge with existing data
    merged = {
        "bankAccounts": list(set(existing_data.get("bankAccounts", []) + new_extracted["bankAccounts"])),
        "upiIds": list(set(existing_data.get("upiIds", []) + new_extracted["upiIds"])),
        "phishingLinks": list(set(existing_data.get("phishingLinks", []) + new_extracted["phishingLinks"])),
        "phoneNumbers": list(set(existing_data.get("phoneNumbers", []) + new_extracted["phoneNumbers"])),
        "suspiciousKeywords": list(set(existing_data.get("suspiciousKeywords", []) + new_extracted["suspiciousKeywords"])),
        "agentNotes": existing_data.get("agentNotes", "")
    }

    # 3. Compile agent notes based on history & category
    history_len = len(conversation_history)
    scam_signals = []
    if merged["upiIds"]:
        scam_signals.append("requested payments via UPI")
    if merged["phishingLinks"]:
        scam_signals.append("shared phishing redirects")
    if merged["bankAccounts"]:
        scam_signals.append("disclosed bank account routing details")
    
    signals_str = ", ".join(scam_signals)
    if signals_str:
        merged["agentNotes"] = f"Scammer interacted across {history_len + 1} turns and {signals_str}."
    else:
        merged["agentNotes"] = f"Scammer engaged in multi-turn conversation (total turns: {history_len + 1})."

    # 4. If LLM provider is configured, enrich using LLM
    if settings.LLM_PROVIDER == "gemini" and settings.GEMINI_API_KEY:
        # Build transcription
        transcript = ""
        for turn in conversation_history:
            transcript += f"{turn['sender'].upper()}: {turn['text']}\n"
        transcript += f"SCAMMER (LATEST): {text}\n"

        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={settings.GEMINI_API_KEY}"
            prompt = (
                "You are an anti-fraud intelligence parser. Extract structured details from this conversation transcript.\n"
                f"Transcript:\n{transcript}\n"
                "Extract all: bank account numbers, UPI IDs, phishing links, phone numbers, and suspicious phrases. "
                "Also write a 1-sentence note summarizing the scammer's strategy (agentNotes).\n"
                "Return JSON exactly in this format:\n"
                "{\n"
                "  \"bankAccounts\": [...],\n"
                "  \"upiIds\": [...],\n"
                "  \"phishingLinks\": [...],\n"
                "  \"phoneNumbers\": [...],\n"
                "  \"suspiciousKeywords\": [...],\n"
                "  \"agentNotes\": \"...\"\n"
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
                    import json
                    text_response = data["candidates"][0]["content"]["parts"][0]["text"]
                    parsed = json.loads(text_response.strip())
                    
                    # Merge LLM results with regex results
                    merged["bankAccounts"] = list(set(merged["bankAccounts"] + parsed.get("bankAccounts", [])))
                    merged["upiIds"] = list(set(merged["upiIds"] + parsed.get("upiIds", [])))
                    merged["phishingLinks"] = list(set(merged["phishingLinks"] + parsed.get("phishingLinks", [])))
                    merged["phoneNumbers"] = list(set(merged["phoneNumbers"] + parsed.get("phoneNumbers", [])))
                    merged["suspiciousKeywords"] = list(set(merged["suspiciousKeywords"] + parsed.get("suspiciousKeywords", [])))
                    if parsed.get("agentNotes"):
                        merged["agentNotes"] = parsed["agentNotes"]
        except Exception as e:
            print(f"Gemini Extractor Error, falling back to regex: {e}")

    elif settings.LLM_PROVIDER == "openai" and settings.OPENAI_API_KEY:
        transcript = ""
        for turn in conversation_history:
            transcript += f"{turn['sender'].upper()}: {turn['text']}\n"
        transcript += f"SCAMMER (LATEST): {text}\n"

        try:
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                "Content-Type": "application/json"
            }
            prompt = (
                "Extract structured fraud intelligence details from this transcript.\n"
                f"Transcript:\n{transcript}\n"
                "Return JSON exactly in this format:\n"
                "{\n"
                "  \"bankAccounts\": [...],\n"
                "  \"upiIds\": [...],\n"
                "  \"phishingLinks\": [...],\n"
                "  \"phoneNumbers\": [...],\n"
                "  \"suspiciousKeywords\": [...],\n"
                "  \"agentNotes\": \"...\"\n"
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
                    
                    merged["bankAccounts"] = list(set(merged["bankAccounts"] + parsed.get("bankAccounts", [])))
                    merged["upiIds"] = list(set(merged["upiIds"] + parsed.get("upiIds", [])))
                    merged["phishingLinks"] = list(set(merged["phishingLinks"] + parsed.get("phishingLinks", [])))
                    merged["phoneNumbers"] = list(set(merged["phoneNumbers"] + parsed.get("phoneNumbers", [])))
                    merged["suspiciousKeywords"] = list(set(merged["suspiciousKeywords"] + parsed.get("suspiciousKeywords", [])))
                    if parsed.get("agentNotes"):
                        merged["agentNotes"] = parsed["agentNotes"]
        except Exception as e:
            print(f"OpenAI Extractor Error, falling back to regex: {e}")

    return merged
