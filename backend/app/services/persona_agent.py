# pyrefly: ignore [missing-import]
import httpx
from typing import List, Dict, Any
from app.config import settings

# A believable, non-technical persona
SYSTEM_PERSONA = (
    "You are Ramesh, a 58-year-old retired clerk. You are not very good with technology, "
    "get easily confused, and speak in a polite, slightly slow, and worried manner. "
    "You are eager to resolve the problem but need step-by-step guidance. "
    "CRITICAL CONSTRAINTS:\n"
    "1. Never mention that you are an AI, a bot, or a honeypot.\n"
    "2. Never show that you suspect fraud or scam. Be completely cooperative and gullible.\n"
    "3. Keep replies relatively short (1-2 sentences), natural, and realistic.\n"
    "4. Ask questions that prompt the scammer to give you payment details (e.g., 'Which UPI ID should I pay?', 'Can you send me a link?', 'Is there a number I can call?').\n"
    "5. Avoid robotic or template-like language."
)

MOCK_RESPONSES = {
    "bank threat": [
        "Oh no, please don't block my card! I need it for my medicine. What should I do to verify?",
        "I am trying to open my banking app but it says password incorrect. Can you tell me which link to use?",
        "Where is the verification option? Can I call you on this number to clear it up?"
    ],
    "upi fraud": [
        "I opened my UPI app but I don't see the request. Can you send me the scanner or the exact UPI ID to pay?",
        "Is it secure to pay here? Should I transfer to phone number or UPI handle?",
        "My daughter usually does these UPI payments. Can you tell me which mobile number she should send it to?"
    ],
    "phishing": [
        "I clicked the link but the page is just loading black. Is there another website address I should go to?",
        "It is asking for my card number and ATM pin on this page. Is that safe?",
        "Can you send the login link again? The previous link got deleted from my messages."
    ],
    "fake offer": [
        "I won the prize?! Oh my god, thank you so much! How do I claim the cashback?",
        "Do I need to pay any processing fees first? Where do I send the money?",
        "Can you send the reward link or scanner so I can receive my prize?"
    ],
    "clean": [
        "Hello, who is this?",
        "Yes, how can I help you?",
        "Sorry, I think you have the wrong number."
    ]
}

def clean_and_self_correct(text: str) -> str:
    """
    Scans the response for system leakage or AI behaviors and corrects them.
    """
    leakage_keywords = [
        "honeypot", "scam detected", "fraud detected", "i am an ai", 
        "i am a bot", "artificial intelligence", "language model", 
        "simulation", "as Ramesh", "persona"
    ]
    
    lower_text = text.lower()
    for kw in leakage_keywords:
        if kw in lower_text:
            # Self-correct by returning a natural persona fallback
            return "Oh, my phone screen is flickering. Can you explain that again simply? What should I do next?"
            
    return text

async def generate_persona_reply(
    text: str, 
    history: List[Dict[str, Any]], 
    category: str
) -> str:
    """
    Generates a reply conforming to the persona.
    """
    # 1. Fallback to mock responses if mock mode
    if settings.LLM_PROVIDER == "mock" or (settings.LLM_PROVIDER == "gemini" and not settings.GEMINI_API_KEY) or (settings.LLM_PROVIDER == "openai" and not settings.OPENAI_API_KEY):
        turn_index = len(history) % len(MOCK_RESPONSES.get(category, MOCK_RESPONSES["clean"]))
        reply = MOCK_RESPONSES.get(category, MOCK_RESPONSES["clean"])[turn_index]
        return clean_and_self_correct(reply)

    # 2. Build standard conversation formatting for LLM APIs
    messages_payload = []
    
    # We include system prompt instructions
    if settings.LLM_PROVIDER == "openai":
        messages_payload.append({"role": "system", "content": SYSTEM_PERSONA})
        for turn in history:
            role = "assistant" if turn["sender"] == "agent" else "user"
            messages_payload.append({"role": role, "content": turn["text"]})
        messages_payload.append({"role": "user", "content": text})
        
        try:
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "gpt-4o-mini",
                "messages": messages_payload,
                "temperature": 0.7,
                "max_tokens": 100
            }
            async with httpx.AsyncClient() as client:
                res = await client.post(url, json=payload, headers=headers, timeout=5.0)
                if res.status_code == 200:
                    data = res.json()
                    reply = data["choices"][0]["message"]["content"].strip()
                    return clean_and_self_correct(reply)
        except Exception as e:
            print(f"OpenAI Persona API call failed: {e}")

    elif settings.LLM_PROVIDER == "gemini":
        # Format for Gemini generateContent endpoint
        gemini_contents = []
        # Add system instructions separately inside systemInstruction parameter (if supported) or prepend to context
        system_instruction_part = {"parts": [{"text": SYSTEM_PERSONA}]}
        
        # Build history
        for turn in history:
            role = "model" if turn["sender"] == "agent" else "user"
            gemini_contents.append({"role": role, "parts": [{"text": turn["text"]}]})
        gemini_contents.append({"role": "user", "parts": [{"text": text}]})

        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={settings.GEMINI_API_KEY}"
            payload = {
                "contents": gemini_contents,
                "systemInstruction": system_instruction_part,
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 100
                }
            }
            async with httpx.AsyncClient() as client:
                res = await client.post(url, json=payload, timeout=5.0)
                if res.status_code == 200:
                    data = res.json()
                    reply = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                    return clean_and_self_correct(reply)
        except Exception as e:
            print(f"Gemini Persona API call failed: {e}")

    # Ultimate fallback if APIs fail or credentials are empty
    turn_index = len(history) % len(MOCK_RESPONSES.get(category, MOCK_RESPONSES["clean"]))
    return clean_and_self_correct(MOCK_RESPONSES.get(category, MOCK_RESPONSES["clean"])[turn_index])
