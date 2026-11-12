# Third-Party Notices & Licenses

CHAINSHIELD is an independent supply chain resilience decision laboratory built from scratch for Manipal Hackathon 2026 (M#26 PS #10).
The architecture and implementation have been developed independently to comply with intellectual property laws, prevent license contamination, and uphold the academic and contest integrity rules of M#26.

Below is an explicit inventory of open-source projects, research repositories, and literature consulted, along with their licenses, usage types, and attribution.

---

### 1. DisruptSC
- **Repository**: https://github.com/ccolon/disrupt-sc
- **Authors**: Célian Colon et al.
- **License**: GNU General Public License v3.0 (GPLv3)
- **Usage**: **Conceptual / Algorithmic Reference Only**.
- **Action Taken**: NO source code copied or linked. We studied the conceptual modeling of transport disruption, node capacity shocks, and criticality analysis. All simulation mechanics in CHAINSHIELD are implemented independently using SimPy and NetworkX.

### 2. Databricks Industry Solutions: Supply Chain Stress Test & Optimization
- **Repositories**:
  - https://github.com/databricks-industry-solutions/supply-chain-stress-test
  - https://github.com/databricks-industry-solutions/supply-chain-optimization
- **License**: Databricks Proprietary License ("Software may not be used except in connection with Licensee's use of Databricks Platform Services... constitutes Databricks Confidential Information").
- **Usage**: **Design Reference Only**.
- **Action Taken**: NO source code or Databricks-specific code copied or used. Mathematical optimization formulations (multi-echelon distribution, capacity bounds) were derived independently and formulated natively in open-source Pyomo using the HiGHS solver without any proprietary dependencies.

### 3. Multi-Echelon Inventory Optimization
- **Repository**: https://github.com/anshul-musing/multi-echelon-inventory-optimization
- **License**: GNU General Public License v3.0 (GPLv3)
- **Usage**: **Conceptual Reference Only**.
- **Action Taken**: NO code copied. Reimplemented standard (s, S) / (r, Q) inventory control logic and lead-time propagation independently within our SimPy discrete-event engine.

### 4. InventOpt
- **Repository**: https://github.com/SupplyChainSimulation/InventOpt
- **License**: MIT License
- **Usage**: **Reference on SimPy discrete-event simulation structures**.
- **Action Taken**: Independent implementation of discrete-event actors (Suppliers, Ports, Factories, Warehouses, Customers) tailored specifically for disruption injection and causal cascade tracking.

### 5. Open-Source Libraries Used Directly as Runtime Dependencies
- **SimPy** (MIT License): Discrete-event simulation framework.
- **NetworkX** (3-Clause BSD License): Graph and network analysis, topological sorting, centrality metrics.
- **Pyomo** (3-Clause BSD License): Mathematical programming and optimization modeling.
- **HiGHS / highspy** (MIT License): High-performance linear and mixed-integer programming solver.
- **NumPy & Pandas** (3-Clause BSD License): Numerical computing and time-series logging.
- **FastAPI & Pydantic** (MIT License): API engine and robust domain validation schemas.
- **SciPy** (3-Clause BSD License): Scientific computing and distribution fitting.
- **PyYAML** (MIT License): Scenario configuration loading.
