from typing import Dict, List, Optional, Tuple, Any
import networkx as nx
from engine.entities.node import Node, Supplier, Factory, Port, Warehouse, Customer, NodeType
from engine.entities.edge import Edge, TransportMode
from engine.entities.product import Product, BillOfMaterials

class SupplyChainNetwork:
    """
    Core graph representation of the multi-echelon supply chain.
    Maintains typed node entities and NetworkX DiGraph for topological queries,
    flow routing, betweenness centrality, and cascade tracing.
    """
    def __init__(self, name: str = "ChainShield Supply Network"):
        self.name = name
        self.graph: nx.DiGraph = nx.DiGraph()
        self.nodes: Dict[str, Node] = {}
        self.edges: Dict[str, Edge] = {}
        self.products: Dict[str, Product] = {}
        self.boms: Dict[str, BillOfMaterials] = {}

    def add_product(self, product: Product, bom: Optional[BillOfMaterials] = None):
        self.products[product.id] = product
        if bom:
            self.boms[product.id] = bom

    def add_node(self, node: Node):
        self.nodes[node.id] = node
        self.graph.add_node(
            node.id,
            node_type=node.node_type.value,
            name=node.name,
            lat=node.location.lat,
            lng=node.location.lng,
            city=node.location.city,
            entity=node
        )

    def add_edge(self, edge: Edge):
        if edge.origin_id not in self.nodes or edge.destination_id not in self.nodes:
            raise ValueError(f"Origin {edge.origin_id} or destination {edge.destination_id} not in network")
        self.edges[edge.id] = edge
        self.graph.add_edge(
            edge.origin_id,
            edge.destination_id,
            edge_id=edge.id,
            distance=edge.distance_km,
            lead_time=edge.effective_lead_time,
            capacity=edge.effective_capacity,
            cost_per_unit=edge.total_unit_cost,
            mode=edge.transport_mode.value,
            active=edge.active,
            entity=edge
        )

    def get_node(self, node_id: str) -> Optional[Node]:
        return self.nodes.get(node_id)

    def get_edge(self, edge_id: str) -> Optional[Edge]:
        return self.edges.get(edge_id)

    def get_edge_between(self, origin_id: str, dest_id: str) -> Optional[Edge]:
        for edge in self.edges.values():
            if edge.origin_id == origin_id and edge.destination_id == dest_id and edge.active:
                return edge
        return None

    def get_suppliers(self) -> Dict[str, Supplier]:
        return {k: v for k, v in self.nodes.items() if isinstance(v, Supplier)}

    def get_factories(self) -> Dict[str, Factory]:
        return {k: v for k, v in self.nodes.items() if isinstance(v, Factory)}

    def get_ports(self) -> Dict[str, Port]:
        return {k: v for k, v in self.nodes.items() if isinstance(v, Port)}

    def get_warehouses(self) -> Dict[str, Warehouse]:
        return {k: v for k, v in self.nodes.items() if isinstance(v, Warehouse)}

    def get_customers(self) -> Dict[str, Customer]:
        return {k: v for k, v in self.nodes.items() if isinstance(v, Customer)}

    def get_upstream_nodes(self, node_id: str) -> List[str]:
        """Returns direct suppliers/predecessors."""
        if node_id not in self.graph:
            return []
        return list(self.graph.predecessors(node_id))

    def get_downstream_nodes(self, node_id: str) -> List[str]:
        """Returns direct customers/successors."""
        if node_id not in self.graph:
            return []
        return list(self.graph.successors(node_id))

    def get_all_downstream_descendants(self, node_id: str) -> List[str]:
        """Returns all transitive downstream nodes affected by this node."""
        if node_id not in self.graph:
            return []
        return list(nx.descendants(self.graph, node_id))

    def find_shortest_path(self, origin_id: str, destination_id: str, weight: str = "lead_time") -> Optional[List[str]]:
        try:
            return nx.shortest_path(self.graph, source=origin_id, target=destination_id, weight=weight)
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return None

    def find_all_alternative_paths(self, origin_id: str, destination_id: str, cutoff: int = 4) -> List[List[str]]:
        """Find all feasible simple paths between origin and destination."""
        try:
            return list(nx.all_simple_paths(self.graph, source=origin_id, target=destination_id, cutoff=cutoff))
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return []

    def compute_centrality_metrics(self) -> Dict[str, Dict[str, float]]:
        """Calculates degree, in-degree, out-degree, and betweenness centrality."""
        deg_centrality = nx.degree_centrality(self.graph)
        between_centrality = nx.betweenness_centrality(self.graph, normalized=True)
        in_deg = nx.in_degree_centrality(self.graph)
        out_deg = nx.out_degree_centrality(self.graph)

        metrics = {}
        for node_id in self.nodes:
            metrics[node_id] = {
                "degree_centrality": round(deg_centrality.get(node_id, 0.0), 4),
                "betweenness_centrality": round(between_centrality.get(node_id, 0.0), 4),
                "in_degree": round(in_deg.get(node_id, 0.0), 4),
                "out_degree": round(out_deg.get(node_id, 0.0), 4),
            }
        return metrics

    def to_dict(self) -> Dict[str, Any]:
        """Export network topology to clean JSON-serializable structure for UI."""
        return {
            "name": self.name,
            "node_count": len(self.nodes),
            "edge_count": len(self.edges),
            "nodes": [
                {
                    "id": n.id,
                    "name": n.name,
                    "type": n.node_type.value,
                    "city": n.location.city,
                    "state": n.location.state,
                    "lat": n.location.lat,
                    "lng": n.location.lng,
                    "criticality": n.criticality,
                    "active": n.active
                }
                for n in self.nodes.values()
            ],
            "edges": [
                {
                    "id": e.id,
                    "origin": e.origin_id,
                    "destination": e.destination_id,
                    "mode": e.transport_mode.value,
                    "capacity": e.capacity_per_day,
                    "lead_time_days": e.lead_time_days,
                    "cost_per_unit_km": e.cost_per_unit_km,
                    "distance_km": e.distance_km,
                    "active": e.active,
                    "disrupted": e.effective_capacity_multiplier < 1.0 or e.disruption_multiplier > 1.0
                }
                for e in self.edges.values()
            ],
            "products": [p.model_dump() for p in self.products.values()]
        }
