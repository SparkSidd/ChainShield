import uuid
from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

class EventSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class EventType(str, Enum):
    DEMAND_ARRIVED = "DEMAND_ARRIVED"
    ORDER_FULFILLED = "ORDER_FULFILLED"
    ORDER_UNFULFILLED = "ORDER_UNFULFILLED"
    REORDER_TRIGGERED = "REORDER_TRIGGERED"
    PRODUCTION_STARTED = "PRODUCTION_STARTED"
    PRODUCTION_COMPLETED = "PRODUCTION_COMPLETED"
    PRODUCTION_STARVED = "PRODUCTION_STARVED"
    SHIPMENT_DEPARTED = "SHIPMENT_DEPARTED"
    SHIPMENT_ARRIVED = "SHIPMENT_ARRIVED"
    SHIPMENT_DELAYED = "SHIPMENT_DELAYED"
    INVENTORY_BREACH = "INVENTORY_BREACH"
    DISRUPTION_START = "DISRUPTION_START"
    DISRUPTION_END = "DISRUPTION_END"
    RECOVERY_ACTION = "RECOVERY_ACTION"
    CASCADE_IMPACT = "CASCADE_IMPACT"

class SimulationEvent(BaseModel):
    id: str = Field(default_factory=lambda: f"evt_{uuid.uuid4().hex[:8]}")
    timestamp: float = Field(..., description="Simulation time in days (e.g. 7.25 = Day 7, 06:00)")
    event_type: EventType
    node_id: Optional[str] = None
    edge_id: Optional[str] = None
    product_id: Optional[str] = None
    quantity: float = 0.0
    description: str
    severity: EventSeverity = EventSeverity.INFO
    financial_impact: float = 0.0
    causal_parent_id: Optional[str] = Field(None, description="ID of upstream event that caused this event")
    metadata: Dict[str, Any] = Field(default_factory=dict)
