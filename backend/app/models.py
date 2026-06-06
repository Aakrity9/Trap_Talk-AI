from datetime import datetime
from typing import List, Optional, Dict, Any
# pyrefly: ignore [missing-import]
from sqlmodel import SQLModel, Field, Relationship, Column, JSON

class Session(SQLModel, table=True):
    __tablename__ = "sessions"
    
    session_id: str = Field(default=None, primary_key=True)
    scam_detected: bool = Field(default=False)
    risk_score: float = Field(default=0.0)
    scam_category: Optional[str] = Field(default=None)
    total_messages_exchanged: int = Field(default=0)
    status: str = Field(default="active")  # "active", "completed", "escalated"
    metadata_json: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    messages: List["Message"] = Relationship(back_populates="session", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    extracted_intelligence: Optional["ExtractedIntelligence"] = Relationship(back_populates="session", sa_relationship_kwargs={"cascade": "all, delete-orphan", "uselist": False})

class Message(SQLModel, table=True):
    __tablename__ = "messages"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: str = Field(foreign_key="sessions.session_id")
    sender: str = Field(..., description="scammer or agent")
    text: str = Field(...)
    timestamp: int = Field(description="Epoch millisecond timestamp")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship back to session
    session: Session = Relationship(back_populates="messages")

class ExtractedIntelligence(SQLModel, table=True):
    __tablename__ = "extracted_intelligence"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: str = Field(foreign_key="sessions.session_id", unique=True)
    bank_accounts: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    upi_ids: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    phishing_links: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    phone_numbers: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    suspicious_keywords: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    agent_notes: str = Field(default="")
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship back to session
    session: Session = Relationship(back_populates="extracted_intelligence")

class CallbackReport(SQLModel, table=True):
    __tablename__ = "callback_reports"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: str = Field(foreign_key="sessions.session_id")
    callback_url: str = Field(...)
    status_code: Optional[int] = Field(default=None)
    success: bool = Field(default=False)
    response_text: Optional[str] = Field(default=None)
    sent_at: datetime = Field(default_factory=datetime.utcnow)
