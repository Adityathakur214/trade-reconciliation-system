import pandas as pd
from datetime import datetime
from sqlalchemy.orm import Session
import models

def process_internal_holdings(file_path: str, db: Session, cut_at: datetime):
    """Parses internal holdings CSV and initializes cases."""
    # Read CSV using Pandas
    df = pd.read_csv(file_path)
    
    for _, row in df.iterrows():
        client_id = str(row.get('client_id'))
        isin = str(row.get('ISIN'))
        qty = int(row.get('quantity', 0))
        
        # Check if case exists for this client, ISIN, and cut
        case = db.query(models.DiscrepancyCase).filter(
            models.DiscrepancyCase.client_id == client_id,
            models.DiscrepancyCase.isin == isin,
            models.DiscrepancyCase.cut_at == cut_at
        ).first()
        
        if not case:
            case = models.DiscrepancyCase(
                client_id=client_id,
                isin=isin,
                internal_qty=qty,
                cut_at=cut_at,
                qty_delta=qty,  # Delta is internal qty until DP data arrives
                state=models.CaseState.OPEN,
                severity=models.CaseSeverity.HIGH # Non-zero delta is HIGH severity
            )
            db.add(case)
        else:
            case.internal_qty = qty
            case.qty_delta = case.internal_qty - case.dp_qty
            
    db.commit()

def process_dp_positions(file_path: str, db: Session, cut_at: datetime):
    """Parses HTML table from Depository and reconciles with internal holdings."""
    # Pandas can instantly parse HTML tables
    tables = pd.read_html(file_path)
    if not tables:
        return
    df = tables[0]
    
    for _, row in df.iterrows():
        client_id = str(row.get('client_id'))
        isin = str(row.get('ISIN'))
        state = str(row.get('movement_state', '')).strip().upper()
        
        # Rule 2: Pending movements must not silently become a settled holding
        if state == 'PENDING':
            continue 
            
        qty = int(row.get('settled_quantity', 0))
        
        case = db.query(models.DiscrepancyCase).filter(
            models.DiscrepancyCase.client_id == client_id,
            models.DiscrepancyCase.isin == isin,
            models.DiscrepancyCase.cut_at == cut_at
        ).first()
        
        if case:
            case.dp_qty = qty
            case.qty_delta = case.internal_qty - case.dp_qty
            
            # Auto-resolve if quantities match perfectly
            if case.qty_delta == 0:
                case.state = models.CaseState.RESOLVED
                case.severity = models.CaseSeverity.LOW
        else:
            # DP holding exists but internal doesn't (MISSING_SOURCE)
            new_case = models.DiscrepancyCase(
                client_id=client_id,
                isin=isin,
                dp_qty=qty,
                qty_delta=-qty,
                cut_at=cut_at,
                evidence_status="MISSING_SOURCE",
                state=models.CaseState.NEEDS_SOURCE,
                severity=models.CaseSeverity.HIGH
            )
            db.add(new_case)
            
    db.commit()