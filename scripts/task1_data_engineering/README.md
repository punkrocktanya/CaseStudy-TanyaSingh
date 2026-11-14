# Task 1: Data Engineering

Transforms two raw Excel workbooks into a clean, integrated Gold dataset using a
Bronze → Silver → Gold medallion architecture.

## Run

```bash
python scripts/task1_data_engineering/task1_data_engineering.py
```

## Method

**Bronze — `01_clean_and_validate.py`**
- Reads source Excel sheets (`LR1865SZ_cycles201217_001_2.xlsx`, `002_4.xlsx`).
- Validates schema: 9 required columns must be present.
- Applies 22 quality checks per row covering: missing temperature, timestamp issues
  (repeated, backward, gap > 10 s, axis mismatch), voltage/current plausibility, counter
  resets and decreases, duplicate rows, and cycle-index jumps.
- Assigns `row_quality_status`: REJECTED (critical), FLAGGED (soft), or OK.
- Exports all rows (including rejected) to Parquet for full traceability.

**Silver — `02_silver_transform.py`**
- Assigns charge/discharge/rest phase labels from current sign (deadband 0.05 A).
- Checks phase continuity and counter agreement.
- Retains row-level quality flags.

**Gold — `03_build_cycle_features.py`**
- Trapezoidal current integration within valid phase intervals
  (same cycle, same phase, 0 < dt ≤ 5 s, no artifact; calendar-clock reversals are flagged but do not veto a valid test-clock interval).
- Derives per-cycle: Discharge_Capacity_Ah, Charge_Capacity_Ah, Coulombic_Efficiency_pct,
  Discharge_Energy_Wh, Duration_s, C-rate (mean and P99), cumulative energy throughput.
- Marks `Computationally_Complete` and `Discharge_Integration_Valid` per cycle.

## Key results

- Both cells: 99 computationally complete paired cycles (2–100), all `Discharge_Integration_Valid` and marked `REVIEW`; physical protocol completeness is not verified.
- Cell 001_2: cycle-2 discharge = 1.5114 Ah; cycle-2 CE = 100.52 % (flagged).
- Cell 002_4: cycle-2 discharge = 1.6878 Ah.
- Temperature column is entirely missing (all rows flagged `temperature_missing`).

## Outputs

| File | Description |
|---|---|
| `outputs/02_silver_phase_data/*_silver.parquet` | Phase-annotated rows |
| `outputs/03_gold_cycle_features/battery_cycle_features_gold.parquet` | Cycle-level features |
| `outputs/03_gold_cycle_features/battery_cycle_features_gold.csv` | Same, CSV copy |

## Limitations

- Temperature is missing for all measurements; thermal analysis downstream is impossible.
- Nominal capacity (2.5 Ah rating) is provisional; both cells are already below 80% of
  nominal at their first complete cycle.
- The two cells operated at different currents and are not a matched population.
- Voltage "outside plausible" bounds (2.5/4.3 V) are hardcoded in `01_clean_and_validate.py`
  alongside config-driven spec bounds — inconsistent sourcing, both currently correct.
- `cycle_elapsed_s` groupby uses unvalidated `source["Cycle_Index"]`; NaN cycle indices
  would be silently excluded from that column.
