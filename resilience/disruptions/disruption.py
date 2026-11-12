from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class DisruptionType(str, Enum):
    VEHICLE_BREAKDOWN = "VEHICLE_BREAKDOWN"
    PORT_STRIKE = "PORT_STRIKE"
    SHIPMENT_DELAY = "SHIPMENT_DELAY"
    DEMAND_SURGE = "DEMAND_SURGE"
    SUPPLIER_FAILURE = "SUPPLIER_FAILURE"
    WAREHOUSE_FAILURE = "WAREHOUSE_FAILURE"
    ROUTE_CLOSURE = "ROUTE_CLOSURE"

class Disruption(BaseModel):
    id: str
    name: str
    disruption_type: DisruptionType
    target_id: str = Field(..., description="Node ID or Edge ID impacted")
    start_day: float = Field(..., description="Day when disruption begins")
    duration_days: float = Field(..., description="Duration of shock in days")
    capacity_multiplier: float = Field(
        0.0,
        description="Available capacity during disruption (0.0 = 100% shutdown, 0.3 = 70% capacity lost)"
    )
    delay_multiplier: float = Field(
        1.0,
        description="Transit time multiplier (e.g., 2.5 = 2.5x normal transit time)"
    )
    demand_surge_multiplier: float = Field(
        1.0,
        description="For DEMAND_SURGE: demand multiplier (e.g. 1.8 = +80% surge)"
    )
    description: str = ""
    active: bool = False

    @property
    def end_day(self) -> float:
        return self.start_day + self.duration_days
