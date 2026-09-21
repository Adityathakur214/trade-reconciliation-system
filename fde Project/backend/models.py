from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
import enum
import datetime
from database import Base

class CaseSeverity(str, enum.Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class CaseState(str, enum.Enum):
    OPEN = "OPEN"
    INVESTIGATING = "INVESTIGATING"
    NEEDS_SOURCE = "NEEDS_SOURCE"
    RESOLVED = "RESOLVED"
    REOPENED = "REOPENED"

class Role(str, enum.Enum):
    OPS_LEAD = "OPS_LEAD"
    INVESTIGATOR = "INVESTIGATOR"
    AUDITOR = "AUDITOR"
    SUPPORT = "SUPPORT"

class DiscrepancyCase(Base):
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(String, index=True)
    isin = Column(String, index=True, nullable=True) 
    
    # Financial Discrepancies - MUST be Integers as per requirements
    internal_qty = Column(Integer, default=0)
    dp_qty = Column(Integer, default=0)
    qty_delta = Column(Integer, default=0)
    
    internal_cash_paise = Column(Integer, default=0)
    bank_cash_paise = Column(Integer, default=0)
    
    # Metadata & States
    cut_at = Column(DateTime, nullable=False)
    state = Column(Enum(CaseState), default=CaseState.OPEN)
    severity = Column(Enum(CaseSeverity), default=CaseSeverity.MEDIUM)
    
    # Missing/Conflict States from instructions
    evidence_status = Column(String) # e.g., "MISSING_SOURCE", "CONFLICTING_EVIDENCE"
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    notes = relationship("CaseNote", back_populates="case")

class CaseNote(Base):
    __tablename__ = "case_notes"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"))
    author_role = Column(Enum(Role))
    note_text = Column(Text, nullable=False)
    evidence_version_ref = Column(String) # To track which file version they relied on
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    case = relationship("DiscrepancyCase", back_populates="notes")