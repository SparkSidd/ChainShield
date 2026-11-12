from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from resilience.disruptions.disruption import Disruption, DisruptionType
from optimization.mip_solver import RecoveryOptimizationRequest
from engine.whatif.whatif_engine import WhatIfRequest
from engine.redesign.redesign_engine import RedesignConfiguration

class SimulationRunRequest(BaseModel):
    horizon_days: int = 30
    seed: int = 42
    disruptions: List[Disruption] = Field(default_factory=list)
    demand_multiplier: float = 1.0

class SimulationRunResponse(BaseModel):
    simulation_id: str
    horizon_days: int
    seed: int
    metrics: Dict[str, Any]
    event_count: int
    cascade_step_count: int
    cascade: Optional[Dict[str, Any]] = None
    daily_timeseries: List[Dict[str, Any]]

class RecoveryCompareRequest(BaseModel):
    disrupted_target_id: str = "PORT_JNPT"
    unfulfilled_demand_units: float = 600.0
    disrupted_service_level: float = 0.74
    daily_loss_inr: float = 450000.0
    max_budget: float = 1200000.0
    min_service_level: float = 0.90
    max_recovery_days: float = 7.0
    preference: str = "balanced"

class StressTestRunRequest(BaseModel):
    runs: int = Field(100, ge=10, le=1000)
    horizon_days: int = 20
    seed: int = 42
