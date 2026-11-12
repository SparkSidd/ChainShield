import random
from typing import Dict, List, Tuple
from engine.entities.node import Supplier, Factory, Port, Warehouse, Customer, Location
from engine.entities.edge import Edge, TransportMode
from engine.entities.product import Product, BillOfMaterials
from engine.network.network import SupplyChainNetwork

def create_baseline_network(seed: int = 42) -> SupplyChainNetwork:
    """
    Constructs the canonical 30-day baseline supply chain network for CHAINSHIELD.
    Topology:
      - 8 Suppliers (Tier 1 & Tier 2)
      - 2 Strategic Container Ports (Mumbai JNPT, Chennai Port)
      - 3 Assembly/Manufacturing Factories (Pune, Manesar, Sriperumbudur)
      - 4 Regional Distribution Centers / Warehouses (Bhiwandi, Gurgaon, Bengaluru, Kolkata)
      - 12 Customer / Demand Centres across India
      - 3 Finished Products + 3 Component Raw Materials
    """
    random.seed(seed)
    net = SupplyChainNetwork("India Industrial & Electronics Corridor")

    # 1. Products & BOM
    # Raw Materials
    rm_chip = Product(id="RM_CHIP", name="Microcontroller & SoC", unit_cost=1200.0, selling_price=0.0, stockout_penalty=3000.0)
    rm_metal = Product(id="RM_CHASSIS", name="Precision Aluminum Enclosure", unit_cost=800.0, selling_price=0.0, stockout_penalty=1500.0)
    rm_polymer = Product(id="RM_POLYMER", name="Thermal Polymer Resin", unit_cost=400.0, selling_price=0.0, stockout_penalty=800.0)

    # Finished Goods
    fg_smart = Product(id="FG_SMART_IOT", name="Industrial IoT Gateway", unit_cost=3500.0, selling_price=7500.0, stockout_penalty=5000.0)
    fg_telecom = Product(id="FG_TELECOM_NODE", name="Secure 5G Edge Node", unit_cost=6000.0, selling_price=12000.0, stockout_penalty=9000.0)
    fg_control = Product(id="FG_CONTROLLER", name="Smart Power Controller", unit_cost=4500.0, selling_price=9000.0, stockout_penalty=6500.0)

    # Register Products
    net.add_product(rm_chip)
    net.add_product(rm_metal)
    net.add_product(rm_polymer)

    net.add_product(fg_smart, BillOfMaterials(product_id="FG_SMART_IOT", input_requirements={"RM_CHIP": 1.0, "RM_CHASSIS": 1.0, "RM_POLYMER": 1.0}))
    net.add_product(fg_telecom, BillOfMaterials(product_id="FG_TELECOM_NODE", input_requirements={"RM_CHIP": 2.0, "RM_CHASSIS": 1.0, "RM_POLYMER": 2.0}))
    net.add_product(fg_control, BillOfMaterials(product_id="FG_CONTROLLER", input_requirements={"RM_CHIP": 1.0, "RM_CHASSIS": 2.0, "RM_POLYMER": 1.0}))

    # 2. Suppliers (8 nodes)
    suppliers = [
        Supplier(id="SUP_TAIWAN_SEMICON", name="Pacific Semiconductor Corp", location=Location(city="Kaohsiung/JNPT", state="Import", lat=18.95, lng=72.95),
                 supplied_products=["RM_CHIP"], daily_capacity={"RM_CHIP": 500.0}, unit_costs={"RM_CHIP": 1150.0}, lead_time_days=4.0, reliability=0.96),
        Supplier(id="SUP_SEOUL_MICRO", name="Hanseong Microchips", location=Location(city="Seoul/Chennai", state="Import", lat=13.08, lng=80.29),
                 supplied_products=["RM_CHIP"], daily_capacity={"RM_CHIP": 400.0}, unit_costs={"RM_CHIP": 1250.0}, lead_time_days=3.5, reliability=0.97),
        Supplier(id="SUP_BHILAI_ALLOYS", name="Bhilai Precision Alloys", location=Location(city="Bhilai", state="Chhattisgarh", lat=21.19, lng=81.38),
                 supplied_products=["RM_CHASSIS"], daily_capacity={"RM_CHASSIS": 600.0}, unit_costs={"RM_CHASSIS": 780.0}, lead_time_days=2.0, reliability=0.98),
        Supplier(id="SUP_JAMSHEDPUR_STEEL", name="Tata Advanced Enclosures", location=Location(city="Jamshedpur", state="Jharkhand", lat=22.80, lng=86.20),
                 supplied_products=["RM_CHASSIS"], daily_capacity={"RM_CHASSIS": 500.0}, unit_costs={"RM_CHASSIS": 810.0}, lead_time_days=2.5, reliability=0.99),
        Supplier(id="SUP_GUJARAT_POLYMERS", name="Reliance Poly Resins", location=Location(city="Dahej", state="Gujarat", lat=21.71, lng=72.58),
                 supplied_products=["RM_POLYMER"], daily_capacity={"RM_POLYMER": 800.0}, unit_costs={"RM_POLYMER": 390.0}, lead_time_days=1.5, reliability=0.98),
        Supplier(id="SUP_MUMBAI_POLYTECH", name="Western Polymer Tech", location=Location(city="Thane", state="Maharashtra", lat=19.21, lng=72.97),
                 supplied_products=["RM_POLYMER"], daily_capacity={"RM_POLYMER": 450.0}, unit_costs={"RM_POLYMER": 420.0}, lead_time_days=1.0, reliability=0.97),
        Supplier(id="SUP_BENGALURU_CHIPS", name="India Semiconductor Lab", location=Location(city="Bengaluru", state="Karnataka", lat=12.97, lng=77.59),
                 supplied_products=["RM_CHIP"], daily_capacity={"RM_CHIP": 250.0}, unit_costs={"RM_CHIP": 1300.0}, lead_time_days=1.0, reliability=0.95),
        Supplier(id="SUP_CHENNAI_METALS", name="Madras Castings & Precision", location=Location(city="Chennai", state="Tamil Nadu", lat=13.06, lng=80.24),
                 supplied_products=["RM_CHASSIS"], daily_capacity={"RM_CHASSIS": 350.0}, unit_costs={"RM_CHASSIS": 830.0}, lead_time_days=1.0, reliability=0.97)
    ]
    for s in suppliers:
        net.add_node(s)

    # 3. Ports (2 nodes)
    ports = [
        Port(id="PORT_JNPT", name="JNPT Port Mumbai", location=Location(city="Navi Mumbai", state="Maharashtra", lat=18.949, lng=72.951),
             processing_capacity_per_day=1200.0, handling_cost_per_unit=45.0),
        Port(id="PORT_CHENNAI", name="Chennai Port Marine Hub", location=Location(city="Chennai", state="Tamil Nadu", lat=13.082, lng=80.298),
             processing_capacity_per_day=900.0, handling_cost_per_unit=50.0)
    ]
    for p in ports:
        net.add_node(p)

    # 4. Factories (3 nodes)
    factories = [
        Factory(id="FAC_PUNE", name="Pune Mega Electronics Plant",
                location=Location(city="Pune", state="Maharashtra", lat=18.5204, lng=73.8567),
                production_capacity_per_day={"FG_SMART_IOT": 180.0, "FG_TELECOM_NODE": 100.0, "FG_CONTROLLER": 120.0},
                inventory={"RM_CHIP": 500.0, "RM_CHASSIS": 800.0, "RM_POLYMER": 900.0, "FG_SMART_IOT": 100.0, "FG_TELECOM_NODE": 50.0, "FG_CONTROLLER": 60.0},
                safety_stock={"RM_CHIP": 300.0, "RM_CHASSIS": 300.0, "RM_POLYMER": 300.0},
                reorder_point={"RM_CHIP": 500.0, "RM_CHASSIS": 500.0, "RM_POLYMER": 500.0}),
        Factory(id="FAC_MANESAR", name="Manesar Industrial Assembly",
                location=Location(city="Manesar", state="Haryana", lat=28.3515, lng=76.9427),
                production_capacity_per_day={"FG_SMART_IOT": 150.0, "FG_TELECOM_NODE": 80.0, "FG_CONTROLLER": 140.0},
                inventory={"RM_CHIP": 450.0, "RM_CHASSIS": 700.0, "RM_POLYMER": 750.0, "FG_SMART_IOT": 80.0, "FG_TELECOM_NODE": 40.0, "FG_CONTROLLER": 70.0},
                safety_stock={"RM_CHIP": 250.0, "RM_CHASSIS": 250.0, "RM_POLYMER": 250.0},
                reorder_point={"RM_CHIP": 450.0, "RM_CHASSIS": 450.0, "RM_POLYMER": 450.0}),
        Factory(id="FAC_SRIPERUMBUDUR", name="Sriperumbudur High-Tech Facility",
                location=Location(city="Sriperumbudur", state="Tamil Nadu", lat=12.9737, lng=79.9424),
                production_capacity_per_day={"FG_SMART_IOT": 140.0, "FG_TELECOM_NODE": 90.0, "FG_CONTROLLER": 110.0},
                inventory={"RM_CHIP": 400.0, "RM_CHASSIS": 600.0, "RM_POLYMER": 700.0, "FG_SMART_IOT": 70.0, "FG_TELECOM_NODE": 45.0, "FG_CONTROLLER": 55.0},
                safety_stock={"RM_CHIP": 200.0, "RM_CHASSIS": 200.0, "RM_POLYMER": 200.0},
                reorder_point={"RM_CHIP": 400.0, "RM_CHASSIS": 400.0, "RM_POLYMER": 400.0})
    ]
    for f in factories:
        net.add_node(f)

    # 5. Warehouses / Distribution Centers (4 nodes)
    warehouses = [
        Warehouse(id="WH_MUMBAI", name="Bhiwandi West Logistics Park",
                  location=Location(city="Bhiwandi", state="Maharashtra", lat=19.2813, lng=73.0483),
                  storage_capacity=15000.0,
                  inventory={"FG_SMART_IOT": 550.0, "FG_TELECOM_NODE": 280.0, "FG_CONTROLLER": 380.0},
                  safety_stock={"FG_SMART_IOT": 250.0, "FG_TELECOM_NODE": 120.0, "FG_CONTROLLER": 160.0},
                  reorder_point={"FG_SMART_IOT": 500.0, "FG_TELECOM_NODE": 250.0, "FG_CONTROLLER": 350.0},
                  reorder_quantity={"FG_SMART_IOT": 600.0, "FG_TELECOM_NODE": 300.0, "FG_CONTROLLER": 450.0}),
        Warehouse(id="WH_GURGAON", name="North Capital Hub",
                  location=Location(city="Gurgaon", state="Haryana", lat=28.4595, lng=77.0266),
                  storage_capacity=16000.0,
                  inventory={"FG_SMART_IOT": 600.0, "FG_TELECOM_NODE": 300.0, "FG_CONTROLLER": 420.0},
                  safety_stock={"FG_SMART_IOT": 280.0, "FG_TELECOM_NODE": 140.0, "FG_CONTROLLER": 200.0},
                  reorder_point={"FG_SMART_IOT": 550.0, "FG_TELECOM_NODE": 280.0, "FG_CONTROLLER": 400.0},
                  reorder_quantity={"FG_SMART_IOT": 700.0, "FG_TELECOM_NODE": 350.0, "FG_CONTROLLER": 500.0}),
        Warehouse(id="WH_BENGALURU", name="South Deccan Fulfilment Hub",
                  location=Location(city="Bengaluru", state="Karnataka", lat=12.9716, lng=77.5946),
                  storage_capacity=14000.0,
                  inventory={"FG_SMART_IOT": 500.0, "FG_TELECOM_NODE": 260.0, "FG_CONTROLLER": 340.0},
                  safety_stock={"FG_SMART_IOT": 220.0, "FG_TELECOM_NODE": 110.0, "FG_CONTROLLER": 150.0},
                  reorder_point={"FG_SMART_IOT": 450.0, "FG_TELECOM_NODE": 230.0, "FG_CONTROLLER": 310.0},
                  reorder_quantity={"FG_SMART_IOT": 600.0, "FG_TELECOM_NODE": 300.0, "FG_CONTROLLER": 400.0}),
        Warehouse(id="WH_KOLKATA", name="Eastern Gateway Logistics",
                  location=Location(city="Kolkata", state="West Bengal", lat=22.5726, lng=88.3639),
                  storage_capacity=10000.0,
                  inventory={"FG_SMART_IOT": 400.0, "FG_TELECOM_NODE": 200.0, "FG_CONTROLLER": 250.0},
                  safety_stock={"FG_SMART_IOT": 160.0, "FG_TELECOM_NODE": 80.0, "FG_CONTROLLER": 100.0},
                  reorder_point={"FG_SMART_IOT": 350.0, "FG_TELECOM_NODE": 170.0, "FG_CONTROLLER": 220.0},
                  reorder_quantity={"FG_SMART_IOT": 450.0, "FG_TELECOM_NODE": 220.0, "FG_CONTROLLER": 300.0})
    ]
    for w in warehouses:
        net.add_node(w)

    # 6. Customer Demands (12 nodes)
    customers = [
        Customer(id="CUST_DELHI", name="Delhi NCR Enterprise Fleet", location=Location(city="Delhi", state="Delhi", lat=28.6139, lng=77.2090),
                 demand_profiles={"FG_SMART_IOT": 45.0, "FG_TELECOM_NODE": 25.0, "FG_CONTROLLER": 30.0}, priority=3),
        Customer(id="CUST_MUMBAI", name="Mumbai Financial District Ops", location=Location(city="Mumbai", state="Maharashtra", lat=19.0760, lng=72.8777),
                 demand_profiles={"FG_SMART_IOT": 50.0, "FG_TELECOM_NODE": 28.0, "FG_CONTROLLER": 32.0}, priority=3),
        Customer(id="CUST_BENGALURU", name="Silicon City Data Centers", location=Location(city="Bengaluru", state="Karnataka", lat=12.9716, lng=77.5946),
                 demand_profiles={"FG_SMART_IOT": 40.0, "FG_TELECOM_NODE": 22.0, "FG_CONTROLLER": 25.0}, priority=3),
        Customer(id="CUST_HYDERABAD", name="Cyberabad Telecom Clusters", location=Location(city="Hyderabad", state="Telangana", lat=17.3850, lng=78.4867),
                 demand_profiles={"FG_SMART_IOT": 35.0, "FG_TELECOM_NODE": 18.0, "FG_CONTROLLER": 22.0}, priority=2),
        Customer(id="CUST_CHENNAI", name="Chennai Auto & Heavy IoT", location=Location(city="Chennai", state="Tamil Nadu", lat=13.0827, lng=80.2707),
                 demand_profiles={"FG_SMART_IOT": 30.0, "FG_TELECOM_NODE": 16.0, "FG_CONTROLLER": 20.0}, priority=2),
        Customer(id="CUST_PUNE", name="Pune Tech Park Consortium", location=Location(city="Pune", state="Maharashtra", lat=18.5204, lng=73.8567),
                 demand_profiles={"FG_SMART_IOT": 25.0, "FG_TELECOM_NODE": 14.0, "FG_CONTROLLER": 18.0}, priority=2),
        Customer(id="CUST_AHMEDABAD", name="Gujarat Manufacturing Circle", location=Location(city="Ahmedabad", state="Gujarat", lat=23.0225, lng=72.5714),
                 demand_profiles={"FG_SMART_IOT": 22.0, "FG_TELECOM_NODE": 12.0, "FG_CONTROLLER": 16.0}, priority=2),
        Customer(id="CUST_KOLKATA", name="Kolkata Port Logistics Users", location=Location(city="Kolkata", state="West Bengal", lat=22.5726, lng=88.3639),
                 demand_profiles={"FG_SMART_IOT": 20.0, "FG_TELECOM_NODE": 10.0, "FG_CONTROLLER": 14.0}, priority=2),
        Customer(id="CUST_JAIPUR", name="Rajasthan Smart Grid", location=Location(city="Jaipur", state="Rajasthan", lat=26.9124, lng=75.7873),
                 demand_profiles={"FG_SMART_IOT": 15.0, "FG_TELECOM_NODE": 8.0, "FG_CONTROLLER": 12.0}, priority=1),
        Customer(id="CUST_LUCKNOW", name="UP Infrastructure Projects", location=Location(city="Lucknow", state="Uttar Pradesh", lat=26.8467, lng=80.9462),
                 demand_profiles={"FG_SMART_IOT": 14.0, "FG_TELECOM_NODE": 7.0, "FG_CONTROLLER": 10.0}, priority=1),
        Customer(id="CUST_KOCHI", name="Kerala Coastal Sensors", location=Location(city="Kochi", state="Kerala", lat=9.9312, lng=76.2673),
                 demand_profiles={"FG_SMART_IOT": 12.0, "FG_TELECOM_NODE": 6.0, "FG_CONTROLLER": 8.0}, priority=1),
        Customer(id="CUST_INDORE", name="Central India Logistics Grid", location=Location(city="Indore", state="Madhya Pradesh", lat=22.7196, lng=75.8577),
                 demand_profiles={"FG_SMART_IOT": 12.0, "FG_TELECOM_NODE": 6.0, "FG_CONTROLLER": 8.0}, priority=1)
    ]
    for c in customers:
        net.add_node(c)

    # 7. Connect Topology: Edges
    # Overseas Suppliers -> Ports
    net.add_edge(Edge(id="E_TAIWAN_JNPT", origin_id="SUP_TAIWAN_SEMICON", destination_id="PORT_JNPT", transport_mode=TransportMode.SEA, capacity_per_day=500.0, distance_km=4800.0, cost_per_unit_km=0.10, lead_time_days=4.0))
    net.add_edge(Edge(id="E_SEOUL_CHENNAI", origin_id="SUP_SEOUL_MICRO", destination_id="PORT_CHENNAI", transport_mode=TransportMode.SEA, capacity_per_day=450.0, distance_km=5200.0, cost_per_unit_km=0.10, lead_time_days=3.5))

    # Ports -> Factories
    net.add_edge(Edge(id="E_JNPT_PUNE", origin_id="PORT_JNPT", destination_id="FAC_PUNE", transport_mode=TransportMode.ROAD, capacity_per_day=700.0, distance_km=135.0, cost_per_unit_km=0.75, lead_time_days=1.0))
    net.add_edge(Edge(id="E_JNPT_MANESAR", origin_id="PORT_JNPT", destination_id="FAC_MANESAR", transport_mode=TransportMode.RAIL, capacity_per_day=600.0, distance_km=1400.0, cost_per_unit_km=0.35, lead_time_days=2.5))
    net.add_edge(Edge(id="E_CHENNAI_SRIPERUMBUDUR", origin_id="PORT_CHENNAI", destination_id="FAC_SRIPERUMBUDUR", transport_mode=TransportMode.ROAD, capacity_per_day=650.0, distance_km=45.0, cost_per_unit_km=0.85, lead_time_days=0.5))
    net.add_edge(Edge(id="E_CHENNAI_PUNE", origin_id="PORT_CHENNAI", destination_id="FAC_PUNE", transport_mode=TransportMode.RAIL, capacity_per_day=400.0, distance_km=1150.0, cost_per_unit_km=0.40, lead_time_days=2.5))

    # Domestic Suppliers -> Factories
    # Bhilai Alloys (Chassis) -> Pune, Manesar
    net.add_edge(Edge(id="E_BHILAI_PUNE", origin_id="SUP_BHILAI_ALLOYS", destination_id="FAC_PUNE", transport_mode=TransportMode.RAIL, capacity_per_day=450.0, distance_km=880.0, cost_per_unit_km=0.35, lead_time_days=2.0))
    net.add_edge(Edge(id="E_BHILAI_MANESAR", origin_id="SUP_BHILAI_ALLOYS", destination_id="FAC_MANESAR", transport_mode=TransportMode.RAIL, capacity_per_day=400.0, distance_km=1100.0, cost_per_unit_km=0.35, lead_time_days=2.5))
    # Jamshedpur (Chassis) -> Manesar, Sriperumbudur
    net.add_edge(Edge(id="E_JAMSHEDPUR_MANESAR", origin_id="SUP_JAMSHEDPUR_STEEL", destination_id="FAC_MANESAR", transport_mode=TransportMode.RAIL, capacity_per_day=450.0, distance_km=1250.0, cost_per_unit_km=0.35, lead_time_days=2.5))
    net.add_edge(Edge(id="E_JAMSHEDPUR_SRIPERUMBUDUR", origin_id="SUP_JAMSHEDPUR_STEEL", destination_id="FAC_SRIPERUMBUDUR", transport_mode=TransportMode.RAIL, capacity_per_day=350.0, distance_km=1550.0, cost_per_unit_km=0.35, lead_time_days=3.0))
    # Gujarat Polymers -> Pune, Manesar
    net.add_edge(Edge(id="E_GUJARAT_PUNE", origin_id="SUP_GUJARAT_POLYMERS", destination_id="FAC_PUNE", transport_mode=TransportMode.ROAD, capacity_per_day=550.0, distance_km=430.0, cost_per_unit_km=0.65, lead_time_days=1.5))
    net.add_edge(Edge(id="E_GUJARAT_MANESAR", origin_id="SUP_GUJARAT_POLYMERS", destination_id="FAC_MANESAR", transport_mode=TransportMode.ROAD, capacity_per_day=500.0, distance_km=980.0, cost_per_unit_km=0.60, lead_time_days=2.0))
    # Mumbai Polytech -> Pune
    net.add_edge(Edge(id="E_MUMBAI_PUNE", origin_id="SUP_MUMBAI_POLYTECH", destination_id="FAC_PUNE", transport_mode=TransportMode.ROAD, capacity_per_day=400.0, distance_km=150.0, cost_per_unit_km=0.75, lead_time_days=1.0))
    # Bengaluru Chips -> Sriperumbudur, Pune
    net.add_edge(Edge(id="E_BLR_SRIPERUMBUDUR", origin_id="SUP_BENGALURU_CHIPS", destination_id="FAC_SRIPERUMBUDUR", transport_mode=TransportMode.ROAD, capacity_per_day=250.0, distance_km=300.0, cost_per_unit_km=0.70, lead_time_days=1.0))
    net.add_edge(Edge(id="E_BLR_PUNE", origin_id="SUP_BENGALURU_CHIPS", destination_id="FAC_PUNE", transport_mode=TransportMode.ROAD, capacity_per_day=200.0, distance_km=840.0, cost_per_unit_km=0.65, lead_time_days=2.0))
    # Chennai Metals -> Sriperumbudur
    net.add_edge(Edge(id="E_MAA_SRIPERUMBUDUR", origin_id="SUP_CHENNAI_METALS", destination_id="FAC_SRIPERUMBUDUR", transport_mode=TransportMode.ROAD, capacity_per_day=350.0, distance_km=40.0, cost_per_unit_km=0.85, lead_time_days=0.5))

    # Factories -> Warehouses (Echelon 2)
    net.add_edge(Edge(id="E_FAC_PUNE_WH_MUMBAI", origin_id="FAC_PUNE", destination_id="WH_MUMBAI", transport_mode=TransportMode.ROAD, capacity_per_day=500.0, distance_km=160.0, cost_per_unit_km=0.70, lead_time_days=1.0))
    net.add_edge(Edge(id="E_FAC_PUNE_WH_BLR", origin_id="FAC_PUNE", destination_id="WH_BENGALURU", transport_mode=TransportMode.ROAD, capacity_per_day=400.0, distance_km=840.0, cost_per_unit_km=0.60, lead_time_days=2.0))
    net.add_edge(Edge(id="E_FAC_MANESAR_WH_GURGAON", origin_id="FAC_MANESAR", destination_id="WH_GURGAON", transport_mode=TransportMode.ROAD, capacity_per_day=550.0, distance_km=35.0, cost_per_unit_km=0.85, lead_time_days=0.5))
    net.add_edge(Edge(id="E_FAC_MANESAR_WH_KOLKATA", origin_id="FAC_MANESAR", destination_id="WH_KOLKATA", transport_mode=TransportMode.RAIL, capacity_per_day=350.0, distance_km=1480.0, cost_per_unit_km=0.35, lead_time_days=2.5))
    net.add_edge(Edge(id="E_FAC_SRIP_WH_BLR", origin_id="FAC_SRIPERUMBUDUR", destination_id="WH_BENGALURU", transport_mode=TransportMode.ROAD, capacity_per_day=450.0, distance_km=310.0, cost_per_unit_km=0.65, lead_time_days=1.0))
    net.add_edge(Edge(id="E_FAC_SRIP_WH_KOLKATA", origin_id="FAC_SRIPERUMBUDUR", destination_id="WH_KOLKATA", transport_mode=TransportMode.SEA, capacity_per_day=300.0, distance_km=1650.0, cost_per_unit_km=0.20, lead_time_days=3.0))

    # Warehouses -> Customers (Echelon 3)
    # WH_GURGAON feeds North
    net.add_edge(Edge(id="E_GUR_DELHI", origin_id="WH_GURGAON", destination_id="CUST_DELHI", transport_mode=TransportMode.ROAD, capacity_per_day=450.0, distance_km=40.0, cost_per_unit_km=0.80, lead_time_days=0.5))
    net.add_edge(Edge(id="E_GUR_JAIPUR", origin_id="WH_GURGAON", destination_id="CUST_JAIPUR", transport_mode=TransportMode.ROAD, capacity_per_day=250.0, distance_km=240.0, cost_per_unit_km=0.65, lead_time_days=1.0))
    net.add_edge(Edge(id="E_GUR_LUCKNOW", origin_id="WH_GURGAON", destination_id="CUST_LUCKNOW", transport_mode=TransportMode.ROAD, capacity_per_day=200.0, distance_km=520.0, cost_per_unit_km=0.60, lead_time_days=1.5))
    net.add_edge(Edge(id="E_GUR_INDORE", origin_id="WH_GURGAON", destination_id="CUST_INDORE", transport_mode=TransportMode.ROAD, capacity_per_day=180.0, distance_km=760.0, cost_per_unit_km=0.55, lead_time_days=2.0))

    # WH_MUMBAI feeds West & Central
    net.add_edge(Edge(id="E_MUM_MUMBAI", origin_id="WH_MUMBAI", destination_id="CUST_MUMBAI", transport_mode=TransportMode.ROAD, capacity_per_day=450.0, distance_km=50.0, cost_per_unit_km=0.80, lead_time_days=0.5))
    net.add_edge(Edge(id="E_MUM_PUNE", origin_id="WH_MUMBAI", destination_id="CUST_PUNE", transport_mode=TransportMode.ROAD, capacity_per_day=300.0, distance_km=145.0, cost_per_unit_km=0.70, lead_time_days=0.75))
    net.add_edge(Edge(id="E_MUM_AHMEDABAD", origin_id="WH_MUMBAI", destination_id="CUST_AHMEDABAD", transport_mode=TransportMode.ROAD, capacity_per_day=280.0, distance_km=510.0, cost_per_unit_km=0.60, lead_time_days=1.5))
    net.add_edge(Edge(id="E_MUM_INDORE", origin_id="WH_MUMBAI", destination_id="CUST_INDORE", transport_mode=TransportMode.ROAD, capacity_per_day=200.0, distance_km=570.0, cost_per_unit_km=0.55, lead_time_days=1.5))

    # WH_BENGALURU feeds South
    net.add_edge(Edge(id="E_BLR_BLR", origin_id="WH_BENGALURU", destination_id="CUST_BENGALURU", transport_mode=TransportMode.ROAD, capacity_per_day=400.0, distance_km=30.0, cost_per_unit_km=0.85, lead_time_days=0.5))
    net.add_edge(Edge(id="E_BLR_HYD", origin_id="WH_BENGALURU", destination_id="CUST_HYDERABAD", transport_mode=TransportMode.ROAD, capacity_per_day=320.0, distance_km=570.0, cost_per_unit_km=0.60, lead_time_days=1.5))
    net.add_edge(Edge(id="E_BLR_MAA", origin_id="WH_BENGALURU", destination_id="CUST_CHENNAI", transport_mode=TransportMode.ROAD, capacity_per_day=300.0, distance_km=350.0, cost_per_unit_km=0.65, lead_time_days=1.0))
    net.add_edge(Edge(id="E_BLR_KOCHI", origin_id="WH_BENGALURU", destination_id="CUST_KOCHI", transport_mode=TransportMode.ROAD, capacity_per_day=180.0, distance_km=540.0, cost_per_unit_km=0.60, lead_time_days=1.5))

    # WH_KOLKATA feeds East
    net.add_edge(Edge(id="E_KOL_KOLKATA", origin_id="WH_KOLKATA", destination_id="CUST_KOLKATA", transport_mode=TransportMode.ROAD, capacity_per_day=300.0, distance_km=35.0, cost_per_unit_km=0.80, lead_time_days=0.5))
    net.add_edge(Edge(id="E_KOL_LUCKNOW", origin_id="WH_KOLKATA", destination_id="CUST_LUCKNOW", transport_mode=TransportMode.ROAD, capacity_per_day=180.0, distance_km=980.0, cost_per_unit_km=0.55, lead_time_days=2.0))

    return net
