# Third-Party Research & Technical Analysis

This document details the architectural and algorithmic inspection of the 11 reference repositories and literature specified in the strategic plan.

## Reference Repositories Analysis

| Reference | License | Core Capabilities | Reusability in CHAINSHIELD | Legal & Architectural Decision |
|---|---|---|---|---|
| **DisruptSC** (`ccolon/disrupt-sc`) | GPLv3 | Multimodal spatial network, capacity shocks, rerouting, Monte Carlo criticality | Study network shock and rerouting logic | **Strict clean-room implementation**: GPL copyleft prevents code reuse without licensing all of CHAINSHIELD under GPL. Concepts reimplemented in Python/SimPy/NetworkX. |
| **Databricks SC Stress Test** | Proprietary Databricks | Scenario generation, LP flow optimization, resilience scoring, Monte Carlo stress testing | Study scenario workflow | **Zero code copy**: Formulate LP natively with Pyomo + HiGHS. Completely independent execution without Databricks/Spark dependency. |
| **Databricks SC Optimization** | Proprietary Databricks | Multi-tier supply allocation, bill-of-materials, capacity constraints, cost minimization | Study mathematical formulation | **Independent formulation**: Formulate pure linear/mixed-integer programming in Pyomo with HiGHS. |
| **InventOpt** | MIT | SimPy discrete-event simulation, inventory buffers, lead times, order batching | SimPy architecture reference | Permissive license. Used as an structural design reference for SimPy actor event loops. |
| **Multi-Echelon Inventory** | GPLv3 | Multi-echelon stockout propagation, (s, S) replenishment policies | Replenishment mechanics | Conceptual study only. Reimplemented independent reorder point policies with stockout and backorder tracking. |
| **AI-Driven Forecast / Resilience Simulator** | Apache/MIT | Interactive UI, scenario sliders, disruption controls, flow animation | UI/UX and What-If interactions | Inspired the interactive What-If scenario controls and causal timeline visualizer in CHAINSHIELD UI. |
| **Supplier Resilience Demo** | Permissive | Supplier allocation diversification (80/20 vs 50/30/20), single-point failure testing | Diversification testing | Built directly into CHAINSHIELD's Network Redesign & Criticality module. |
| **DeepBullwhip** | Permissive / Academic | Arbitrary DAG network representations, demand generator, bullwhip effect metrics | Network representation & metrics | Inspired DAG topological validation and demand surge generation. |
| **Nexus-SCCT** | Reference | Control tower architecture, Next.js/FastAPI, cascade tracking | Cascade trace concept | Reimplemented causal cascade propagation graph engine natively in Python. |

---

## Literature & Scientific Grounding

1. **Simulation-Driven Optimization for Resilient Supply Chains**:
   - *Dimensions*: Robustness, Redundancy, Resourcefulness, Rapidity (the 4 R's of resilience).
   - *Incorporation*: CHAINSHIELD Resilience Score directly calculates service retention (robustness), spare capacity (redundancy), recovery cost/alternatives (resourcefulness), and Time-to-Recover (rapidity).

2. **Cognitive Digital Twins & Disruption Detection**:
   - *Finding*: Digital twin + disruption simulation + recovery optimization exists in literature.
   - *CHAINSHIELD Differentiation*: An interactive *Decision Laboratory* combining discrete-event simulation, causal cascade tracking, constraint-driven multi-objective optimization, and proactive network redesign.

3. **Production-Distribution Resilience (Time-to-Survive / Time-to-Recover)**:
   - *Incorporation*: Time-to-Survive (TTS: time until buffer exhaustion at each node without replenishments) and Time-to-Recover (TTR: time until operational KPI returns to >=95% of baseline) are tracked as first-class metrics.

4. **Cascading Failures in Interdependent Networks**:
   - *Incorporation*: The Cascade Engine maps how a shock at an upstream port or supplier ripples into factory stockouts, warehouse starvation, and final customer delivery delays.
