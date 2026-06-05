import time
from typing import List
from fastapi import FastAPI, Depends, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlmodel import Session as DBSession, select

from app.config import settings
from app.database import init_db, get_db_session
from app.auth import verify_api_key
from app.schemas import MessageEventRequest, MessageEventResponse, SessionReportResponse, ExtractedIntelligenceSchema
from app.models import Session, Message, ExtractedIntelligence, CallbackReport
from app.services.scam_engine import analyze_scam_intent
from app.services.persona_agent import generate_persona_reply
from app.services.extractor import extract_intelligence
from app.services.callback import dispatch_callback

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize db on startup
    init_db()
    yield

app = FastAPI(
    title="TrapTalk AI - Scam Honeypot API",
    description="API-first agentic scam honeypot platform",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post(
    "/api/v1/engage",
    response_model=MessageEventResponse,
    dependencies=[Depends(verify_api_key)],
    summary="Receive message event, process scam risk, and engage the scammer."
)
async def engage(
    payload: MessageEventRequest,
    db: DBSession = Depends(get_db_session)
):
    # 1. Fetch or create Session
    session_id = payload.sessionId
    db_session = db.exec(select(Session).where(Session.session_id == session_id)).first()
    
    if not db_session:
        # Create new Session
        db_session = Session(
            session_id=session_id,
            scam_detected=False,
            risk_score=0.0,
            scam_category=None,
            total_messages_exchanged=0,
            status="active",
            metadata_json=payload.metadata.dict() if payload.metadata else None
        )
        db.add(db_session)
        db.commit()
        db.refresh(db_session)

    # 2. Get or create Extracted Intelligence
    intelligence = db.exec(select(ExtractedIntelligence).where(ExtractedIntelligence.session_id == session_id)).first()
    if not intelligence:
        intelligence = ExtractedIntelligence(
            session_id=session_id,
            bank_accounts=[],
            upi_ids=[],
            phishing_links=[],
            phone_numbers=[],
            suspicious_keywords=[],
            agent_notes=""
        )
        db.add(intelligence)
        db.commit()
        db.refresh(intelligence)

    # 3. Save incoming Scammer Message
    new_message = Message(
        session_id=session_id,
        sender=payload.message.sender,
        text=payload.message.text,
        timestamp=payload.message.timestamp
    )
    db.add(new_message)
    
    # 4. Run Scam Detection Engine
    scam_result = await analyze_scam_intent(payload.message.text)
    
    # Update session risk and category
    db_session.risk_score = max(db_session.risk_score, scam_result["risk_score"])
    if scam_result["scam_category"] != "clean":
        db_session.scam_category = scam_result["scam_category"]
        
    # Activate agent if risk is high enough
    if db_session.risk_score > 30.0:
        db_session.scam_detected = True

    # 5. Build conversation history list for context
    db.commit()
    db.refresh(db_session)
    
    # Query all messages so far to feed LLM/Agent
    history_messages = db.exec(
        select(Message)
        .where(Message.session_id == session_id)
        .order_by(Message.timestamp.asc())
    ).all()
    
    history_list = [
        {"sender": msg.sender, "text": msg.text, "timestamp": msg.timestamp}
        for msg in history_messages[:-1]  # Exclude the very last message we just saved
    ]

    # 6. Run Intelligence Extractor and Persona Agent if scam detected
    if db_session.scam_detected:
        # Load existing intelligence to merge
        existing_data = {
            "bankAccounts": intelligence.bank_accounts,
            "upiIds": intelligence.upi_ids,
            "phishingLinks": intelligence.phishing_links,
            "phoneNumbers": intelligence.phone_numbers,
            "suspiciousKeywords": intelligence.suspicious_keywords,
            "agentNotes": intelligence.agent_notes
        }
        
        # Incremental extraction
        merged_intel = await extract_intelligence(
            text=payload.message.text,
            conversation_history=history_list,
            existing_data=existing_data
        )
        
        # Save merged intelligence
        intelligence.bank_accounts = merged_intel["bankAccounts"]
        intelligence.upi_ids = merged_intel["upiIds"]
        intelligence.phishing_links = merged_intel["phishingLinks"]
        intelligence.phone_numbers = merged_intel["phoneNumbers"]
        intelligence.suspicious_keywords = merged_intel["suspiciousKeywords"]
        intelligence.agent_notes = merged_intel["agentNotes"]
        db.add(intelligence)

        # Generate persona reply
        reply_text = await generate_persona_reply(
            text=payload.message.text,
            history=history_list,
            category=db_session.scam_category or "clean"
        )
    else:
        # Default clean fallback reply if no scam is detected
        reply_text = "Sorry, I think you have the wrong number."

    # 7. Save generated Agent Reply
    agent_message = Message(
        session_id=session_id,
        sender="agent",
        text=reply_text,
        timestamp=int(time.time() * 1000)
    )
    db.add(agent_message)
    
    # Update total counts
    db_session.total_messages_exchanged = len(history_messages) + 1
    
    db.add(db_session)
    db.commit()

    return MessageEventResponse(
        status="success",
        reply=reply_text
    )

@app.post(
    "/api/v1/sessions/{session_id}/close",
    response_model=SessionReportResponse,
    dependencies=[Depends(verify_api_key)],
    summary="Close active session, compile fraud reports, and dispatch to callback."
)
async def close_session(
    session_id: str,
    db: DBSession = Depends(get_db_session)
):
    db_session = db.exec(select(Session).where(Session.session_id == session_id)).first()
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    intelligence = db.exec(select(ExtractedIntelligence).where(ExtractedIntelligence.session_id == session_id)).first()
    if not intelligence:
        intelligence = ExtractedIntelligence(
            session_id=session_id,
            bank_accounts=[],
            upi_ids=[],
            phishing_links=[],
            phone_numbers=[],
            suspicious_keywords=[],
            agent_notes="No intelligence gathered."
        )
        db.add(intelligence)
        db.commit()
        db.refresh(intelligence)
        
    # Update session status
    db_session.status = "completed"
    db_session.updated_at = db_session.created_at # Keep metadata clean or set updated_at
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    
    # Compile report response
    report = SessionReportResponse(
        sessionId=db_session.session_id,
        scamDetected=db_session.scam_detected,
        totalMessagesExchanged=db_session.total_messages_exchanged,
        extractedIntelligence=ExtractedIntelligenceSchema(
            bankAccounts=intelligence.bank_accounts,
            upiIds=intelligence.upi_ids,
            phishingLinks=intelligence.phishing_links,
            phoneNumbers=intelligence.phone_numbers,
            suspiciousKeywords=intelligence.suspicious_keywords
        ),
        agentNotes=intelligence.agent_notes
    )
    
    # Dispatch callback in background
    # (Using dict formatting for network payload compatibility)
    payload_dict = report.dict(by_alias=True)
    await dispatch_callback(session_id, payload_dict, db)
    
    return report

@app.get(
    "/api/v1/sessions/{session_id}/report",
    response_model=SessionReportResponse,
    dependencies=[Depends(verify_api_key)],
    summary="Get current report details for a specific session."
)
def get_session_report(
    session_id: str,
    db: DBSession = Depends(get_db_session)
):
    db_session = db.exec(select(Session).where(Session.session_id == session_id)).first()
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    intelligence = db.exec(select(ExtractedIntelligence).where(ExtractedIntelligence.session_id == session_id)).first()
    if not intelligence:
        raise HTTPException(status_code=404, detail="Intelligence not found for this session")
        
    return SessionReportResponse(
        sessionId=db_session.session_id,
        scamDetected=db_session.scam_detected,
        totalMessagesExchanged=db_session.total_messages_exchanged,
        extractedIntelligence=ExtractedIntelligenceSchema(
            bankAccounts=intelligence.bank_accounts,
            upiIds=intelligence.upi_ids,
            phishingLinks=intelligence.phishing_links,
            phoneNumbers=intelligence.phone_numbers,
            suspiciousKeywords=intelligence.suspicious_keywords
        ),
        agentNotes=intelligence.agent_notes
    )

# Mock GUVI Callback Endpoint for Local Testing
@app.post(
    "/api/v1/mock-callback",
    status_code=status.HTTP_200_OK,
    summary="Mock callback endpoint for testing target webhooks."
)
def mock_callback(report: SessionReportResponse):
    print(f"Mock Callback Received Report for Session: {report.sessionId}")
    return {"status": "success", "message": "Callback processed successfully"}
