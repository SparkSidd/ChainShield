import uuid
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

class CascadeLink(BaseModel):
    id: str = Field(default_factory=lambda: f"casc_{uuid.uuid4().hex[:8]}")
    timestamp: float
    source_node_or_edge: str
    target_node: str
    cause_event_id: Optional[str] = None
    cause_description: str
    effect_type: str  # e.g., "BUFFER_DEPLETION", "PRODUCTION_STARVATION", "STOCKOUT", "QUEUE_BACKLOG"
    magnitude: float  # e.g., -35.0 (percentage or units lost)
    magnitude_unit: str = "%"
    downstream_impact_summary: str

class CascadeTracer:
    """
    Traces and explains causal propagation of disruptions across network tiers.
    Builds a causal DAG showing how upstream shocks cascade to end customer service.
    """
    def __init__(self):
        self.links: List[CascadeLink] = []
        self.node_first_impact_time: Dict[str, float] = {}
        self.node_time_to_survive: Dict[str, float] = {}

    def record_cascade(
        self,
        timestamp: float,
        source: str,
        target: str,
        cause_description: str,
        effect_type: str,
        magnitude: float,
        magnitude_unit: str = "%",
        downstream_summary: str = "",
        cause_event_id: Optional[str] = None
    ) -> CascadeLink:
        link = CascadeLink(
            timestamp=round(timestamp, 2),
            source_node_or_edge=source,
            target_node=target,
            cause_event_id=cause_event_id,
            cause_description=cause_description,
            effect_type=effect_type,
            magnitude=round(magnitude, 2),
            magnitude_unit=magnitude_unit,
            downstream_impact_summary=downstream_summary
        )
        self.links.append(link)

        if target not in self.node_first_impact_time:
            self.node_first_impact_time[target] = timestamp

        return link

    def record_time_to_survive(self, node_id: str, tts_days: float):
        self.node_time_to_survive[node_id] = round(tts_days, 2)

    def get_causal_chain(self, node_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Returns ordered sequence of causal propagation."""
        filtered = self.links
        if node_id:
            filtered = [l for l in self.links if l.target_node == node_id or l.source_node_or_edge == node_id]
        return [l.model_dump() for l in filtered]

    def get_summary(self) -> Dict[str, Any]:
        return {
            "total_cascade_steps": len(self.links),
            "impacted_nodes_count": len(self.node_first_impact_time),
            "node_first_impact_time": self.node_first_impact_time,
            "node_time_to_survive": self.node_time_to_survive,
            "chain": [l.model_dump() for l in self.links]
        }
