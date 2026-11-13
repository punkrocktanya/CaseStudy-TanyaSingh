# Task 5: Scaling to Module/Pack Level — Methodology

> **Scope:** This document proposes a methodology to extrapolate the cell-level analytical
> results produced by this pipeline to module and pack-level degradation. All referenced
> scripts are part of the existing codebase. No new code is required to understand the
> approach; the descriptions below explain how each pipeline stage would be extended or
> re-purposed.

---

> **Interpretation:** Mechanism interactions and fleet strategies below are hypotheses or
> proposed extensions; they are not identified or validated by these two cell datasets.

## 1. Proposed Methodology

The core abstraction is a **virtual $N_s \times N_p$ cell array**, where the pack's total
deliverable capacity at any cycle is constrained by the minimum-capacity series block.
Formally, for a pack with $M$ modules each containing $S$ series groups of $P$ parallel
cells:

$$Q_\text{pack}(n) = \min_{m} \left[ \min_{s} \left( \sum_{p} Q_{m,s,p}(n) \cdot \text{SOC}_{m,s,p} \right) \right]$$

The implemented threshold is $Q_\text{pack}(n)/(2q_0)<0.80$, relative to an ideal fully charged identical-cell 2P group. It is not each simulated pack’s actual initial capacity.

---

### A. Cell-to-Cell Variation (5 pts)

**The problem:** Manufacturing tolerances mean individual cells begin life with slightly
different initial capacities $q_0$ and degrade at different rates $k$. Because pack capacity
is bounded by the weakest series block, failure is driven by outlier cells — not the
population mean. Averaging across cells systematically overestimates pack lifetime.

**Proposed methodology — Monte Carlo ensemble:**

1. **Extract cell-level parameters.** The pipeline already fits an Exponential model
   $Q = q_0 \exp(-kn)$ for each cell in `stage_04_fit_capacity_fade.py` and records
   `Capacity_Residual_Ah` and `Local_Deviation_Ah` per cycle in
   `07_detect_battery_anomalies.py`. These provide empirical estimates of both the
   mean degradation trajectory and its cycle-by-cycle noise.

2. **Parameterise a population distribution.** Use the fitted $q_0$ and $k$ values across
   all available cells to estimate a bivariate distribution (e.g., independent lognormals
   with the observed coefficients of variation). Where only two physical cells are
   available, literature manufacturing CVs supplement the empirical estimate — but the
   empirical residuals remain the primary noise source.

3. **Instantiate the virtual pack.** Draw $N_s \times N_p \times E$ samples (where $E$ is
   the ensemble size) from the population distribution to populate the capacity and rate
   arrays. Inject the empirical `Capacity_Residual_Ah` series from
   `07_detect_battery_anomalies.py` as additive per-cycle noise, so the simulation
   reflects measured variation patterns rather than white noise.

4. **Propagate to pack level.** At each simulated cycle, apply the topology envelope
   (sum parallels, take series minimum) to obtain a distribution of pack retention values.
   Report mean, P05 and P95 bands as the uncertainty envelope.

**Why this matters:** Minor initial capacity differences widen exponentially over hundreds
of cycles under exponential fade. A 3 % capacity CV at cycle 2 can translate into a
15–20 % spread in predicted EOL cycle at the pack level, meaning the worst-case cell —
not the average — determines when the vehicle is retired.

---

### B. Temperature Gradients (5 pts)

**The problem:** Cells in the thermal core of a module operate at consistently higher
temperatures than edge cells. Because electrochemical degradation follows an Arrhenius
relationship, even a modest 5–10 K differential between core and edge positions
meaningfully accelerates fade in the hotter cells, compounding the variation introduced
by manufacturing spread.

**Proposed methodology — spatial Arrhenius scaling:**

1. **Build a spatial thermal matrix.** Assign each cell position $(m, s, p)$ in the virtual
   pack a steady-state temperature offset $\Delta T_{m,s,p}$ derived from either:
   - A simplified 1-D or 2-D analytical thermal model (fin-array approximation), or
   - Measured temperature data where available. `01_clean_and_validate.py` already flags
     `temperature_outside_broad_range` events; those flags identify which physical cells
     experienced sustained thermal stress and can seed the gradient estimate.

2. **Apply an Arrhenius acceleration factor** to each cell's degradation rate:

$$k_{m,s,p}^\text{eff} = k_{m,s,p} \cdot \exp\!\left[\frac{E_a}{R}\left(\frac{1}{T_\text{ref}} - \frac{1}{T_\text{ref} + \Delta T_{m,s,p}}\right)\right]$$

   where $E_a \approx 40{,}000$–$80{,}000\ \text{J/mol}$ for Li-ion capacity fade
   (literature range; the value must be calibrated to the specific chemistry before use in
   a production system), $R = 8.314\ \text{J mol}^{-1}\text{K}^{-1}$, and $T_\text{ref}$
   is the reference temperature at which $k$ was fitted.

3. **Update dynamically from telemetry.** As streaming cycle data arrives, re-estimate the
   per-cell temperature from the available sensors and update $\Delta T_{m,s,p}$. Cells
   with persistently elevated temperatures receive progressively larger acceleration
   factors, widening the intra-pack spread over time.

4. **Propagate combined variation.** The effective rate array $k^\text{eff}$ now carries
   both manufacturing variation (§A) and positional thermal stress. The same topology
   envelope produces a pack retention distribution that reflects both sources jointly.

**Key sensitivity:** A 10 K gradient with $E_a = 50{,}000\ \text{J/mol}$ accelerates
degradation by roughly 20 % at the core relative to the edge — equivalent to adding
several percentage points of extra CV to the rate distribution. Ignoring the gradient
while trusting cell-level fits made at a uniform reference temperature will cause the
model to underestimate the rate of the fastest-ageing cells.

---

### C. Balancing Inefficiencies (5 pts)

**The problem:** Capacity and thermal differences cause individual cell voltages to drift
apart over cycles. If the BMS passive balancing circuit cannot bleed energy fast enough to
re-equalize cells before the next charge cycle, the charge terminates early when the
highest-voltage cell hits $V_\text{max}$, leaving other cells undercharged. This
**apparent capacity loss** (usable capacity truncated by balancing limits) stacks on top
of **electrochemical capacity loss** (irreversible active-material degradation), and the
two must be distinguished to avoid misattributing a BMS tuning problem as accelerated
cell ageing.

**Proposed methodology — OCV/SOC drift and balancing-rate model:**

1. **Track OCV–SOC drift per cell.** The `06_differential_voltage.py` script already
   extracts $dV/dQ$ curves and monitors the shifting capacity span of voltage peaks. This
   same infrastructure can track each simulated cell's Open Circuit Voltage as a function
   of its instantaneous SOC, using a parameterised OCV curve for the cell chemistry.

2. **Compute the end-of-charge voltage spread.** At full charge, cells with higher
   capacity will reach $V_\text{max}$ later; cells with elevated internal resistance will
   reach it earlier. The voltage spread $\Delta V$ across the series string determines
   how much charge is inaccessible in the under-charged cells.

3. **Model three balancing strategies and their limits:**

   | Strategy | Mechanism | Energy loss | Limitation |
   |---|---|---|---|
   | No balancing | None | Zero | Full SOC spread is permanent |
   | Passive (resistive) | Bleed excess from high-SOC cells via resistor | Dissipated as heat | Limited by balancing current $I_b$ and available time $\Delta t$; heat fed back into thermal model |
   | Active (charge transfer) | Shuttle energy from high-SOC to low-SOC cells | Conversion loss $1 - \eta_\text{active}$ | Limited by donor capacity, recipient deficit, $I_b$, $\Delta t$, and transfer efficiency |

   The key balancing constraint is:

   $$\Delta Q_\text{balanced} = \min\!\left(I_b \cdot \Delta t,\ Q_\text{donor},\ Q_\text{deficit}\right)$$

   Any SOC imbalance that exceeds this budget persists and reduces the accessible pack
   capacity.

4. **Separate electrochemical from apparent degradation.** Compare pack retention under
   the same fade parameters with and without balancing. The gap between the two curves is
   the **apparent capacity loss attributable to balancing inefficiency** — a recoverable
   loss if the BMS is retuned, unlike the irreversible electrochemical component.

5. **Feed balancing heat back into the thermal model.** Passive balancing dissipates
   energy as heat inside the module. This raises the local $\Delta T_{m,s,p}$ of the cells
   undergoing balancing, which in turn increases their $k^\text{eff}$ in the next cycle —
   creating a feedback loop between §B and §C that a purely electrostatic model misses.

---

### D. Module-Level Intermediate Step

The direct cell-to-pack jump obscures a critical serviceable boundary. In most EV
architectures the **module** — not the individual cell and not the full pack — is the
field-replaceable unit. Modelling at the module level first makes the methodology
practically useful for maintenance scheduling and second-life assessment.

**Two-stage aggregation:**

**Stage 1 — cell → module.**
Apply the topology envelope within a single module ($S$ series groups of $P$ parallel
cells). The module's deliverable capacity is:

$$Q_\text{module}^{(m)}(n) = \min_{s \in S} \left( \sum_{p \in P} Q_{m,s,p}(n) \cdot \text{SOC}_{m,s,p} \right)$$

Each module also accumulates its own imbalance state independently: the thermal gradient
and balancing budget (§B, §C) are scoped to the module's internal geometry, not the full
pack string. This means two modules in the same pack can have very different internal
imbalance histories depending on their position in the cooling flow path.

**Stage 2 — module → pack.**
Once per-module capacity distributions are obtained, the pack capacity is simply:

$$Q_\text{pack}(n) = \min_{m \in M} Q_\text{module}^{(m)}(n)$$

The module-level P05 distribution, not the cell-level distribution, feeds this second
minimisation. This matters because aggregating $P$ parallel cells within a series group
partially averages out cell-level noise before the series-minimum is taken — so the
effective CV entering the pack-level calculation is lower than the raw cell CV.

**Why the intermediate step matters for maintenance:**

- **Replacement decisions** are made at module granularity. A module whose P05 retention
  crosses 80 % is flagged for replacement even if the pack mean is still above threshold.
- **Second-life grading** sorts modules by their remaining capacity distribution. A module
  whose $Q_\text{module}$ mean and variance are both low is a candidate for stationary
  storage; one with high variance but adequate mean needs further cell-level inspection
  before re-use.
- **Fault isolation** is faster: the pipeline's anomaly flags from
  `07_detect_battery_anomalies.py` are associated with a module ID, allowing the BMS to
  flag a specific module for inspection rather than the entire pack.

---

### E. Pack-Level RUL Propagation

For each ensemble member, propagate **cell capacity trajectories**, not only cell EOL
cycles. At each future cycle, sum accessible capacities within each parallel group,
then take the minimum over series groups and modules:

$$Q_\text{pack}^{(e)}(n) = \min_{m,s}\sum_p Q_{e,m,s,p}(n)\,\text{SOC}_{e,m,s,p}.$$

The present simulation defines $Q_\mathrm{ref}=2q_0$ as the capacity of an ideal,
fully charged 2P group with identical cells. It records the first cycle where
$Q_\text{pack}^{(e)}(n)/Q_\mathrm{ref}<0.80$. This common ideal reference is **not**
the actual initial accessible capacity of each simulated pack: initial variation and
SOC deficits can contribute to the crossing. Using each pack's own initial accessible
capacity instead would answer a different retention question and requires a rerun.

The first individual cell to cross its own threshold does not necessarily determine
pack EOL: its parallel partner contributes to the group. Report the first crossing of
the simulated pack envelope for each ensemble member, with the forecast horizon and
non-crossing count. Scenario quantiles describe the assumed ensemble only; they are
not calibrated confidence intervals or validated warranty/safety thresholds.

For future RUL analysis, subtract the current cycle from each valid pack crossing.
Updating forecasts or bootstrapping cell models is proposed work, not implemented in
this simulation. Correlations, training uncertainty and pack voltage/current constraints
would need validation before interpreting a population-level distribution.

---

### F. Degradation Mode Interactions at Pack Scale

Cell-level fits describe the aggregate capacity trajectory but do not distinguish between
the underlying degradation mechanisms. At pack scale, different mechanisms interact
non-linearly in ways that cannot be captured by simply scaling a single-cell exponential.

**Three mechanism classes and their pack-scale behaviour:**

**1. SEI growth (calendar + cycle ageing)**
SEI growth is relatively uniform across cells at similar temperatures and SOC levels. Its
Arrhenius temperature dependence means it is well-captured by the §B gradient model: core
cells accumulate more SEI faster, increasing internal resistance and reducing accessible
capacity. At pack scale, SEI-driven fade is therefore **correlated across cells in the
same thermal zone** — the covariance structure matters, not just the marginal
distributions.

Implication for the Monte Carlo model: cells within the same module should not be sampled
independently. A **correlated lognormal** draw (using a spatial correlation length derived
from the thermal model) better represents how neighbouring cells share similar SEI
accumulation rates.

**2. Lithium plating (fast-charge and low-temperature)**
Lithium plating is triggered when the local anode potential drops below 0 V vs. Li/Li⁺,
which occurs preferentially at high charge rates or low temperatures. In a parallel group,
cells with lower impedance draw more current and are therefore more susceptible to
plating — a **current-crowding** effect that the topology envelope (which assumes uniform
parallel current) does not capture.

Implication: plating risk is highest in the parallel cell with the lowest internal
resistance at the start of life — which may be a *different* cell from the one with the
lowest capacity. The pipeline's `06_differential_voltage.py` dV/dQ analysis can detect
the capacity loss signature of lithium plating (loss of the anode staging peaks) and flag
which cells are affected. At pack scale, the fraction of parallel groups containing at
least one plating-affected cell grows with group count, making fast-charge degradation
**superlinear** in pack size under naive scaling.

**3. Mechanical fatigue (particle cracking, delamination)**
Mechanical fatigue accumulates with cumulative charge throughput and is exacerbated by
large SOC swings. In a series string, cells that are chronically undercharged by
balancing limitations (§C) experience smaller SOC swings and therefore accumulate less
mechanical fatigue — partially offsetting their electrochemical disadvantage. Conversely,
cells at the high-voltage end of the string undergo larger swings and accumulate fatigue
faster.

Implication: a pack-level model that ignores mechanism interactions will over-predict the
lifetime of high-swing cells and under-predict the lifetime of chronically undercharged
cells. The `Capacity_Residual_Ah` series from `07_detect_battery_anomalies.py` can be
decomposed by cycle-by-cycle charge throughput to separate the fatigue contribution from
the SEI contribution, providing a more accurate per-mechanism rate input to the pack
model.

**Interaction summary:**

| Mechanism | Dominant driver | Pack-scale interaction | Pipeline signal |
|---|---|---|---|
| SEI growth | Temperature, time | Spatially correlated; use correlated sampling | `temperature_outside_broad_range` flags |
| Lithium plating | High rate, low T | Current crowding in parallel groups; superlinear with pack size | dV/dQ anode peak shift (`06_differential_voltage.py`) |
| Mechanical fatigue | SOC swing amplitude | Anti-correlated with balancing undercharge; partially compensating | Throughput-normalised `Capacity_Residual_Ah` |

---

## 2. Trade-offs: Accuracy vs. Computational Scalability

Scaling from two cells to a pack of thousands forces an explicit choice on the
accuracy–scalability frontier. Three operating points are relevant:

### High Accuracy — "Digital Twin"

**Approach:** Instantiate a separate sequence model (the LSTM from `10_rul_lstm.py`) or
full $dV/dQ$ tracker (`06_differential_voltage.py`) for every individual cell in the
pack simultaneously.

**Accuracy:** Maximum. Every weak link is tracked explicitly; no aggregation hides
localised hotspots or anomalous cells.

**Computational cost:** Scales as $O(N_s \cdot N_p)$ model inferences per cycle. For a
pack of 4,000 cells, this is 4,000 parallel LSTM forward passes per cycle update —
requiring dedicated GPU infrastructure and making real-time fleet analytics or
instantaneous Battery Passport updates practically infeasible.

**When to use:** Offline forensic analysis of a single pack with known safety concerns;
prototype validation where compute budget is unconstrained.

---

### High Scalability — "Mean-Pack"

**Approach:** Average voltage, current, and temperature telemetry across the entire pack
and run a single XGBoost or LSTM RUL inference per cycle, treating the module as one
equivalent cell.

**Computational cost:** $O(1)$ model inferences per cycle — trivially scalable to
thousands of vehicles in real time.

**Accuracy:** Dangerously low for safety-critical decisions. Pack failure is dictated by
the weakest outlier cell. An averaged model consistently overestimates RUL and masks
localised thermal hotspots or anomalous cells until the failure is already in progress.
The `Local_Deviation_Ah` metric computed in `07_detect_battery_anomalies.py` exists
precisely because the mean-pack signal suppresses the information that matters most.

**When to use:** Coarse fleet-level dashboards where pack health is only one of many
signals; never for safety-threshold or warranty decisions.

---

### Optimal Compromise — "Cluster-Based Surrogate"

**Approach:** Use the unsupervised clustering logic already present in
`07_detect_battery_anomalies.py`. Rather than tracking all $N$ cells individually, apply
DBSCAN (or k-means) to group the pack's cells into $C = 5$–$10$ dynamic clusters based
on their real-time thermal states and voltage residuals. Run the computationally expensive
LSTM or XGBoost RUL model only on the centroid of each cluster — with priority on the
**worst-performing outlier cluster**, which represents the cells most likely to trigger
pack-level failure.

**Computational cost:** Scales as $O(C)$ model inferences per cycle, where $C \ll N$.
For 10 clusters out of 4,000 cells, this is a **>99 % reduction** in inference cost
relative to the Digital Twin approach.

**Accuracy:** Substantially better than the Mean-Pack approach because the worst-case
cluster explicitly tracks the weakest cells. The cluster membership is updated each cycle
as the thermal and degradation state evolves, so cells that migrate into the high-risk
cluster are caught before they become the pack-limiting constraint.

**Key trade-off remaining:** Cluster centroids are representative summaries, not
individual cells. If two cells in the same cluster diverge significantly mid-life — one
recovers to nominal behaviour while the other continues degrading — the centroid model
will lag behind the true worst cell. The residual error can be bounded by monitoring the
within-cluster variance and triggering a cluster split when it exceeds a threshold, at the
cost of incrementally increasing $C$.

---

### Summary Comparison

| Dimension | Digital Twin | Mean-Pack | Cluster Surrogate |
|---|:---:|:---:|:---:|
| Inference cost per cycle | $O(N)$ | $O(1)$ | $O(C),\ C \ll N$ |
| Captures weakest-cell failure | ✅ | ❌ | ✅ (cluster-level) |
| Detects localised hotspots | ✅ | ❌ | ✅ (if cluster splits) |
| Real-time fleet scalability | ❌ | ✅ | ✅ |
| Accuracy vs. true pack EOL | Highest | Lowest | High |
| Implementation complexity | High | Low | Medium |

The cluster-based surrogate is the recommended operating point for production deployment.
It preserves the safety-critical weakest-link sensitivity of the Digital Twin while
remaining computationally viable for real-time fleet monitoring and Battery Passport
generation.

---

## 3. Validation Requirements

The methodology above is structurally sound but cannot produce calibrated probability
intervals without the following additional data:

- **Measured cell population** (>20 matched cells from the same manufacturing lot) to
  replace the assumed capacity and rate CVs with empirical distributions.
- **Spatial temperature measurements** (thermocouples or IR camera at multiple positions)
  to calibrate $\Delta T_{m,s,p}$ and constrain $E_a$.
- **Current and voltage traces at cell level** (not just pack level) to validate the
  OCV–SOC drift and balancing model.
- **Measured balancer behaviour** (actual $I_b$ and switching duty cycle) to replace the
  assumed constant-current model.

Until these are available, all pack-level projections should be labelled as
**synthetic sensitivity analyses** rather than calibrated lifetime predictions.
