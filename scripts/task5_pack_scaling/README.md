# Task 5: Module and Pack Scaling

Proposes and illustrates a methodology to extrapolate cell-level degradation results to
module and pack level, covering cell-to-cell variation, temperature gradients, and
balancing inefficiencies.

## Run

```bash
python scripts/task5_pack_scaling/task5_pack_scaling.py
```

Requires Tasks 1 and 2 to have been run first (uses `cycle_capacity_analysis.csv`).

## Implementation

- [`stage_13_scale_module_pack.py`](stage_13_scale_module_pack.py)
- [`test_pack_scaling.py`](test_pack_scaling.py)

## Method

**Pack topology:** 4 series groups per module × 2 parallel cells × 3 modules in series
= 12S2P, 24 cells.

**Step 1 — Cell baseline**
Fits Exponential Q = q₀·exp(−k·n) to cycles ≤ 8 of each cell. Uses q₀ (cycle-1
capacity) and k (rate) as population baseline parameters.

**Step 2 — Monte Carlo ensemble (E = 100 samples)**
Draws initial capacities from Lognormal(μ=q₀, CV=3 %) and fade rates from
Lognormal(μ=k, CV=15 %) for every cell position in the pack.

**Step 3 — Spatial thermal gradient**
Assigns a linear 0–10 K temperature offset across all 24 cell positions. Applies
Arrhenius acceleration: k_eff = k × exp[Ea/R × (1/T_ref − 1/(T_ref + ΔT))], with
Ea = 20,000 J/mol (assumed; not calibrated to this chemistry).

**Step 4 — SOC initial imbalance**
Uniform random SOC deficits in [0, 3 %] assigned before balancing.

**Step 5 — Four scenarios**
1. `uniform_no_balance` — no gradient, no balancing
2. `gradient_no_balance` — 0–10 K gradient, no balancing
3. `gradient_passive` — gradient + resistive balancing (bleeds high-SOC cells)
4. `gradient_active` — gradient + charge-transfer balancing (η = 85 %)

**Step 6 — Topology envelope**
Pack capacity = min over modules of [min over series groups of (sum of parallel capacities × SOC)].
EOL when pack/BOL < 0.80.

## Key results

| Cell baseline | Scenario | Mean EOL (cycle) | Mean balance loss (Wh) |
|---|---|---|---|
| 001_2 | uniform_no_balance | 11.8 | 0.00 |
| 001_2 | gradient_no_balance | 10.3 | 0.00 |
| 001_2 | gradient_active | 10.3 | 0.07 |
| 001_2 | gradient_passive | 9.9 | 1.56 |
| 002_4 | uniform_no_balance | 22.7 | 0.00 |
| 002_4 | gradient_no_balance | 19.8 | 0.00 |
| 002_4 | gradient_active | 19.7 | 0.07 |
| 002_4 | gradient_passive | 18.9 | 1.71 |

- Passive balancing performs worse than active because it bleeds usable charge.
- Temperature gradient reduces mean EOL by ~1.5 cycles (001_2) and ~3 cycles (002_4).

## Outputs

| File | Description |
|---|---|
| `outputs/13_pack_scaling/scenario_summary.csv` | Mean/min/max EOL and balance loss per scenario |
| `outputs/13_pack_scaling/pack_scaling_methodology.md` | Full methodology document with equations |

## Limitations

- Ea = 20,000 J/mol is unrealistically low for Li-ion capacity fade (literature: 40,000–80,000 J/mol);
  the thermal gradient effect is therefore underestimated.
- No voltage/OCV model — only charge-availability (Ah) envelope.
- No unequal parallel-cell current dynamics, thermal ODE, resistance growth, or BMS voltage cutoff.
- Balancing SOC corrections held fixed over ageing; balancing heat not fed back into degradation.
- Population CVs (3 % capacity, 15 % rate) are assumed from literature, not measured.
- Based on only 2 physical cells; ensemble spread is entirely from assumed distributions.
- Energy loss uses a fixed 3.7 V cell voltage — illustrative only.
