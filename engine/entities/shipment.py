from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field

class ShipmentStatus(str, Enum):
    SCHEDULED = "SCHEDULED"
    IN_TRANSIT = "IN_TRANSIT"
    DELAYED = "DELAYED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"

class Shipment(BaseModel):
    id: str
    product_id: str
    quantity: float
    origin_id: str
    destination_id: str
    transport_mode: str = "ROAD"
    edge_id: Optional[str] = None
    created_day: float
    departure_day: float
    expected_arrival_day: float
    actual_arrival_day: Optional[float] = None
    status: ShipmentStatus = ShipmentStatus.SCHEDULED
    transport_cost: float = 0.0
    delay_days: float = 0.0
    expedited: bool = False
    rerouted: bool = False
