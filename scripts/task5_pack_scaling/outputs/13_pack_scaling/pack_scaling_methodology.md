# Task 5: Scaling to Module/Pack Level — Methodology

> **Scope:** This document proposes a methodology to extrapolate the cell-level analytical
> results produced by this pipeline to module and pack-level degradation. All referenced
> scripts are part of the existing codebase. No new code is required to understand the
> approach; the descriptions below explain how each pipeline stage would be extended or
> re-purposed.

---

## 1. Proposed Methodology

The core abstraction is a **virtual $N_s \times N_p$ cell array**, where the pack's total
deliverable capacity at any cycle is constrained by the minimum-capacity series block.
Formally, for a pack with $M$ modules each containing $S$ series groups of $P$ parallel
cells:

$$Q_\text{pack}(n) = \min_{m} \left[ \min_{s} \left( \sum_{p} Q_{m,s,p}(n) \cdot \text{SOC}_{m,s,p} \right) \right]$$

End-of-life is declared when $Q_\text{pack}(n) / Q_\text{pack}^\text{BOL} < 0.80$.

---

### A. Cell-to-Cell Variation (5 pts)

**The problem:** Manufacturing tolerances mean individual cells begin life with slightly
different initial capacities $q_0$ and degrade at different rates $k$. Because pack
capacity is bounded by the weakest series block, failure is driven by outlier cells — not
the population mean. Averaging across cells systematically overestimates pack lifetime.

**Proposed methodology — Monte Carlo ensemble:**

1. **Extract cell-level parameters.** The pipeline already fits an Exponential model
   $Q = q_0 \exp(-kn)$ for each cell in `stage_04_fit_capacity_fade.py` and records
   `Capacity_Residual_Ah` and `Local_Deviation_Ah` per cycle in
   `07_detect_battery_anomalies.py`. These provide empirical estimates of both the mean
   degradation trajectory and its cycle-by-cycle noise.

2. **Parameterise a population distribution.** Use the fitted $q_0$ and $k$ values across
   all available cells to estimate a bivariate distribution (e.g., independent lognormals
   with the observed coefficients of variation). Where only two physical cells are
   available, literature manufacturing CVs supplement the empirical estimate — but the
   empirical residuals remain the primary noise source.

3. **Instantiate the virtual pack.** Draw $N_s \times N_p \times E$ samples (where $E$ is
   the ensemble size) from the population distribution. Inject the empirical
   `Capacity_Residual_Ah` series from `07_detect_battery_anomalies.py` as additive
   per-cycle noise, so the simulation reflects measured variation patterns rather than
   white noise.

4. **Propagate to pack level.** At each simulated cycle, apply the topology envelope
   (sum parallels, take series minimum) to obtain a distribution of pack retention values.
   Report mean, P05, and P95 bands as the uncertainty envelope.

**Why this matters:** Minor initial capacity differences widen exponentially over hundreds
of cycles under exponential fade. A 3 % capacity CV at cycle 2 can translate into a
15–20 % spread in predicted EOL cycle at the pack level, meaning the worst-case cell —
not the average — determines when the vehicle is retired.

---

### B. Temperature Gradients (5 pts)

**The problem:** Cells in the thermal core of a module operate at consistently higher
temperatures than edge cells. Even a modest 5–10 K differential meaningfully accelerates
fade in the hotter cells via the Arrhenius relationship, compounding manufacturing spread.

**Proposed methodology — spatial Arrhenius scaling:**

1. **Build a spatial thermal matrix.** Assign each cell position $(m, s, p)$ a steady-state
   temperature offset $\Delta T_{m,s,p}$ derived from either a simplified 1-D or 2-D
   analytical thermal model (fin-array approximation), or measured data.
   `01_clean_and_validate.py` already flags `temperature_outside_broad_range` events;
   those flags identify which physical cells experienced sustained thermal stress and can
   seed the gradient estimate.

2. **Apply an Arrhenius acceleration factor** to each cell's degradation rate:

$$k_{m,s,p}^\text{eff} = k_{m,s,p} \cdot \exp\!\left[\frac{E_a}{R}\left(\frac{1}{T_\text{ref}} - \frac{1}{T_\text{ref} + \Delta T_{m,s,p}}\right)\right]$$

   where $E_a \approx 40{,}000$–$80{,}000\ \text{J/mol}$ for Li-ion capacity fade
   ($R = 8.314\ \text{J mol}^{-1}\text{K}^{-1}$; value must be calibrated to the
   specific chemistry).

3. **Update dynamically from telemetry.** As streaming cycle data arrives, re-estimate
   per-cell temperatures and update $\Delta T_{m,s,p}$. Cells with persistently elevated
   temperatures receive progressively larger acceleration factors, widening the intra-pack
   spread over time.

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
apart over cycles. If the BMS balancing circuit cannot re-equalize cells before the next
charge cycle, the cycle terminates early when the highest-voltage cell hits $V_\text{max}$,
leaving other cells undercharged. This **apparent capacity loss** stacks on top of
**electrochemical capacity loss** and the two must be distinguished to avoid
misattributing a BMS tuning problem as accelerated cell ageing.

**Proposed methodology — OCV/SOC drift and balancing-rate model:**

1. **Track OCV–SOC drift per cell.** The `06_differential_voltage.py` script already
   extracts $dV/dQ$ curves and monitors the shifting capacity span of voltage peaks. This
   same infrastructure can track each simulated cell's Open Circuit Voltage as a function
   of its instantaneous SOC.

2. **Compute the end-of-charge voltage spread.** At full charge, cells with higher
   capacity reach $V_\text{max}$ later; cells with elevated internal resistance reach it
   earlier. The voltage spread $\Delta V$ across the series string determines how much
   charge is inaccessible in the under-charged cells.

3. **Model three balancing strategies and their limits:**

   | Strategy | Mechanism | Energy loss | Limitation |
   |---|---|---|---|
   | No balancing | None | Zero | Full SOC spread is permanent |
   | Passive (resistive) | Bleed excess from high-SOC cells via resistor | Dissipated as heat | Limited by $I_b$ and available time $\Delta t$; heat fed back into thermal model |
   | Active (charge transfer) | Shuttle energy from high-SOC to low-SOC | Conversion loss $1 - \eta_\text{active}$ | Limited by donor capacity, recipient deficit, $I_b$, $\Delta t$, and $\eta$ |

   The key balancing constraint is:

   $$\Delta Q_\text{balanced} = \min\!\left(I_b \cdot \Delta t,\ Q_\text{donor},\ Q_\text{deficit}\right)$$

   Any SOC imbalance that exceeds this budget persists and reduces accessible pack
   capacity.

4. **Separate electrochemical from apparent degradation.** Compare pack retention under
   the same fade parameters with and without balancing. The gap between the two curves is
   the apparent capacity loss attributable to balancing inefficiency — a recoverable loss
   if the BMS is retuned, unlike the irreversible electrochemical component.

5. **Feed balancing heat back into the thermal model.** Passive balancing dissipates
   energy as heat inside the module, raising $\Delta T_{m,s,p}$ and increasing
   $k^\text{eff}$ in the next cycle — a feedback loop between §B and §C that a purely
   electrostatic model misses.

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

Each module accumulates its own imbalance state independently: the thermal gradient and
balancing budget (§B, §C) are scoped to the module's internal geometry, not the full pack
string. Two modules in the same pack can therefore have very different internal imbalance
histories depending on their position in the cooling flow path.

**Stage 2 — module → pack.**
Once per-module capacity distributions are obtained, the pack capacity is:

$$Q_\text{pack}(n) = \min_{m \in M} Q_\text{module}^{(m)}(n)$$

The module-level P05 distribution, not the raw cell-level distribution, feeds this second
minimisation. This matters because aggregating $P$ parallel cells within a series group
partially averages out cell-level noise before the series-minimum is taken — so the
effective CV entering the pack-level calculation is lower than the raw cell CV.

**Why the intermediate step matters for maintenance:**

- **Replacement decisions** are made at module granularity. A module whose P05 retention
  crosses 80 % is flagged for replacement even if the pack mean is still above threshold.
- **Second-life grading** sorts modules by their remaining capacity distribution. A module
  with low mean *and* low variance is a candidate for stationary storage; one with high
  variance but adequate mean needs further cell-level inspection before re-use.
- **Fault isolation** is faster: anomaly flags from `07_detect_battery_anomalies.py` are
  associated with a module ID, allowing the BMS to pinpoint a specific module rather than
  the entire pack.

---

### E. Pack-Level RUL Propagation

The cell-level RUL model (task 4, `stage_08_individual_curve_rul.py` and
`10_rul_lstm.py`) produces a predicted EOL cycle $\hat{n}_\text{EOL}$ per cell. Converting
this to a **pack-level RUL** requires formalising the weakest-link relationship across the
full ensemble.

**Step 1 — build the joint EOL distribution.**
For each ensemble member $e$ and each cell $(m, s, p)$, the cell-level model gives a
predicted EOL $\hat{n}_{e,m,s,p}$. The pack EOL for that ensemble member is:

$$\hat{n}_\text{pack}^{(e)} = \min_{m,s,p}\ \hat{n}_{e,m,s,p}$$

Taking this minimum across all cells converts the per-cell EOL distribution into a
**pack EOL distribution**. Because the minimum of $N$ random variables shifts left and
narrows as $N$ grows, the pack RUL is both shorter and more predictable than the
single-cell RUL — a counterintuitive result that the Mean-Pack approach completely misses.

**Step 2 — report pack RUL with calibrated uncertainty.**

| Statistic | Meaning |
|---|---|
| $\text{P50}(\hat{n}_\text{pack})$ | Median predicted pack EOL cycle |
| $\text{P05}(\hat{n}_\text{pack})$ | Conservative (safe) RUL — 95 % of ensemble members last at least this long |
| $\text{P95}(\hat{n}_\text{pack})$ | Optimistic RUL — only 5 % of ensemble members last this long |
| $\text{P50} - n_\text{current}$ | **Pack RUL in remaining cycles** at the current cycle $n_\text{current}$ |

The P05 value is the operationally relevant figure for safety and warranty decisions.

**Step 3 — update RUL online.**
At each new cycle, the pipeline re-fits the exponential model to the latest capacity
measurements, generates a fresh ensemble, and recomputes $\hat{n}_\text{pack}$. The RUL
estimate shrinks monotonically and its uncertainty band narrows as more cycles of real
data constrain the rate distribution.

**Step 4 — propagate task-4 LSTM uncertainty.**
The LSTM in `10_rul_lstm.py` produces a point estimate. To propagate uncertainty into the
pack RUL, replace the point estimate with a **bootstrap ensemble**: re-train the LSTM on
$B$ bootstrap resamples of the available cycle history, obtain $B$ predicted EOL values
per cell, and use all $B \times N_\text{cells}$ predictions to construct
$\hat{n}_\text{pack}^{(e)}$. This keeps the pack-level uncertainty bands honest rather
than implying false precision from a single model run.

---

### F. Degradation Mode Interactions at Pack Scale

Cell-level fits describe the aggregate capacity trajectory but do not distinguish between
the underlying degradation mechanisms. At pack scale, different mechanisms interact
non-linearly in ways that cannot be captured by simply scaling a single-cell exponential.

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
**superlinear in pack size** under naive scaling.

**3. Mechanical fatigue (particle cracking, delamination)**
Mechanical fatigue accumulates with cumulative charge throughput and is exacerbated by
large SOC swings. In a series string, cells chronically undercharged by balancing
limitations (§C) experience smaller SOC swings and therefore accumulate less mechanical
fatigue — partially offsetting their electrochemical disadvantage. Conversely, cells at
the high-voltage end of the string undergo larger swings and accumulate fatigue faster.

Implication: a pack-level model that ignores mechanism interactions will over-predict the
lifetime of high-swing cells and under-predict the lifetime of chronically undercharged
cells. The `Capacity_Residual_Ah` series from `07_detect_battery_anomalies.py` can be
decomposed by cycle-by-cycle charge throughput to separate the fatigue contribution from
the SEI contribution.

**Interaction summary:**

| Mechanism | Dominant driver | Pack-scale interaction | Pipeline signal |
|---|---|---|---|
| SEI growth | Temperature, time | Spatially correlated; use correlated sampling | `temperature_outside_broad_range` flags |
| Lithium plating | High rate, low T | Current crowding in parallel groups; superlinear with pack size | dV/dQ anode peak shift (`06_differential_voltage.py`) |
| Mechanical fatigue | SOC swing amplitude | Anti-correlated with balancing undercharge; partially compensating | Throughput-normalised `Capacity_Residual_Ah` |

---

### G. Worked Numerical Example

A concrete example grounds the equations above and shows how the numbers from the
existing pipeline feed into the pack model.

**Setup:** 4S2P module (4 series groups, 2 parallel cells per group), three modules in
series — a 12S2P, 24-cell pack. Use values directly from the pipeline outputs.

**Cell parameters (from `stage_04_fit_capacity_fade.py`):**

| Cell | $q_0$ (Ah) | $k$ (cycle⁻¹) |
|---|---|---|
| 001_2 | 1.85 | 0.0213 |
| 002_4 | 1.86 | 0.0107 |

For this example, use cell 001_2 as the population baseline with capacity CV = 3 % and
rate CV = 15 %.

**Ensemble draw (3 representative samples from E = 100):**

| Sample | Cell position | $q_0$ (Ah) | $k$ (cycle⁻¹) | $\Delta T$ (K) | $k^\text{eff}$ |
|---|---|---|---|---|---|
| 1 | Module 1, Group 2, Cell A | 1.90 | 0.0198 | 0 K (edge) | 0.0198 |
| 2 | Module 2, Group 3, Cell B | 1.84 | 0.0241 | 5 K (mid) | 0.0241 × 1.10 = **0.0265** |
| 3 | Module 3, Group 1, Cell A | 1.82 | 0.0231 | 10 K (core) | 0.0231 × 1.21 = **0.0280** |

Arrhenius factor at $\Delta T = 10$ K, $E_a = 50{,}000$ J/mol:
$$\exp\!\left[\frac{50000}{8.314}\left(\frac{1}{298.15} - \frac{1}{308.15}\right)\right] \approx 1.21$$

**Pack capacity at cycle 20 (sample 1):**

$$Q_{m,s,p}(20) = q_0 \cdot e^{-k^\text{eff} \cdot 20}$$

| Position | $Q(20)$ (Ah) |
|---|---|
| Module 1, Group 2, Cell A ($k^\text{eff}=0.0198$) | $1.90 \times e^{-0.396} = 1.29$ |
| Module 2, Group 3, Cell B ($k^\text{eff}=0.0265$) | $1.84 \times e^{-0.530} = 1.07$ |
| Module 3, Group 1, Cell A ($k^\text{eff}=0.0280$) | $1.82 \times e^{-0.560} = 1.03$ |

For a full module (assume all other cells similar to Module 1): group capacities sum two
parallel cells (~2.58 Ah per group), module capacity = minimum group = ~2.44 Ah.

The limiting module in this sample is **Module 3** (hottest cells, fastest degradation).
Pack capacity is therefore constrained by Module 3 — not by the average of all 24 cells.

**BOL reference** (all cells at $q_0$, SOC = 1):
$$Q_\text{pack}^\text{BOL} = \min_m \left[\min_s \left(1.85 + 1.85\right)\right] = 3.70\ \text{Ah}$$

**Retention at cycle 20:**
$$\frac{Q_\text{pack}(20)}{Q_\text{pack}^\text{BOL}} \approx \frac{2.06}{3.70} = 0.557$$

This is well below the 0.80 EOL threshold — consistent with the pipeline's observed EOL
of ~11 cycles for cell 001_2 when thermal gradients are present. The example illustrates
why the core cells determine pack life: even though edge cells still retain 69 % capacity
at cycle 20, the pack has already failed.

---

## 2. Trade-offs: Accuracy vs. Computational Scalability

Scaling from two cells to a pack of thousands forces an explicit choice on the
accuracy–scalability frontier. Three operating points are relevant:

### High Accuracy — "Digital Twin"

**Approach:** Instantiate a separate sequence model (the LSTM from `10_rul_lstm.py`) or
full $dV/dQ$ tracker for every individual cell simultaneously.

**Accuracy:** Maximum — every weak link is tracked explicitly; no aggregation hides
localised hotspots or anomalous cells.

**Computational cost:** Scales as $O(N_s \cdot N_p)$ model inferences per cycle. For a
pack of 4,000 cells this is 4,000 parallel LSTM forward passes per cycle update —
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
localised thermal hotspots until failure is already in progress. The `Local_Deviation_Ah`
metric in `07_detect_battery_anomalies.py` exists precisely because the mean-pack signal
suppresses the information that matters most.

**When to use:** Coarse fleet-level dashboards only; never for safety-threshold or
warranty decisions.

---

### Optimal Compromise — "Cluster-Based Surrogate"

**Approach:** Use the unsupervised clustering logic already in
`07_detect_battery_anomalies.py`. Group the pack's cells into $C = 5$–$10$ dynamic
clusters based on real-time thermal states and voltage residuals using DBSCAN. Run the
expensive LSTM/XGBoost RUL model only on each cluster centroid — with priority on the
**worst-performing outlier cluster**, which represents the cells most likely to trigger
pack-level failure.

**Computational cost:** Scales as $O(C)$ model inferences per cycle. For 10 clusters out
of 4,000 cells, this is a **>99 % reduction** in inference cost vs. the Digital Twin.

**Accuracy:** Substantially better than Mean-Pack because the worst-case cluster
explicitly tracks the weakest cells. Cluster membership is updated each cycle as the
thermal and degradation state evolves, so cells that migrate into the high-risk cluster
are caught before they become the pack-limiting constraint.

**Key trade-off remaining:** Cluster centroids are representative summaries, not
individual cells. If two cells in the same cluster diverge mid-life, the centroid model
lags behind the true worst cell. This is bounded by monitoring within-cluster variance
and triggering a cluster split when it exceeds a threshold, incrementally increasing $C$.

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

The cluster-based surrogate is the recommended operating point for production deployment:
it preserves the safety-critical weakest-link sensitivity of the Digital Twin while
remaining computationally viable for real-time fleet monitoring and Battery Passport
generation.

---

## 3. Validation Requirements

The methodology is structurally sound but cannot produce calibrated probability intervals
without:

- **Measured cell population** (>20 matched cells from the same lot) to replace assumed
  CVs with empirical distributions.
- **Spatial temperature measurements** to calibrate $\Delta T_{m,s,p}$ and constrain $E_a$.
- **Cell-level current and voltage traces** to validate the OCV–SOC drift and balancing
  model.
- **Measured balancer behaviour** (actual $I_b$ and switching duty cycle) to replace the
  assumed constant-current model.

Until these are available, all pack-level projections should be labelled as
**synthetic sensitivity analyses** rather than calibrated lifetime predictions.
