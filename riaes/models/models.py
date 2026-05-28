from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Enum, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum
from riaes.database import Base

class TaskStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTED = "executed"

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String, unique=True, index=True)
    name = Column(String)
    description = Column(String)
    category = Column(String)
    base_price = Column(Float)
    current_price = Column(Float)
    cost = Column(Float)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class Inventory(Base):
    __tablename__ = "inventory"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity_on_hand = Column(Integer)
    location = Column(String)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class CompetitorPrice(Base):
    __tablename__ = "competitor_prices"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    competitor_name = Column(String)
    price = Column(Float)
    is_on_sale = Column(Boolean, default=False)
    observed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class AgentTask(Base):
    __tablename__ = "agent_tasks"
    id = Column(Integer, primary_key=True, index=True)
    agent_name = Column(String)
    task_type = Column(String) # e.g., "PRICE_CHANGE", "REORDER"
    description = Column(String)
    payload = Column(JSON) # Data required for execution
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class Recommendation(Base):
    __tablename__ = "recommendations"
    id = Column(Integer, primary_key=True, index=True)
    agent_name = Column(String)
    product_id = Column(Integer, ForeignKey("products.id"))
    action = Column(String)
    impact_estimate = Column(Float)
    reasoning = Column(String)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
