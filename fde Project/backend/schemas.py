from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from models import CaseSeverity, CaseState, Role

class CaseNoteCreate(BaseModel):
    author_role: Role
    note_text: str
    evidence_version_ref: Optional[str] = None

class CaseNoteResponse(BaseModel):
    id: int
    author_role: Role
    note_text: str
    evidence_version_ref: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class DiscrepancyCaseResponse(BaseModel):
    id: int
    client_id: str
    isin: Optional[str]
    internal_qty: int
    dp_qty: int
    qty_delta: int
    internal_cash_paise: int
    bank_cash_paise: int
    cut_at: datetime
    state: CaseState
    severity: CaseSeverity
    evidence_status: Optional[str]
    notes: List[CaseNoteResponse] = []

    class Config:
        from_attributes = True