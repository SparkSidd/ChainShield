from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class NodeType(str, Enum):
    SUPPLIER = "SUPPLIER"
    FACTORY = "FACTORY"
    PORT = "PORT"
    WAREHOUSE = "WAREHOUSE"
    CUSTOMER = "CUSTOMER"

class Location(BaseModel):
    city: str
    state: str
    country: str = "India"
    lat: float
    lng: float

class Node(BaseModel):
    id: str
    name: str
    node_type: NodeType
    location: Location
    active: bool = True
    criticality: float = 0.0
    current_load: float = 0.0

class Supplier(Node):
    node_type: NodeType = NodeType.SUPPLIER
    supplied_products: List[str] = Field(default_factory=list, description="Product IDs supplied")
    daily_capacity: Dict[str, float] = Field(default_factory=dict, description="Daily capacity per product")
    unit_costs: Dict[str, float] = Field(default_factory=dict, description="Unit cost per product")
    lead_time_days: float = 2.0
    reliability: float = Field(0.98, ge=0.0, le=1.0, description="Probability of on-time complete shipment")

class Factory(Node):
    node_type: NodeType = NodeType.FACTORY
    production_capacity_per_day: Dict[str, float] = Field(default_factory=dict, description="Daily production capacity per finished good")
    inventory: Dict[str, float] = Field(default_factory=dict, description="Raw materials and finished goods inventory")
    safety_stock: Dict[str, float] = Field(default_factory=dict)
    reorder_point: Dict[str, float] = Field(default_factory=dict)
    processing_time_days: float = 1.0
    utilization: float = 0.0

class Port(Node):
    node_type: NodeType = NodeType.PORT
    processing_capacity_per_day: float = Field(..., description="Max containers/units processed per day")
    current_throughput: float = 0.0
    congestion_delay_days: float = 0.0
    handling_cost_per_unit: float = 50.0

class Warehouse(Node):
    node_type: NodeType = NodeType.WAREHOUSE
    storage_capacity: float = Field(..., description="Max total units storage capacity")
    inventory: Dict[str, float] = Field(default_factory=dict)
    safety_stock: Dict[str, float] = Field(default_factory=dict)
    reorder_point: Dict[str, float] = Field(default_factory=dict)
    reorder_quantity: Dict[str, float] = Field(default_factory=dict)
    holding_cost_per_day: float = 1.0

class Customer(Node):
    node_type: NodeType = NodeType.CUSTOMER
    demand_profiles: Dict[str, float] = Field(default_factory=dict, description="Average daily demand per finished product")
    priority: int = Field(1, description="1 (Normal) to 3 (Strategic/Critical)")
    service_requirement: float = Field(0.95, description="Target service level / fill rate")
