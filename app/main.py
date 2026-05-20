from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import engine, Base, get_db
from app.models import models
from app.schemas.schemas import TrackRequest, ProfileResponse, IdentifierSchema, TraitSchema
from app.services.identity_service import IdentityResolutionService

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Identity Resolution API")

@app.post("/track", response_model=ProfileResponse)
def track_event(request: TrackRequest, db: Session = Depends(get_db)):
    service = IdentityResolutionService(db)
    profile = service.resolve_and_track(
        identifiers=[id.model_dump() for id in request.identifiers],
        traits=[trait.model_dump() for trait in request.traits],
        event=request.event.model_dump() if request.event else None
    )

    return profile

@app.get("/profile/{id_type}/{id_value}", response_model=ProfileResponse)
def get_profile(id_type: str, id_value: str, db: Session = Depends(get_db)):
    service = IdentityResolutionService(db)
    profile = service.get_profile_by_identifier(id_type, id_value)

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    return profile

@app.get("/health")
def health_check():
    return {"status": "healthy"}
