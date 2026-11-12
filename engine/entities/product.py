from pydantic import BaseModel, Field
from typing import Dict, Optional

class Product(BaseModel):
    id: str
    name: str
    unit_cost: float = Field(..., description="Cost to produce or acquire one unit in INR")
    weight_kg: float = 1.0
    volume_m3: float = 0.01
    holding_cost_per_day: float = Field(0.5, description="Holding cost per unit per day in INR")
    selling_price: float = Field(..., description="Selling price per unit in INR")
    stockout_penalty: float = Field(..., description="Cost per unfulfilled unit in INR")

class BillOfMaterials(BaseModel):
    product_id: str
    input_requirements: Dict[str, float] = Field(
        default_factory=dict,
        description="Mapping of raw_material_id -> quantity needed per unit of finished good"
    )
