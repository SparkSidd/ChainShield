import simpy
from typing import Dict, List, Optional, Any, Tuple
import math
from engine.network.network import SupplyChainNetwork
from engine.entities.node import Supplier, Factory, Port, Warehouse, Customer
from engine.entities.edge import Edge
from engine.entities.shipment import Shipment, ShipmentStatus
from engine.simulation.events import SimulationEvent, EventType, EventSeverity
from resilience.disruptions.disruption import Disruption, DisruptionType
from resilience.cascade.tracker import CascadeTracer
from resilience.metrics.calculator import MetricsReport, calculate_metrics

class SupplyChainSimulator:
    """
    Discrete-event supply chain simulator powered by SimPy.
    Simulates inventory dynamics, BOM-constrained production, multimodal transport,
    disruptions, cascade propagation, and recovery strategies.
    """
    def __init__(
        self,
        network: SupplyChainNetwork,
        horizon_days: int = 30,
        seed: int = 42
    ):
        self.network = network
        self.horizon_days = horizon_days
        self.seed = seed

        self.env: simpy.Environment = simpy.Environment()
        self.events: List[SimulationEvent] = []
        self.cascade_tracer: CascadeTracer = CascadeTracer()

        self.disruptions: List[Disruption] = []
        self.active_disruptions: Dict[str, Disruption] = {}

        # Tracking state
        self.demand_records: List[Dict[str, Any]] = []
        self.shipment_records: List[Dict[str, Any]] = []
        self.daily_timeseries: List[Dict[str, Any]] = []
        self.cumulative_holding_cost: float = 0.0

        # Dynamic inventories (copied from network initial values)
        self.node_inventories: Dict[str, Dict[str, float]] = {}
        self._init_node_states()

    def _init_node_states(self):
        for node_id, node in self.network.nodes.items():
            if isinstance(node, Factory) or isinstance(node, Warehouse):
                self.node_inventories[node_id] = dict(node.inventory)
            else:
                self.node_inventories[node_id] = {}

    def log_event(
        self,
        event_type: EventType,
        description: str,
        node_id: Optional[str] = None,
        edge_id: Optional[str] = None,
        product_id: Optional[str] = None,
        quantity: float = 0.0,
        severity: EventSeverity = EventSeverity.INFO,
        financial_impact: float = 0.0,
        causal_parent_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> SimulationEvent:
        evt = SimulationEvent(
            timestamp=round(self.env.now, 2),
            event_type=event_type,
            node_id=node_id,
            edge_id=edge_id,
            product_id=product_id,
            quantity=round(quantity, 1),
            description=description,
            severity=severity,
            financial_impact=round(financial_impact, 2),
            causal_parent_id=causal_parent_id,
            metadata=metadata or {}
        )
        self.events.append(evt)
        return evt

    def add_disruption(self, disruption: Disruption):
        self.disruptions.append(disruption)

    # ----------------- SIMPY PROCESSES -----------------

    def disruption_monitor(self):
        """Monitors scheduled disruptions and alters network state dynamically."""
        while True:
            current_time = self.env.now

            # Check starts
            for d in self.disruptions:
                if not d.active and d.start_day <= current_time < d.end_day:
                    d.active = True
                    self.active_disruptions[d.id] = d
                    self._apply_disruption_effects(d, active=True)

                elif d.active and current_time >= d.end_day:
                    d.active = False
                    if d.id in self.active_disruptions:
                        del self.active_disruptions[d.id]
                    self._apply_disruption_effects(d, active=False)

            yield self.env.timeout(0.25)  # Check every 6 hours

    def _apply_disruption_effects(self, d: Disruption, active: bool):
        target = self.network.get_node(d.target_id)
        edge = self.network.get_edge(d.target_id)

        if active:
            evt = self.log_event(
                event_type=EventType.DISRUPTION_START,
                description=f"Disruption STARTED: {d.name} on {d.target_id}",
                node_id=d.target_id if target else None,
                edge_id=d.target_id if edge else None,
                severity=EventSeverity.CRITICAL,
                metadata={"disruption_type": d.disruption_type.value, "duration": d.duration_days}
            )

            if target and isinstance(target, Port):
                # Reduce port throughput capacity
                target.current_throughput *= d.capacity_multiplier
                target.congestion_delay_days = (1.0 - d.capacity_multiplier) * 4.0
                self.cascade_tracer.record_cascade(
                    timestamp=self.env.now,
                    source=target.id,
                    target=target.id,
                    cause_description=f"Port strike throttled capacity to {int(d.capacity_multiplier*100)}%",
                    effect_type="PORT_CONGESTION",
                    magnitude=(1.0 - d.capacity_multiplier) * 100,
                    downstream_summary="Shipments queuing at port; downstream factories will starve for chips",
                    cause_event_id=evt.id
                )

            elif target and isinstance(target, Supplier):
                # Supplier failure
                target.active = False
                self.cascade_tracer.record_cascade(
                    timestamp=self.env.now,
                    source=target.id,
                    target=target.id,
                    cause_description="Supplier facility offline / breakdown",
                    effect_type="SUPPLIER_OFFLINE",
                    magnitude=100.0,
                    downstream_summary="Component replenishment halted",
                    cause_event_id=evt.id
                )

            elif edge:
                edge.effective_capacity_multiplier = d.capacity_multiplier
                edge.disruption_multiplier = d.delay_multiplier
                self.cascade_tracer.record_cascade(
                    timestamp=self.env.now,
                    source=edge.id,
                    target=edge.destination_id,
                    cause_description=f"Transit link disruption: {d.disruption_type.value}",
                    effect_type="TRANSIT_CHOKE",
                    magnitude=(1.0 - d.capacity_multiplier) * 100,
                    downstream_summary=f"Transit capacity -{int((1-d.capacity_multiplier)*100)}%, lead time x{d.delay_multiplier}",
                    cause_event_id=evt.id
                )

        else:
            # Recovery / End of disruption
            self.log_event(
                event_type=EventType.DISRUPTION_END,
                description=f"Disruption ENDED: {d.name} on {d.target_id}. Normal operations resuming.",
                node_id=d.target_id if target else None,
                edge_id=d.target_id if edge else None,
                severity=EventSeverity.INFO
            )
            if target and isinstance(target, Port):
                target.congestion_delay_days = 0.0
            elif target and isinstance(target, Supplier):
                target.active = True
            elif edge:
                edge.effective_capacity_multiplier = 1.0
                edge.disruption_multiplier = 1.0

    def customer_demand_daily_loop(self, schedule: Dict[int, Dict[str, Dict[str, float]]]):
        """Executes customer demand pull and records fulfillment vs stockouts."""
        for day in range(1, self.horizon_days + 1):
            day_schedule = schedule.get(day, {})
            current_day_demand = 0.0
            current_day_fulfilled = 0.0

            for cust_id, prods in day_schedule.items():
                cust = self.network.get_node(cust_id)
                if not isinstance(cust, Customer):
                    continue

                # Find supplier warehouse (upstream warehouse connected by edge)
                feeding_warehouses = self.network.get_upstream_nodes(cust_id)
                if not feeding_warehouses:
                    continue
                primary_wh_id = feeding_warehouses[0]

                for prod_id, demand_qty in prods.items():
                    if demand_qty <= 0:
                        continue

                    prod = self.network.products[prod_id]
                    wh_stock = self.node_inventories.get(primary_wh_id, {}).get(prod_id, 0.0)

                    fulfilled_qty = min(demand_qty, wh_stock)
                    unfulfilled_qty = demand_qty - fulfilled_qty

                    # Deduct from warehouse
                    self.node_inventories[primary_wh_id][prod_id] = max(0.0, wh_stock - fulfilled_qty)

                    penalty = unfulfilled_qty * prod.stockout_penalty
                    revenue = fulfilled_qty * prod.selling_price

                    current_day_demand += demand_qty
                    current_day_fulfilled += fulfilled_qty

                    self.demand_records.append({
                        "day": day,
                        "customer_id": cust_id,
                        "warehouse_id": primary_wh_id,
                        "product_id": prod_id,
                        "demand": demand_qty,
                        "fulfilled": fulfilled_qty,
                        "unfulfilled": unfulfilled_qty,
                        "on_time": unfulfilled_qty == 0,
                        "penalty": penalty,
                        "revenue": revenue
                    })

                    if unfulfilled_qty > 0:
                        evt = self.log_event(
                            event_type=EventType.ORDER_UNFULFILLED,
                            description=f"Stockout at {primary_wh_id} for {cust.name}: {unfulfilled_qty:.1f} units unfulfilled",
                            node_id=primary_wh_id,
                            product_id=prod_id,
                            quantity=unfulfilled_qty,
                            severity=EventSeverity.WARNING,
                            financial_impact=penalty
                        )
                        # Record cascade propagation to end customer
                        self.cascade_tracer.record_cascade(
                            timestamp=self.env.now,
                            source=primary_wh_id,
                            target=cust_id,
                            cause_description=f"Warehouse stockout on {prod.name}",
                            effect_type="CUSTOMER_SERVICE_DROP",
                            magnitude=(unfulfilled_qty / demand_qty) * 100,
                            downstream_summary=f"Customer order unfulfilled. Penalty ₹{penalty:,.0f}",
                            cause_event_id=evt.id
                        )

            # Daily timeseries snapshot
            day_service = (current_day_fulfilled / current_day_demand) if current_day_demand > 0 else 1.0
            self._record_daily_snapshot(day, day_service)

            # Calculate daily inventory holding cost
            for n_id, invs in self.node_inventories.items():
                for p_id, qty in invs.items():
                    p = self.network.products[p_id]
                    self.cumulative_holding_cost += qty * p.holding_cost_per_day

            yield self.env.timeout(1.0)  # Next day

    def warehouse_replenishment_loop(self):
        """Daily (s, S) replenishment orders from warehouses to feeding factories."""
        while True:
            for wh_id, wh in self.network.get_warehouses().items():
                feeding_factories = self.network.get_upstream_nodes(wh_id)
                if not feeding_factories:
                    continue
                factory_id = feeding_factories[0]
                edge = self.network.get_edge_between(factory_id, wh_id)

                for prod_id, r_point in wh.reorder_point.items():
                    current_inv = self.node_inventories[wh_id].get(prod_id, 0.0)
                    if current_inv <= r_point:
                        order_qty = wh.reorder_quantity.get(prod_id, 300.0)
                        # Trigger shipment process from factory to warehouse
                        self.env.process(self._transit_shipment(
                            origin_id=factory_id,
                            destination_id=wh_id,
                            product_id=prod_id,
                            quantity=order_qty,
                            edge=edge
                        ))
            yield self.env.timeout(1.0)

    def factory_production_loop(self):
        """Simulates factory production constrained by raw material BOM inventory."""
        while True:
            for fac_id, fac in self.network.get_factories().items():
                for fg_id, daily_cap in fac.production_capacity_per_day.items():
                    bom = self.network.boms.get(fg_id)
                    if not bom:
                        continue

                    # Check max buildable from available raw materials
                    max_buildable = daily_cap
                    limiting_rm = None
                    for rm_id, needed_per_unit in bom.input_requirements.items():
                        avail_rm = self.node_inventories[fac_id].get(rm_id, 0.0)
                        buildable = avail_rm / needed_per_unit
                        if buildable < max_buildable:
                            max_buildable = buildable
                            limiting_rm = rm_id

                    # Consume raw materials and produce finished good
                    actual_production = max(0.0, min(daily_cap, max_buildable))

                    for rm_id, needed_per_unit in bom.input_requirements.items():
                        consumed = actual_production * needed_per_unit
                        self.node_inventories[fac_id][rm_id] = max(0.0, self.node_inventories[fac_id].get(rm_id, 0.0) - consumed)

                    # Add finished good inventory
                    self.node_inventories[fac_id][fg_id] = self.node_inventories[fac_id].get(fg_id, 0.0) + actual_production

                    # Cascade alert if factory is starved of raw materials
                    if actual_production < (daily_cap * 0.70):
                        shortfall = daily_cap - actual_production
                        shortfall_pct = (shortfall / daily_cap) * 100
                        evt = self.log_event(
                            event_type=EventType.PRODUCTION_STARVED,
                            description=f"Factory {fac.name} production starved for {limiting_rm}: output reduced by {shortfall_pct:.1f}%",
                            node_id=fac_id,
                            product_id=fg_id,
                            quantity=shortfall,
                            severity=EventSeverity.WARNING
                        )
                        self.cascade_tracer.record_cascade(
                            timestamp=self.env.now,
                            source=limiting_rm or fac_id,
                            target=fac_id,
                            cause_description=f"Raw material {limiting_rm} depleted at factory",
                            effect_type="PRODUCTION_STARVATION",
                            magnitude=shortfall_pct,
                            downstream_summary=f"Assembly line throttled to {actual_production:.0f}/{daily_cap:.0f} units/day",
                            cause_event_id=evt.id
                        )

            yield self.env.timeout(1.0)

    def factory_raw_material_procurement_loop(self):
        """Procures raw materials from upstream ports/suppliers to factories."""
        while True:
            for fac_id, fac in self.network.get_factories().items():
                for rm_id, reorder_pt in fac.reorder_point.items():
                    current_stock = self.node_inventories[fac_id].get(rm_id, 0.0)
                    if current_stock <= reorder_pt:
                        # Find supplier or port supplying this
                        upstream_nodes = self.network.get_upstream_nodes(fac_id)
                        for up_id in upstream_nodes:
                            edge = self.network.get_edge_between(up_id, fac_id)
                            up_node = self.network.get_node(up_id)

                            # If port or supplier supplies this material
                            can_supply = False
                            if isinstance(up_node, Port):
                                can_supply = True
                            elif isinstance(up_node, Supplier) and rm_id in up_node.supplied_products:
                                can_supply = up_node.active

                            if can_supply and edge:
                                order_qty = 500.0
                                self.env.process(self._transit_shipment(
                                    origin_id=up_id,
                                    destination_id=fac_id,
                                    product_id=rm_id,
                                    quantity=order_qty,
                                    edge=edge
                                ))
                                break
            yield self.env.timeout(2.0)

    def _transit_shipment(
        self,
        origin_id: str,
        destination_id: str,
        product_id: str,
        quantity: float,
        edge: Optional[Edge],
        expedited: bool = False
    ):
        """Simulates physical transit of a shipment along an edge with lead times and delay multipliers."""
        if not edge:
            return

        # Transit time calculation
        lead_time = edge.effective_lead_time
        if expedited:
            lead_time = max(0.25, lead_time * 0.40)  # 60% faster

        # Port congestion delay if origin is a port
        origin_node = self.network.get_node(origin_id)
        if isinstance(origin_node, Port):
            lead_time += origin_node.congestion_delay_days

        cost = quantity * edge.total_unit_cost
        expedite_cost = (cost * 1.5) if expedited else 0.0

        departure_day = self.env.now
        expected_arrival = departure_day + edge.lead_time_days

        self.log_event(
            event_type=EventType.SHIPMENT_DEPARTED,
            description=f"Shipment of {quantity:.0f} {product_id} dispatched from {origin_id} -> {destination_id} via {edge.transport_mode.value}",
            edge_id=edge.id,
            product_id=product_id,
            quantity=quantity
        )

        yield self.env.timeout(lead_time)

        actual_arrival = self.env.now
        delay_days = max(0.0, actual_arrival - expected_arrival)

        # Deposit into destination inventory
        if destination_id in self.node_inventories:
            self.node_inventories[destination_id][product_id] = self.node_inventories[destination_id].get(product_id, 0.0) + quantity

        self.shipment_records.append({
            "origin": origin_id,
            "destination": destination_id,
            "product_id": product_id,
            "quantity": quantity,
            "departure": departure_day,
            "expected_arrival": expected_arrival,
            "actual_arrival": actual_arrival,
            "delay_days": delay_days,
            "cost": cost + expedite_cost,
            "expedite_surcharge": expedite_cost,
            "expedited": expedited
        })

        if delay_days > 0.2:
            evt = self.log_event(
                event_type=EventType.SHIPMENT_DELAYED,
                description=f"Shipment {origin_id}->{destination_id} delayed by {delay_days:.1f} days (Arrived Day {actual_arrival:.1f})",
                edge_id=edge.id,
                severity=EventSeverity.WARNING
            )
            self.cascade_tracer.record_cascade(
                timestamp=actual_arrival,
                source=edge.id,
                target=destination_id,
                cause_description=f"Transit delay on {edge.id}",
                effect_type="SHIPMENT_DELAY_ARRIVAL",
                magnitude=delay_days,
                magnitude_unit="days",
                downstream_summary=f"Replenishment delayed by {delay_days:.1f} days",
                cause_event_id=evt.id
            )
        else:
            self.log_event(
                event_type=EventType.SHIPMENT_ARRIVED,
                description=f"Shipment of {quantity:.0f} {product_id} arrived safely at {destination_id}",
                edge_id=edge.id,
                product_id=product_id,
                quantity=quantity
            )

    def _record_daily_snapshot(self, day: int, daily_service_level: float):
        total_inv_units = sum(sum(inv.values()) for inv in self.node_inventories.values())
        self.daily_timeseries.append({
            "day": day,
            "service_level": round(daily_service_level, 4),
            "total_inventory_units": round(total_inv_units, 1),
            "active_disruptions_count": len(self.active_disruptions)
        })

    def run(self, demand_schedule: Dict[int, Dict[str, Dict[str, float]]]) -> Tuple[MetricsReport, Dict[str, Any]]:
        """
        Executes full discrete-event simulation run up to horizon_days.
        Returns final MetricsReport and comprehensive execution telemetry.
        """
        # Register SimPy actor processes
        self.env.process(self.disruption_monitor())
        self.env.process(self.customer_demand_daily_loop(demand_schedule))
        self.env.process(self.warehouse_replenishment_loop())
        self.env.process(self.factory_production_loop())
        self.env.process(self.factory_raw_material_procurement_loop())

        # Execute simulation
        self.env.run(until=self.horizon_days)

        # Compute metrics
        report = calculate_metrics(
            demand_records=self.demand_records,
            shipment_records=self.shipment_records,
            daily_inventory_holding_cost=self.cumulative_holding_cost
        )

        telemetry = {
            "events": [e.model_dump() for e in self.events],
            "cascade": self.cascade_tracer.get_summary(),
            "daily_timeseries": self.daily_timeseries,
            "final_inventories": self.node_inventories
        }

        return report, telemetry
