# Task 2: Degradation Modeling

Fits four capacity-fade models, extracts dV/dQ degradation signatures, and compares
model performance using a chronological train/validate/test split.

## Run

```bash
python scripts/task2_degradation_modeling/task2_degradation_modeling.py
```

## Method

### Step 1 — Capacity fade fitting (`stage_04_fit_capacity_fade.py`)

Input: `battery_cycle_features_gold.parquet` filtered to `Computationally_Complete`
cycles 2–100 (`n = Cycle_Index − 2`).

Four models:

| Model | Equation | Parameters |
|---|---|---|
| Linear | Q = q₀ − a·n | q₀, a ≥ 0 |
| Exponential | Q = q₀·exp(−k·n) | q₀ ≥ 0, k ∈ [0, 0.2] |
| Square-root time | Q = q₀ − a·√t | q₀, a ≥ 0 |
| Power law | Q = q₀ − a·nᵇ | q₀, a ≥ 0, b ∈ [0.05, 2] |

Fitting: profile least squares (closed-form q₀/a, grid search over nonlinear exponent
with 5 iterative refinements). Nonlinear parameters constrained; no log transform.

Chronological split: train 2–70, validate 71–85, refit 2–85, test 86–100.

Sensitivity analysis: re-fits excluding cycles where CE > 100 % to test robustness.

### Step 2 — Model comparison (`05_compare_capacity_models.py`)

Compares all four models plus fixed-origin persistence baseline on the same split.
Square-root time is excluded from forecast winner selection (uses future timestamps).

### Step 3 — Differential voltage (`06_differential_voltage.py`)

Integrates discharge current to get Q; interpolates V(Q) onto 301 points; smooths with
three Savitzky-Golay windows (11, 21, 31 pts); detects interior dV/dQ peaks; stability
check requires peak to appear in all three windows and in a neighbouring cycle.

## Key results

| Cell | q₀ (full fit) | k (/cycle) | Full R² | Val RMSE (Ah) | Winner |
|---|---|---|---|---|---|
| 001_2 | 1.432 Ah | 0.01954 | 0.987 | 0.0644 | Exponential |
| 002_4 | 1.764 Ah | 0.01454 | 0.994 | 0.0078 | Exponential |

- Capacity decline: 001_2 drops 1.511→0.270 Ah (−82 %); 002_4 drops 1.688→0.453 Ah (−73 %).
- Test R² is negative for most models (narrow 15-cycle window; persistence wins on this range).
- Power-law sensitivity (CE-filter effect): max 0.42 Ah change for 001_2 — substantial.
- dV/dQ stable detections: 20/33 candidates for 001_2, 3/21 for 002_4 (across 6 cycles).

## Outputs

| File | Description |
|---|---|
| `outputs/04_capacity_fade/cycle_capacity_analysis.csv` | 198-row master cycle table |
| `outputs/04_capacity_fade/evaluation_metrics.csv` | Per-model MAE/RMSE/R² |
| `outputs/04_capacity_fade/model_parameters.csv` | Fitted parameters per scope |
| `outputs/04_capacity_fade/predictions.csv` | Per-cycle model predictions |
| `outputs/06_differential_voltage/feature_cycle_summary.csv` | dV/dQ candidate summary |

## Limitations

- Full-series fits use all 99 cycles and are descriptive, not predictive.
- Square-root time model uses future timestamps; excluded from live-forecast comparison.
- `Fade_Rate_Ah_per_Cycle_Smoothed` follows ΔQ sign (negative = fade); the unsmoothed
  `Fade_Rate_Ah_per_Cycle` follows −ΔQ (positive = fade). The sign convention differs
  between the two columns — a known inconsistency flagged in the report.
- Fitted exponent ranges are hardcoded in `fit()` (k: 0–0.2, b: 0.05–2).
- dV/dQ peak stability is a heuristic; no electrode identity can be claimed at high current.
- `assert len(g)==99` will crash if rerun on data with fewer valid cycles.
