# Cycle-by-cycle capacity fade

- Target: high-rate delivered discharge capacity (Ah), not certified SOH.
- Primary analysis: cycles 2–100; incomplete boundary pairs excluded. REVIEW status is retained as provenance.
- n = cycle index minus 2. t = days since cycle-2 discharge completion, using the test clock.
- Retention = discharge Ah / cycle-2 discharge Ah x 100. Cycle 2 is not a verified beginning-of-life reference.
- Four equations: linear Q=q0-a*n; exponential Q=q0*exp(-k*n); square-root Q=q0-a*sqrt(t); power law Q=q0-a*n^b.
- q0 is fitted. Parameters are constrained nonnegative; power exponent is bounded to [0.05, 2], exponential k to [0, 0.2] per cycle.
- Fits minimize squared error in Ah. Nonlinear parameters use a dense profile search with five local refinements; no log transformation of the target.
- Full-series fits describe the observed trajectory. Separate chronological evaluation trains on 2–70, validates on 71–85, then refits on 2–85 and tests on 86–100.
- Square-root-time evaluation uses observed future timestamps and is a conditional retrospective comparison, not a deployable fixed-origin forecast. It is excluded from selecting the cycle-only forecast winner.
- Negative predictions are reported, not clipped. No extrapolated lifetime or mechanism identification is claimed.

**Cell 001_2**

- Capacity: 1.511447 to 0.269956 Ah; decline 82.14%.
- Cycle-only model selected using validation RMSE: **Exponential**.
- Sensitivity analysis excludes 5 flagged CE cycles; the primary analysis retains them.
- Coefficients and separate descriptive/validation/test metrics are in the accompanying CSV files.

**Cell 002_4**

- Capacity: 1.687755 to 0.452649 Ah; decline 73.18%.
- Cycle-only model selected using validation RMSE: **Exponential**.
- Sensitivity analysis excludes 1 flagged CE cycles; the primary analysis retains them.
- Coefficients and separate descriptive/validation/test metrics are in the accompanying CSV files.

**Interpretation limits**

- Cycle-to-cycle change is ΔQ_n = Q_n − Q_(n−1). The plotted smoothed line is a centred 7-cycle rolling mean; negative ΔQ means fading. The separate positive fade-rate columns use −ΔQ.

- High-current polarization, changing charge endpoints and irreversible aging can all contribute. A fitted exponent does not identify their individual contributions.
- Missing temperature and reference-capacity tests prevent certified SOH or electrode-mechanism claims.
- Models are fitted independently to two trajectories; results do not establish population-level generalization.
- The last 15 cycles span a narrow capacity range, so test R2 may be poor even when Ah errors look small.
- Units of a: Ah/cycle for linear; Ah/sqrt(day) for square-root; Ah/cycle^b for power law. k is per cycle.
