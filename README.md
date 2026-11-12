# ChainShield: Multi-Layer Supply Chain Resilience & Recovery Digital Twin

<div align="center">

[![Hackathon](https://img.shields.io/badge/M%2326-Problem%20Statement%20%2310-blue.svg?style=for-the-badge&logo=target)](docs/third_party_research.md)
[![Tests](https://img.shields.io/badge/Tests-16%2F16%20PASS%20(100%25)-emerald.svg?style=for-the-badge&logo=checkmarx)](tests/)
[![Optimization](https://img.shields.io/badge/MIP%20Solver-Pyomo%20%2B%20HiGHS-orange.svg?style=for-the-badge&logo=python)](optimization/)
[![Simulation](https://img.shields.io/badge/Simulation-SimPy%20Discrete--Event-cyan.svg?style=for-the-badge&logo=fastapi)](engine/)
[![Frontend](https://img.shields.io/badge/Frontend-React%2019%20%2B%20Tailwind%20v4-violet.svg?style=for-the-badge&logo=react)](frontend/)
[![License](https://img.shields.io/badge/License-MIT-purple.svg?style=for-the-badge)](THIRD_PARTY_NOTICES.md)

**An enterprise-grade, multi-layer supply chain resilience decision laboratory and digital twin.**  
*Discrete-Event Simulation (SimPy) · Mixed-Integer Linear Programming (Pyomo + HiGHS) · Causal Cascade Shock Tracing · Multi-Dimensional Pareto Optimization · Monte Carlo Stress Testing · Counterfactual What-If Sensitivity · Proactive Network Hardening*

[Executive Summary](#-problem-context--executive-summary) • [Canonical Verified Results](#-canonical-verified-results) • [System Architecture](#-system-architecture) • [Mathematical & Algorithmic Foundations](#-mathematical--algorithmic-foundations) • [Network Topology](#-multi-echelon-network-topology) • [Web Control Center](#-interactive-web-control-center) • [REST API Reference](#-rest-api-specification) • [Quick Start](#-quick-start)

</div>

---

## 📌 Problem Context & Executive Summary

Modern industrial supply chains are complex multi-echelon networks governed by tight interdependencies, lean inventories, and just-in-time logistics. When severe disruptions strike—such as maritime container terminal strikes, foreign foundry shutdowns, or regional transport corridor failures—unmitigated shocks propagate non-linearly across tiers. A 10-day capacity shock at an import gateway quickly starves downstream component buffers, throttles assembly lines, drains regional warehouse safety stocks, and ultimately triggers widespread customer stockouts with severe financial penalties.

Conventional Enterprise Resource Planning (ERP) and supply chain management tools rely on static heuristics, spreadsheet estimations, or unconstrained greedy rerouting. These traditional approaches fail to account for:
1. **Dynamic Temporal Cascades**: The propagation delay between an upstream choke point and downstream stockout (Time-to-Survive).
2. **Hard Multi-Tier Constraints**: Supplier capacity limits, multimodal transit transit times, vehicle availability, and warehouse storage ceilings.
3. **Multi-Objective Trade-Offs**: Balancing incremental recovery expenditure against customer On-Time In-Full (OTIF) targets and operational recovery timelines.

**ChainShield** resolves this paradigm by delivering an end-to-end, mathematically rigorous **Supply Chain Resilience & Recovery Decision Laboratory**. ChainShield bridges discrete-event simulation with mathematical optimization, causal graph tracing, and proactive topological redesign:

* **Discrete-Event Digital Twin (SimPy)**: Simulates daily $(s, S)$ inventory policies, Bill-of-Materials (BOM) multi-component assembly constraints, stochastic Poisson/surge demand schedules, and multimodal freight transit across a 29-node pan-India supply network.
* **Causal Cascade Graph Tracer**: Constructs a directed acyclic dependency graph (DAG) tracing how raw shock events at ports or suppliers trigger downstream buffer depletions, production starvation, and delivery delay chains with millisecond precision.
* **Constraint-Driven Recovery Arena**: Evaluates 4 candidate recovery strategies side-by-side, constructing the empirical 3D Pareto frontier across **Incremental Cost**, **Recovery Days**, and **Service Level**.
* **Mathematical MIP Optimization (Pyomo + HiGHS)**: Solves the exact multi-echelon flow reallocation problem as a Mixed-Integer Linear Program (MILP), identifying the mathematically optimal mix of alternate sourcing, express routing, expedited freight, and inventory transfers subject to strict user budget ceilings and service targets.
* **Monte Carlo Stress-Testing Lab**: Executes 100 to 1,000 randomized disruptions across failure types, producing quantitative loss distributions (P50, P90, P95 Value-at-Risk), Time-to-Recover percentiles, and component vulnerability indices.
* **Proactive Network Hardening Engine**: Re-evaluates identical disruption stress tests under structural modifications (e.g., Bharat Silicon Foundry in Hyderabad, Mundra Port maritime hub, Western Dedicated Freight Rail bypass) to verify resilience improvements before capital commitment.

---

## 📊 Canonical Verified Results

All performance metrics and quantitative claims are validated through deterministic test suites and automated benchmark verification scripts (`scripts/verify_truthfulness_and_defense.py` and `scripts/e2e_demo_flow.py`).

### End-to-End Primary Demo Workflow Benchmarks

Execution of the full 8-step primary demo workflow across 30 simulated days on single-core CPU architecture:

| Workflow Step | Simulation & Analytical Task | Key Telemetry / Operational Metrics | Computational Latency |
| :--- | :--- | :--- | :--- |
| **Step 1: Baseline** | 30-Day Healthy Network Nominal Run | Service Level: **100.0%** · Operating Cost: **₹189.3 Lakhs** · Stockout: **0 units** · Resilience Score: **100.0/100** | $0.04\text{ s}$ |
| **Step 2: Port Strike** | 80% Capacity Knockout at JNPT Mumbai (10 days) | Disrupted Service: **100.0%** · Delayed Consignments: **24 shipments** · Financial Risk Exposure: **High** | $0.03\text{ s}$ |
| **Step 3: Cascade Trace** | Causal Shock Propagation Engine | **175 causal transition links** captured (`RM_CHIP` $\to$ `FAC_PUNE`/`FAC_MANESAR` starvation) | $<0.01\text{ s}$ |
| **Step 4: Recovery Arena** | 4-Strategy Pareto & Constraint Audit | Evaluated 4 strategies · **2 Feasible** vs. **2 Rejected** (Air freight: budget breach ₹18.5L > ₹12L; Rail: recovery breach 8.5d > 7d) | $<0.01\text{ s}$ |
| **Step 5: Mathematical MIP** | Pyomo + HiGHS Exact Flow Allocation | Status: **OPTIMAL** · Incremental Cost: **₹1.0 Lakhs** (Budget: ₹12L) · Service Target: **100.0%** achieved in **1.0 days** | **$0.17\text{ s}$** |
| **Step 6: What-If Explorer** | Counterfactual Sensitivity (+30% Demand, 20% Port) | Evaluated counterfactual non-mutating scenario · Operating Cost Delta: **-8.4%** · Customer Service: **100.0%** | $0.08\text{ s}$ |
| **Step 7: Stress Test Lab** | Monte Carlo Stress Testing (100 Scenarios) | Total Runs: **100** · P90 Cost Exposure: **₹140.1 Lakhs** · Mean Service: **100.0%** | **$2.25\text{ s}$** |
| **Step 8: Redesign Hardening** | Structural Redesign Evaluation (50 Disruption Runs) | Criticality Drop: JNPT Mumbai from **0.92 $\to$ 0.58** (**-0.34 shift**) · Structural bypass links verified | **$2.78\text{ s}$** |
| **TOTAL WORKFLOW** | **Full 8-Phase Primary Demonstration** | **All 8 Core Engine Phases Successfully Executed** | **$5.35\text{ s}$** |

### Truthfulness, Determinism & Robustness Audit Matrix

Validated via `python scripts/verify_truthfulness_and_defense.py`:

```text
[1/6] Fixed-Seed Determinism ......... ✓ 100% Identical: Demand=21,683.6 units, Cost=₹18,613,605
[2/6] What-If Immutability ........... ✓ Baseline Unchanged (21,683.6 units) vs What-If (29,274.4 units)
[3/6] Optimizer Hard Constraints ..... ✓ 100% Infeasibility Reasons Explicitly Attributed
[4/6] Stress-Test Reproducibility .... ✓ 15-Run Monte Carlo Deterministic (P90 Cost: ₹7,170,978)
[5/6] Network Redesign Live Sim ...... ✓ Live Re-simulation Across Disruption Matrix Verified
[6/6] Automated Test Suite ........... ✓ 16/16 Tests Passing (100% Pass Rate in 9.96s)
```

---

## 🏛️ System Architecture

ChainShield implements a high-throughput, 4-tier decoupled architecture separating discrete-event state simulation from mathematical solvers, analytical scoring modules, and interactive user interfaces:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                               CHAINSHIELD CORE ARCHITECTURE                            │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ TIER 1: MULTI-ECHELON DISCRETE-EVENT SIMULATION ENGINE (SimPy)                         │
│   • Node Actor Threads (Suppliers, Ports, Factories, Warehouses, Customer Demands)      │
│   • Multimodal Dynamic In-Transit Pipeline (Sea, Rail, Road) with Real Distance/Times  │
│   • Multi-Component Bill-of-Materials (BOM) & Inventory Buffer Depletion Dynamics     │
│   • Configurable Scheduled & Stochastic Disruption Injector                            │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ TIER 2: CAUSAL PROPAGATION & RESILIENCE ANALYTICS ENGINE                               │
│   • Causal Cascade Tracer: Event-Driven Directed Acyclic Graph (DAG)                   │
│   • Buffer Metrics: Time-to-Survive (TTS) & Empirical Time-to-Recover (TTR)            │
│   • Transparent 4-R Resilience Score: Robustness, Rapidity, Resourcefulness, Redundancy│
│   • NetworkX Graph Centrality & Counterfactual Knockout Criticality Scoring            │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ TIER 3: RECOVERY DECISION & MATHEMATICAL OPTIMIZATION ENGINE                           │
│   • Pyomo MILP Formulation Solved via HiGHS Optimizer (appsi_highs)                     │
│   • Recovery Arena: Multi-Dimensional Pareto Frontier Generator (Cost vs Time vs Svc) │
│   • Counterfactual What-If Sensitivity Engine (Zero-Mutation Network Cloning)          │
│   • Proactive Network Redesign Evaluation Engine                                       │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ TIER 4: ENTERPRISE CONTROL CENTER & REST API                                           │
│   • High-Performance Async FastAPI Backend with Pydantic Data Contract Schemas        │
│   • Modern React 19 + TypeScript + Tailwind CSS v4 Interactive Decision Laboratory     │
│   • 9 Specialized Mission-Control Modules with Live Topology Canvas & Dynamic Sliders   │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

### End-to-End Decision Flow

```
                      ┌────────────────────────────────┐
                      │    SCHEDULED DISRUPTIONS       │
                      │  (Port Strike, Supplier Fail)  │
                      └───────────────┬────────────────┘
                                      │
                                      ▼
┌─────────────────────────┐   ┌────────────────────────────────┐   ┌───────────────────────────┐
│  CUSTOMER DEMAND STREAM │──►│     DISCRETE-EVENT ENGINE      │──►│   CAUSAL CASCADE TRACER   │
│  (Stochastic / Surges)  │   │   (SimPy Multi-Echelon Run)    │   │  (175+ Shock Event Links) │
└─────────────────────────┘   └───────────────┬────────────────┘   └─────────────┬─────────────┘
                                              │                                  │
                                              ▼                                  ▼
                              ┌────────────────────────────────┐   ┌───────────────────────────┐
                              │     METRICS & LOSS REPORT      │   │   CRITICALITY RANKINGS    │
                              │  (Service, OTIF, Penalties)    │   │ (Betweenness & Knockout)  │
                              └───────────────┬────────────────┘   └───────────────────────────┘
                                              │
                      ┌───────────────────────┴────────────────────────┐
                      ▼                                                ▼
       ┌──────────────────────────────┐                ┌──────────────────────────────┐
       │        RECOVERY ARENA        │                │     PYOMO + HiGHS SOLVER     │
       │  (4 Candidate Strategies     │                │  (Exact Flow Optimization    │
       │   + 3D Pareto Frontier)      │                │   Subject to User Ceilings)  │
       └──────────────┬───────────────┘                └──────────────┬───────────────┘
                      │                                                │
                      └───────────────────────┬────────────────────────┘
                                              │
                                              ▼
                              ┌────────────────────────────────┐
                              │  PROACTIVE NETWORK REDESIGN    │
                              │ (Topological Hardening Proofs) │
                              └────────────────────────────────┘
```

---

## 🧮 Mathematical & Algorithmic Foundations

ChainShield's core modules are strictly grounded in supply chain operations research, combinatorial optimization, and graph network theory:

### 1. Transparent 4-R Supply Chain Resilience Metric

Rather than relying on opaque black-box heuristics, the **ChainShield Composite Resilience Score** ($S_{\text{resilience}} \in [0, 100]$) implements the 4 R's framework (Robustness, Rapidity, Resourcefulness, Redundancy):

$$S_{\text{resilience}} = 0.30 \cdot S_{\text{robustness}} + 0.25 \cdot S_{\text{rapidity}} + 0.20 \cdot S_{\text{resourcefulness}} + 0.15 \cdot S_{\text{survival}} + 0.10 \cdot S_{\text{redundancy}}$$

Where:
* **Robustness (Service Retention)**:
  $$S_{\text{robustness}} = \min\left(100, \frac{\text{Service Level}_{\text{actual}}}{\text{Service Level}_{\text{baseline}}} \times 100\right)$$
* **Rapidity (Recovery Speed)**: Penalizes recovery duration past day 0:
  $$S_{\text{rapidity}} = \max\left(0, 100 - \text{TTR}_{\text{days}} \times 7.14\right)$$
* **Resourcefulness (Cost Stability)**: Measures containment of unbudgeted penalties and expedite costs relative to total gross revenue:
  $$S_{\text{resourcefulness}} = \max\left(0, 100 - \frac{\text{Penalties} + \text{Expedite Costs}}{\text{Gross Revenue}} \times 100\right)$$
* **Survival (Buffer Endurance)**: Normalized against a 7-day operational survival target:
  $$S_{\text{survival}} = \min\left(100, \frac{\min_{i} \text{TTS}_i}{7.0} \times 100\right)$$
* **Redundancy (Spare Capacity)**:
  $$S_{\text{redundancy}} = \min\left(100, \text{Spare Capacity Ratio} \times 400\right)$$

### 2. Pyomo + HiGHS Mixed-Integer Linear Program (MILP)

When a disruption causes supply shortfalls, the mathematical optimizer solves for the optimal flow allocation vector across all available alternative channels:

#### Sets & Indices
* $P$: Finished goods and component products, indexed by $p$.
* $S_{\text{alt}}$: Certified alternate domestic suppliers, indexed by $s$.
* $E$: Multimodal transport corridors/edges, indexed by $e = (u, v)$.
* $W$: Regional warehouse distribution centers, indexed by $w, w_1, w_2$.

#### Decision Variables
* $x^{\text{alt}}_{s, p} \ge 0$: Volume of product $p$ procured from alternate supplier $s$.
* $x^{\text{route}}_{e, p} \ge 0$: Volume of product $p$ rerouted through corridor $e$.
* $x^{\text{exp}}_{e, p} \ge 0$: Volume of product $p$ expedited via priority air/express cargo on corridor $e$.
* $x^{\text{transfer}}_{w_1, w_2, p} \ge 0$: Volume of product $p$ transferred from warehouse $w_1$ to warehouse $w_2$.
* $y^{\text{short}}_{p} \ge 0$: Unfulfilled demand shortfall for product $p$.
* $u_m \in \{0, 1\}$: Binary indicators denoting activation of recovery transport modes.

#### Objective Function
Minimizes total incremental recovery cost plus heavy penalty on unfulfilled customer demand:

$$\min \quad \sum_{s \in S_{\text{alt}}} \sum_{p} c_{s,p}^{\text{alt}} x^{\text{alt}}_{s, p} + \sum_{e \in E} \sum_{p} \left(c_{e}^{\text{route}} x^{\text{route}}_{e, p} + c_{e}^{\text{exp}} x^{\text{exp}}_{e, p}\right) + \sum_{w_1 \ne w_2} \sum_{p} c_{w_1, w_2}^{\text{xfer}} x^{\text{transfer}}_{w_1, w_2, p} + \sum_{p} \rho_{p}^{\text{stockout}} y^{\text{short}}_{p}$$

#### Subject to Operational Constraints
1. **Flow Conservation & Demand Satisfaction**:
   $$\sum_{s} x^{\text{alt}}_{s, p} + \sum_{e \in \text{In}(w)} \left(x^{\text{route}}_{e, p} + x^{\text{exp}}_{e, p}\right) + \sum_{w'} x^{\text{transfer}}_{w', w, p} + y^{\text{short}}_{p} \ge \text{Shortfall}_{p}, \quad \forall p \in P$$
2. **Alternate Supplier Capacity**:
   $$x^{\text{alt}}_{s, p} \le \text{Capacity}_{s, p}^{\text{alt}}, \quad \forall s \in S_{\text{alt}}, \forall p \in P$$
3. **Route & Corridor Capacity**:
   $$\sum_{p} \left(x^{\text{route}}_{e, p} + x^{\text{exp}}_{e, p}\right) \le \text{Capacity}_{e}, \quad \forall e \in E$$
4. **Inter-Warehouse Inventory Limits**:
   $$\sum_{w_2} x^{\text{transfer}}_{w_1, w_2, p} \le \max\left(0, \text{Inventory}_{w_1, p} - \text{SafetyStock}_{w_1, p}\right), \quad \forall w_1 \in W, \forall p \in P$$
5. **Strict Budget Ceiling**:
   $$\text{Total Incremental Cost} \le \text{Budget}_{\max}$$
6. **Minimum Target Service Level**:
   $$1.0 - \frac{\sum_{p} y^{\text{short}}_{p}}{\sum_{p} \text{Demand}_{p}} \ge \text{ServiceLevel}_{\min}$$
7. **Maximum Allowable Recovery Timeline**:
   $$\max_{m \in \text{Active}} \text{LeadTime}_{m} \le \text{RecoveryDays}_{\max}$$

### 3. Causal Cascade & Dynamic Shock Propagation

Upstream shocks propagate through continuous lead-time delays:
* **Time-to-Survive (TTS)**: The number of operating days an assembly node or warehouse can sustain baseline production/fulfillment before exhausting buffer inventory:
  $$\text{TTS}_{i} = \min_{p \in \text{BOM}(i)} \left\{ \frac{\text{Inventory}_{i, p}}{\text{Daily Consumption Rate}_{i, p}} \right\}$$
* **Time-to-Recover (TTR)**: The elapsed duration between shock inception $t_{\text{disrupt}}$ and the restoration of normal customer service level $\ge 95\%$:
  $$\text{TTR} = \inf \{ t > t_{\text{disrupt}} \mid \text{ServiceLevel}(t) \ge 0.95 \times \text{ServiceLevel}_{\text{baseline}} \} - t_{\text{disrupt}}$$

### 4. Graph Centrality & Criticality Scoring

Every node $v \in V$ in the supply network is evaluated across topological graph properties and counterfactual shock simulations:
* **Betweenness Centrality**:
  $$C_B(v) = \sum_{s \ne v \ne t \in V} \frac{\sigma_{st}(v)}{\sigma_{st}}$$
  Where $\sigma_{st}$ is the total number of shortest supply paths from source $s$ to sink $t$, and $\sigma_{st}(v)$ is the number of those paths passing through node $v$.
* **Composite Criticality Index**:
  $$\text{Criticality}(v) = 0.50 \cdot \left(\frac{\text{Dependent Demand}(v)}{\text{Total Network Demand}}\right) + 0.30 \cdot \left(\frac{\text{Simulated Impact}(v)}{\text{Max Shock Impact}}\right) + 0.20 \cdot C_B(v)$$

---

## 🗺️ Multi-Echelon Network Topology

ChainShield models a realistic, 29-node pan-India high-tech electronics manufacturing corridor with 6 distinct product SKUs and 25+ multimodal transport routes:

```
[ kaohsiung / seoul ]   [ bhilai / jamshedpur / dahej / thane / blr / maa ]
    (Overseas)                            (Domestic Tier-1 & Tier-2)
         │                                            │
         ▼ (Maritime Sea Routes)                      ▼ (Express Rail & National Highway)
┌──────────────────┐                         ┌───────────────────────────────────────┐
│ STRATEGIC PORTS  │                         │          DOMESTIC SUPPLIERS           │
│ • JNPT Mumbai    │                         │ • Bhilai Precision Alloys (Chassis)   │
│ • Chennai Marine │                         │ • Reliance Poly Resins (Polymer)      │
└────────┬─────────┘                         │ • India Semiconductor Lab (Microchips)│
         │                                   └──────────────────┬────────────────────┘
         └───────────────────┬──────────────────────────────────┘
                             ▼
              ┌───────────────────────────────┐
              │     ASSEMBLY FACTORIES        │
              │ • Pune Mega Electronics Plant │
              │ • Manesar Industrial Assembly │
              │ • Sriperumbudur High-Tech Hub │
              └──────────────┬────────────────┘
                             │
                             ▼ (Direct Freight Rail / Dedicated Corridors)
              ┌───────────────────────────────┐
              │    REGIONAL WAREHOUSES / DC   │
              │ • Bhiwandi West (Mumbai Hub)  │
              │ • North Capital Hub (Gurgaon) │
              │ • South Deccan (Bengaluru)    │
              │ • Eastern Gateway (Kolkata)   │
              └──────────────┬────────────────┘
                             │
                             ▼ (Last-Mile Regional Distribution)
              ┌───────────────────────────────┐
              │     12 DEMAND CONSUMERS       │
              │ Delhi NCR, Mumbai, Bengaluru, │
              │ Hyderabad, Chennai, Pune,     │
              │ Ahmedabad, Kolkata, Jaipur,   │
              │ Lucknow, Kochi, Indore        │
              └───────────────────────────────┘
```

### Complete Network Inventory

| Echelon Tier | Node Count | Sample Entities & Locations | Key Capabilities / Capacity Limits |
| :--- | :---: | :--- | :--- |
| **Tier 1: Suppliers** | 8 | Kaohsiung, Seoul, Bhilai, Jamshedpur, Dahej, Thane, Bengaluru, Chennai | Microcontrollers (500 units/d), Precision Enclosures (600 units/d), Thermal Polymer Resins (800 units/d) |
| **Tier 2: Maritime Ports** | 2 | JNPT Mumbai, Chennai Marine Terminal | JNPT: 1,200 units/d container handling; Chennai: 900 units/d container handling |
| **Tier 3: Manufacturing** | 3 | Pune (MH), Manesar (HR), Sriperumbudur (TN) | 3-line BOM assembly: Industrial IoT Gateways, Secure 5G Edge Nodes, Smart Power Controllers |
| **Tier 4: Regional Warehouses**| 4 | Bhiwandi (West), Gurgaon (North), Bengaluru (South), Kolkata (East) | 10,000 to 16,000 unit automated pallet storage capacity; $(s, S)$ continuous replenishment |
| **Tier 5: Customer Hubs** | 12 | Delhi NCR, Mumbai, Bengaluru, Hyderabad, Chennai, Pune, Ahmedabad, Kolkata, Jaipur, Lucknow, Kochi, Indore | Enterprise fleets, telecommunications infrastructure, smart power grids (Poisson daily demand) |
| **Multimodal Logistics** | 25+ | Dedicated Rail Corridors, National Highways, Maritime Sea Lanes | Real-world distances (40 km to 5,200 km), modal unit costs (₹0.10/km sea to ₹0.85/km road) |

---

## 🎮 Interactive Web Control Center

ChainShield provides a responsive, dark-mode **Mission-Control Web Application** built with React 19, TypeScript, Vite, and Tailwind CSS v4, organized into 9 specialized command screens:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ CHAINSHIELD CONTROL CENTER                                           [RESET] [PORT STRIKE]│
├────────────────────────────────────────────────────────────────────────────────────────┤
│ [Control Center] [Network] [Disruption Lab] [Cascade Trace] [Recovery Arena] ...       │
├────────────────────────────────────────────────────────────────────────────────────────┤
│  SERVICE LEVEL      ON-TIME IN-FULL       OPERATING COST      RESILIENCE SCORE         │
│     100.0%              100.0%             ₹189.3 Lakhs          100.0 / 100           │
├────────────────────────────────────────────────────────────────────────────────────────┤
│  INTERACTIVE DIGITAL TWIN TOPOLOGY               CRITICALITY HEATMAP                   │
│   • 29 interactive node pins with live status     • JNPT Port Mumbai (0.92 Index)      │
│   • Flow volume indicators along routes           • Taiwan Semicon Corp (0.84 Index)   │
│   • Pulsing red alerts during active choke        • Pune Assembly Hub (0.76 Index)     │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

1. **Executive Control Center (`/control-center`)**: High-level KPI summary cards (Service Level, Fill Rate, OTIF Rate, Operating Costs, Resilience Score) with live disruption status badge and primary demo action buttons.
2. **Interactive Network View (`/network`)**: Interactive 2D spatial canvas displaying all 29 facilities and multimodal corridors across India with coordinate-accurate positioning, capacity statistics, and active disruption pulses.
3. **Disruption Injection Lab (`/disruption-lab`)**: Inject and simulate tailored shocks (Port Strikes, Supplier Failures, Vehicle Breakdowns, Shipment Delays) with granular control over start day, duration, and capacity choking factors.
4. **Causal Cascade Trace (`/cascade-trace`)**: Visual audit graph documenting every causal propagation event step-by-step from raw shock initiation to final customer fulfillment impact.
5. **Recovery Arena (`/recovery-arena`)**: Side-by-side trade-off matrix comparing 4 candidate recovery strategies against user-defined budget and service constraints, plotting the true 3D Pareto frontier.
6. **Mathematical MIP Solver (`/recovery-arena`)**: Interactive interface triggering the Pyomo + HiGHS optimization engine to produce exact action decision vectors with transparent mathematical rationales.
7. **Monte Carlo Stress Test Lab (`/stress-test`)**: Monte Carlo simulation workbench running 100 to 1,000 randomized disruptions, generating empirical cost distributions, P90/P95 loss exposures, and vulnerability rankings.
8. **What-If Sensitivity Explorer (`/what-if`)**: Zero-mutation parameter sensitivity simulator allowing operators to tweak demand multipliers, port capacities, and transport rates to inspect radar differential charts against baseline.
9. **Network Redesign Studio (`/redesign`)**: Architectural hardening testing suite evaluating topological augmentations (Hyderabad foundry, Mundra Port, rail bypasses) to prove long-term resilience gains.

---

## 🔌 REST API Specification

ChainShield exposes a high-performance, asynchronous REST API powered by FastAPI and validated through Pydantic v2 data models:

| Method | Endpoint | Request Payload / Params | Response Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | None | Service heartbeat, version (`1.0.0`), and engine health status |
| `GET` | `/network` | None | Complete 29-node topology, multimodal edges, products, BOMs, and spatial coordinates |
| `POST` | `/simulation/run` | `SimulationRunRequest` (`horizon_days`, `seed`, `disruptions`, `demand_mult`) | Executes SimPy discrete-event simulation; returns run ID, KPIs, event logs, and cascade graph |
| `GET` | `/simulation/{sim_id}` | Path: `sim_id` | Retrieves complete telemetry, timeseries, and metrics for a specific simulation run |
| `GET` | `/simulation/{sim_id}/metrics` | Path: `sim_id` | Returns customer, operational, financial, and 4-R resilience metrics for a run |
| `GET` | `/simulation/{sim_id}/events` | Path: `sim_id` | Full chronological simulation event stream with timestamps, severities, and impacts |
| `GET` | `/simulation/{sim_id}/cascade` | Path: `sim_id` | Causal cascade chain, Time-to-Survive (TTS), and impacted facility audit records |
| `POST` | `/recovery/compare` | `RecoveryCompareRequest` (`disrupted_target`, `budget`, `min_service`, `max_days`) | Evaluates 4 candidate strategies, computes Pareto frontier, and attributes infeasibility reasons |
| `POST` | `/recovery/optimize` | `RecoveryOptimizationRequest` (`max_budget`, `min_service`, `preference`) | Solves exact MILP flow optimization via Pyomo + HiGHS; returns action decisions |
| `POST` | `/what-if` | `WhatIfRequest` (`demand_multiplier`, `port_capacity_multiplier`, etc.) | Counterfactual sensitivity execution without mutating baseline network state |
| `POST` | `/stress-test` | `StressTestRunRequest` (`runs`: 10–1000, `horizon_days`, `seed`) | Monte Carlo stress testing suite producing P50/P90/P95 loss and recovery distributions |
| `GET` | `/criticality` | None | Ranked criticality indices for suppliers, factories, ports, warehouses, and failure modes |
| `POST` | `/redesign` | `RedesignConfiguration` (booleans for backup supplier, bypass, alternate port) | Simulates and compares before-and-after resilience metrics across structural redesigns |

### Sample API Request: MIP Recovery Optimization

```bash
curl -X POST "http://localhost:8000/recovery/optimize" \
  -H "Content-Type: application/json" \
  -d '{
    "max_budget": 1200000.0,
    "min_service_level": 0.90,
    "max_recovery_days": 7.0,
    "preference": "balanced"
  }'
```

#### Sample JSON Response
```json
{
  "status": "OPTIMAL",
  "solver_name": "HiGHS",
  "objective_value": 97500.0,
  "incremental_cost": 97500.0,
  "achieved_service_level": 1.0,
  "recovery_time_days": 1.0,
  "actions": [
    {
      "action_type": "ALT_SUPPLIER",
      "source_id": "SUP_BENGALURU_CHIPS",
      "target_id": "FAC_PUNE",
      "product_id": "FG_SMART_IOT",
      "quantity": 150.0,
      "unit_cost": 3800.0,
      "total_cost": 570000.0,
      "lead_time_days": 1.5,
      "description": "Procure 150.0 units of FG_SMART_IOT from alternate supplier SUP_BENGALURU_CHIPS"
    }
  ],
  "decision_rationale": "HiGHS solver identified optimal mathematical plan. Allocated 2 recovery actions achieving 100.0% service level within 1.0 days at ₹97,500 (budget utilization: 8.1%)."
}
```

---

## 🛠️ Technology Stack Matrix

| Architectural Layer | Technology / Library | Version | Engineering Role & Purpose |
| :--- | :--- | :--- | :--- |
| **Simulation Core** | **SimPy** | $\ge 4.1.0$ | Asynchronous discrete-event engine modeling inventory loops, transit queues, and event streams |
| **Optimization Modeling**| **Pyomo** | $\ge 6.7.0$ | Declarative mathematical programming framework for linear and mixed-integer recovery formulations |
| **MIP / LP Solver** | **HiGHS (`highspy`)** | $\ge 1.7.0$ | State-of-the-art open-source linear/MIP solver (`appsi_highs`) for global optimum discovery |
| **Graph Analytics** | **NetworkX** | $\ge 3.2.0$ | Network topology graph construction, shortest path computation, and betweenness centrality analysis |
| **Numerical Computing** | **NumPy & SciPy** | $\ge 2.0.0$ / $\ge 1.13.0$ | Statistical distributions, Monte Carlo random variations, and matrix calculations |
| **Data Layer** | **Pandas** | $\ge 2.2.0$ | Daily simulation timeseries recording, KPI dataframes, and analytical aggregations |
| **Domain Validation** | **Pydantic** | $\ge 2.7.0$ | Strict data schema validation, type safety, and serialization for requests and responses |
| **Backend API Engine** | **FastAPI & Uvicorn** | $\ge 0.111.0$ / $\ge 0.30.0$ | Asynchronous RESTful service framework with automated OpenAPI interactive documentation |
| **Frontend Framework** | **React 19 & TypeScript**| `^19.3.0` / `~6.0.2` | Enterprise user interface, component-based control state, and strict frontend type safety |
| **Styling & Icons** | **Tailwind CSS v4 & Lucide**| `^4.3.3` / `^1.46.0` | High-performance styling engine and rich industrial iconography |
| **Build & Tooling** | **Vite** | `^8.3.0` | Ultra-fast frontend bundler, HMR server, and production static site optimizer |
| **Testing & CI** | **pytest** | $\ge 8.0.0$ | Comprehensive test runner for unit tests, solver integration, and determinism verification |

---

## 🚀 Quick Start

### Prerequisites
* **Python**: `3.10` or higher (tested on Python 3.11, 3.12, 3.13)
* **Node.js**: `18.x` or higher and `npm`
* **Git**: Installed and configured

### 1. Repository Setup

```bash
# Clone the repository
git clone https://github.com/SparkSidd/ChainShield.git
cd ChainShield

# Create and activate Python virtual environment
python -m venv venv

# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# On Linux / macOS:
# source venv/bin/activate

# Install core backend dependencies
pip install -r requirements.txt
```

### 2. Verify Mathematical Solvers & Run Test Suite

Run the full automated test suite to verify the SimPy environment, Pyomo models, and HiGHS solver bindings:

```bash
# Execute pytest suite (16 test cases)
python -m pytest -v
```

Expected output:
```text
tests/test_api.py .....                                      [ 31%]
tests/test_mip_optimizer.py ..                               [ 43%]
tests/test_recovery_arena.py .                               [ 50%]
tests/test_resilience_services.py ....                       [ 75%]
tests/test_simulation_and_resilience.py ....                 [100%]
======================= 16 passed in 9.96s ========================
```

### 3. Run Truthfulness & Defense Verification

Run the formal determinism and counterfactual verification audit:

```bash
python scripts/verify_truthfulness_and_defense.py
```

### 4. Run Full End-to-End Primary Demo Workflow

Execute the comprehensive 8-step primary demonstration script:

```bash
python scripts/e2e_demo_flow.py
```

### 5. Launch the Full-Stack Application

Launch the FastAPI backend server and Vite frontend simultaneously:

#### Terminal 1: Backend API
```bash
# From repository root (with venv active)
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```
*API documentation available at [http://localhost:8000/docs](http://localhost:8000/docs)*

#### Terminal 2: Frontend Control Center
```bash
cd frontend
npm install
npm run dev
```
*Web Control Center available at [http://localhost:5173](http://localhost:5173)*

---

## 🧪 Comprehensive Test Manifest

| Test Module | Test Function | Subsystem Verified | Assertions & Invariants Checked | Status |
| :--- | :--- | :--- | :--- | :---: |
| `test_api.py` | `test_api_health` | FastAPI Root | Health status response and API version validation | **PASS** |
| `test_api.py` | `test_api_network` | Network Topology API | Verifies 29 facilities, node coordinates, and 25+ multimodal edges | **PASS** |
| `test_api.py` | `test_api_simulation_run_and_cascade`| Discrete-Event Engine | Validates 15-day simulation execution and cascade chain endpoint | **PASS** |
| `test_api.py` | `test_api_recovery_compare_and_optimize`| Decision Services | Evaluates multi-strategy comparison and HiGHS solver execution | **PASS** |
| `test_api.py` | `test_api_whatif_and_redesign` | Advanced Analytics | Tests What-If sensitivity diff and network redesign metrics | **PASS** |
| `test_mip_optimizer.py` | `test_pyomo_highs_optimal_solve` | Mathematical MIP | Pyomo ConcreteModel formulation solved via HiGHS to global optimum | **PASS** |
| `test_mip_optimizer.py` | `test_pyomo_highs_infeasible_constraints` | Constraint Solver | Validates infeasibility detection when budget ceiling is exceeded | **PASS** |
| `test_recovery_arena.py`| `test_recovery_arena_comparison` | Strategy Comparison | Computes 4 candidate strategies, Pareto frontier, and constraint rejection | **PASS** |
| `test_resilience_services.py` | `test_stress_test_engine` | Monte Carlo Engine | 10 randomized disruption runs, statistical loss buckets, and mean KPIs | **PASS** |
| `test_resilience_services.py` | `test_criticality_engine_rankings` | Criticality Module | Verifies JNPT highest port score and targeted vs random failure delta | **PASS** |
| `test_resilience_services.py` | `test_whatif_engine_immutability_and_diff`| Sensitivity Engine | Validates zero-mutation network immutability and metric deltas | **PASS** |
| `test_resilience_services.py` | `test_network_redesign_resilience_gain` | Topological Redesign | Re-simulates 10 disruption runs under hardened redesign architecture | **PASS** |
| `test_simulation_and_resilience.py` | `test_baseline_network_topology` | Network Integrity | Verifies 29 nodes, 6 products, BOM connectivity, and shortest path | **PASS** |
| `test_simulation_and_resilience.py` | `test_baseline_30_day_simulation_healthy`| SimPy Engine | 30-day baseline simulation: $\ge 90\%$ service level, zero false stockouts | **PASS** |
| `test_simulation_and_resilience.py` | `test_port_strike_disruption_and_cascade_trace`| Causal Shock Engine | Injects JNPT dockworkers strike; verifies 100+ cascade transition links | **PASS** |
| `test_simulation_and_resilience.py` | `test_constraint_driven_recovery_optimizer` | Constraint Engine | Validates optimal vs infeasible recommendations under budget bounds | **PASS** |

---

## 🔬 Research Provenance & Clean-Room Development

ChainShield was engineered from the ground up as an independent research project and decision laboratory. To uphold scientific integrity and intellectual property standards:

* **Strict Clean-Room Derivation**: No source code was copied or imported from GPL or proprietary repositories (e.g., `DisruptSC`, Databricks Industry Solutions). All discrete-event actors, $(s, S)$ replenishment policies, and multimodal pipeline dynamics were authored from mathematical principles using SimPy and NetworkX.
* **Open Mathematical Formulation**: Mixed-integer programming models were derived independently and formulated natively in open-source Pyomo using the high-performance HiGHS solver, removing all proprietary cloud dependencies.
* **Documentation & Attribution**: Detailed comparative literature surveys and legal notices are cataloged in [`docs/third_party_research.md`](docs/third_party_research.md) and [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).

---

## 📄 License

This project is licensed under the **MIT License** — see the [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) file for comprehensive third-party attribution and library licensing details.

---

<div align="center">
<b>ChainShield</b> — Engineering Next-Generation Autonomous Resilience for Global Supply Networks.  
Developed by <b>Siddharth (SparkSidd)</b>.
</div>
