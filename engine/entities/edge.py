from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field

class TransportMode(str, Enum):
    ROAD = "ROAD"
    RAIL = "RAIL"
    SEA = "SEA"
    AIR = "AIR"

class Edge(BaseModel):
    id: str
    origin_id: str
    destination_id: str
    transport_mode: TransportMode = TransportMode.ROAD
    capacity_per_day: float = Field(..., description="Max daily shipping units")
    distance_km: float
    cost_per_unit_km: float = Field(..., description="INR per unit per km")
    lead_time_days: float = Field(..., description="Normal transit duration in days")
    reliability: float = Field(0.98, ge=0.0, le=1.0)
    active: bool = True
    disruption_multiplier: float = Field(1.0, description="Multiplier on lead time or cost during disruption (1.0 = normal)")
    effective_capacity_multiplier: float = Field(1.0, description="Multiplier on available capacity (1.0 = 100%, 0.0 = blocked)")

    @property
    def effective_lead_time(self) -> float:
        return self.lead_time_days * self.disruption_multiplier

    @property
    def effective_capacity(self) -> float:
        return self.capacity_per_day * self.effective_capacity_multiplier

    @property
    def total_unit_cost(self) -> float:
        return self.distance_km * self.cost_per_unit_km
