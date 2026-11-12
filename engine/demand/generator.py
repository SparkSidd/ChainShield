import math
import random
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class DemandSurge(BaseModel):
    customer_id: Optional[str] = None  # None applies to all customers
    product_id: Optional[str] = None   # None applies to all products
    start_day: float
    duration_days: float
    multiplier: float = 1.5  # 1.5 = +50% surge

class DemandGenerator:
    """
    Synthetic demand generator for supply-chain simulation.
    Generates realistic customer daily orders using:
    Demand(t) = (Base * (1 + Trend * t) * Seasonality(t) + Noise) * Surge(t)
    """
    def __init__(self, seed: int = 42):
        self.seed = seed
        self.rng = random.Random(seed)

    def generate_daily_demand(
        self,
        base_demand: float,
        day: int,
        trend_rate: float = 0.001,
        seasonality_amplitude: float = 0.15,
        noise_std: float = 0.08,
        surge_multiplier: float = 1.0
    ) -> float:
        """
        Calculates demand for a specific customer-product on day t.
        Seasonality is modeled as a 7-day cyclical weekly business pattern.
        """
        # Day of week cycle (peak mid-week, lower on weekend)
        day_of_week = day % 7
        # weekly sine pattern centered around Wednesday (day 3)
        seasonality = 1.0 + seasonality_amplitude * math.sin(2 * math.pi * (day_of_week / 7.0))

        # Trend component
        trend = 1.0 + (trend_rate * day)

        # Noise component (Gaussian)
        noise = self.rng.gauss(0.0, noise_std * base_demand)

        # Base adjusted
        total_demand = (base_demand * trend * seasonality) + noise
        total_demand *= surge_multiplier

        return max(0.0, round(total_demand, 1))

    def generate_schedule(
        self,
        customer_profiles: Dict[str, Dict[str, float]],  # customer_id -> {product_id: base_daily}
        horizon_days: int = 30,
        surges: Optional[List[DemandSurge]] = None
    ) -> Dict[int, Dict[str, Dict[str, float]]]:
        """
        Generates full demand timeline: day -> {customer_id -> {product_id -> quantity}}
        """
        surges = surges or []
        schedule: Dict[int, Dict[str, Dict[str, float]]] = {}

        for day in range(1, horizon_days + 1):
            schedule[day] = {}
            for cust_id, prods in customer_profiles.items():
                schedule[day][cust_id] = {}
                for prod_id, base in prods.items():
                    # Check active surges
                    surge_mult = 1.0
                    for s in surges:
                        if s.start_day <= day < (s.start_day + s.duration_days):
                            if (s.customer_id is None or s.customer_id == cust_id) and \
                               (s.product_id is None or s.product_id == prod_id):
                                surge_mult *= s.multiplier

                    schedule[day][cust_id][prod_id] = self.generate_daily_demand(
                        base_demand=base,
                        day=day,
                        surge_multiplier=surge_mult
                    )
        return schedule
