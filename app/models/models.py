from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

class Profile(Base):
    __tablename__ = "profiles"
    id = Column(Integer, primary_key=True, index=True)
    canonical_id = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    identifiers = relationship("Identifier", back_populates="profile", cascade="all, delete-orphan", lazy="selectin")
    traits = relationship("IdentityTrait", back_populates="profile", cascade="all, delete-orphan", lazy="selectin")
    events = relationship("BehavioralEvent", back_populates="profile", cascade="all, delete-orphan", lazy="selectin")
    interest_scores = relationship("InterestScore", back_populates="profile", cascade="all, delete-orphan", lazy="selectin")

class Identifier(Base):
    __tablename__ = "identifiers"
    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"))
    type = Column(String, index=True) # email, loyalty_id, phone, cookie_id, etc.
    value = Column(String, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (UniqueConstraint('type', 'value', name='_type_value_uc'),)

    profile = relationship("Profile", back_populates="identifiers")

class IdentityTrait(Base):
    __tablename__ = "identity_traits"
    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"))
    type = Column(String, index=True) # ip, fingerprint
    value = Column(String, index=True)
    last_seen = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    profile = relationship("Profile", back_populates="traits")

class BehavioralEvent(Base):
    __tablename__ = "behavioral_events"
    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"))
    event_type = Column(String, index=True) # page_view, product_view, review, etc.
    category = Column(String, index=True) # e.g., Electronics, Fashion
    metadata_json = Column(String) # For additional event details
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    profile = relationship("Profile", back_populates="events")

class InterestScore(Base):
    __tablename__ = "interest_scores"
    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"))
    category = Column(String, index=True)
    score = Column(Float, default=0.0)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    profile = relationship("Profile", back_populates="interest_scores")
