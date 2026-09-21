from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import shutil
import os
from datetime import datetime

import models, schemas, ingestion
from database import engine, get_db

# Database tables create karna
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="FDE Operations Exception Desk", version="1.0")

# CORS Middleware lagaya gaya hai taaki React (port 5173) se request aa sake
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "FDE Operations Desk API is running. Check /docs for API details."}

@app.get("/cases", response_model=List[schemas.DiscrepancyCaseResponse])
def get_cases(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    cases = db.query(models.DiscrepancyCase).offset(skip).limit(limit).all()
    return cases

@app.get("/cases/{case_id}", response_model=schemas.DiscrepancyCaseResponse)
def get_case(case_id: int, db: Session = Depends(get_db)):
    case = db.query(models.DiscrepancyCase).filter(models.DiscrepancyCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case

@app.post("/cases/{case_id}/notes", response_model=schemas.CaseNoteResponse)
def add_note(case_id: int, note: schemas.CaseNoteCreate, db: Session = Depends(get_db)):
    if note.author_role not in [models.Role.INVESTIGATOR, models.Role.OPS_LEAD]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Auditors and Support cannot add notes"
        )
        
    case = db.query(models.DiscrepancyCase).filter(models.DiscrepancyCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
        
    new_note = models.CaseNote(
        case_id=case_id,
        author_role=note.author_role,
        note_text=note.note_text,
        evidence_version_ref=note.evidence_version_ref
    )
    db.add(new_note)
    db.commit()
    db.refresh(new_note)
    return new_note

@app.post("/imports/holdings")
async def import_holdings_data(
    cut_at: str = Form(...),
    internal_file: UploadFile = File(...),
    dp_file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Z-timezone error ko fix karne ke liye replace lagaya
    cut_time = datetime.fromisoformat(cut_at.replace("Z", "+00:00"))
    
    # Save uploaded files temporarily
    os.makedirs("temp_data", exist_ok=True)
    internal_path = f"temp_data/{internal_file.filename}"
    dp_path = f"temp_data/{dp_file.filename}"
    
    with open(internal_path, "wb") as buffer:
        shutil.copyfileobj(internal_file.file, buffer)
        
    with open(dp_path, "wb") as buffer:
        shutil.copyfileobj(dp_file.file, buffer)
        
    # Run the ingestion engine
    ingestion.process_internal_holdings(internal_path, db, cut_time)
    ingestion.process_dp_positions(dp_path, db, cut_time)
    
    # Clean up
    os.remove(internal_path)
    os.remove(dp_path)
    
    return {"message": "Files ingested and reconciled successfully", "cut_at": cut_time}