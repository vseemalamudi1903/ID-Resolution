from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class IdentifierSchema(BaseModel):
    type: str
    value: str

class TraitSchema(BaseModel):
    type: str
    value: str

class EventSchema(BaseModel):
    event_type: str
    category: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class TrackRequest(BaseModel):
    identifiers: List[IdentifierSchema]
    traits: List[TraitSchema] = Field(default_factory=list)
    event: Optional[EventSchema] = None

class InterestScoreSchema(BaseModel):
    category: str
    score: float
    updated_at: datetime

    class Config:
        from_attributes = True

class ProfileResponse(BaseModel):
    canonical_id: str
    identifiers: List[IdentifierSchema]
    traits: List[TraitSchema]
    interest_scores: List[InterestScoreSchema]
    created_at: datetime

    class Config:
        from_attributes = True
