# Task 4: Remaining Useful Life Estimation

Forecasts pack EOL from early cycle history using three model families evaluated at
four predefined checkpoints. EOL = first cycle strictly below 80 % of own cycle-2
discharge capacity.

## Run

```bash
python scripts/task4_rul_estimation/task4_rul_estimation.py
```

## Method

**Step 1 — Individual curve RUL (`stage_08_individual_curve_rul.py`)**
At each checkpoint (cycles 5, 8, 10, 12), fits all four fade models (Linear, Exponential,
Square-root, Power law) to the history available up to that cycle. Extrapolates the fitted
curve to find the first predicted crossing of the 80 % threshold. RUL = predicted EOL −
checkpoint cycle. No-crossing cases within 1,000 cycles are recorded as failures.

**Step 2 — XGBoost RUL (`stage_09_estimate_rul_xgboost_shared.py`)**
Pools both cells. Features: last 3 discharge capacities, last/mean cycle-to-cycle changes,
cycles since BOL. Trains a shared XGBoost regressor at each checkpoint on all available
windows from both cells. Predicts next-capacity changes iteratively until threshold is
crossed. Both cells are in the training set — not independent external validation.

**Step 3 — LSTM RUL (`stage_10_estimate_rul_lstm_minimal.py`)**
Minimal shared LSTM (1 hidden unit) trained on sliding windows of size 1 or 3.
Runs 3 seeds (42, 7, 123) per configuration. Normalises capacity by own cycle-2 value.
Iterative forecast: predicts next change, adds to last capacity, repeats until below 0.80.
Horizon = 1,000 cycles; non-crossing within horizon recorded as failure.

**Step 4 — Comparison (`11_build_common_checkpoint_comparison.py`)**
Normalises all predictions to a common schema. Primary fair comparison: checkpoints 8
and 10 only, four methods (Linear, Exponential, XGBoost, LSTM window=3). Reports MAE,
bias, and coverage (fraction of attempts that produced a valid crossing prediction).

## Key results at common checkpoints (8 & 10)

| Cell | Method | MAE (cycles) | Bias (cycles) | Coverage |
|---|---|---|---|---|
| 001_2 | Exponential (curve) | 0.5 | −0.5 | 100 % |
| 001_2 | Linear (curve) | 1.0 | −1.0 | 100 % |
| 001_2 | Shared XGBoost | 2.5 | +2.5 | 100 % |
| 001_2 | LSTM window=3 | 3.7 | +3.0 | 100 % |
| 002_4 | Linear (curve) | 0.5 | +0.5 | 100 % |
| 002_4 | Exponential (curve) | 2.0 | +2.0 | 100 % |
| 002_4 | Shared XGBoost | 2.0 | 0.0 | 100 % |
| 002_4 | LSTM window=3 | 5.3 | −1.7 | 100 % |

- Power law overestimates 002_4 RUL by 11 cycles; Square-root overestimates by 47 cycles.
- LSTM window=1 achieves MAE 1.25 (001_2) but −6.1 bias (002_4) — systematically early.
- Seed spread (3 runs) is not a population distribution; it reflects initialisation
  sensitivity with very few training windows.

## Outputs

| File | Description |
|---|---|
| `outputs/08_rul_individual_curves/predictions.csv` | Per-checkpoint curve RUL forecasts |
| `outputs/09_rul_xgboost/predictions.csv` | Per-checkpoint XGBoost forecasts |
| `outputs/10_rul_lstm/predictions.csv` | Per-checkpoint LSTM forecasts (all seeds/windows) |
| `outputs/11_rul_model_comparison/all_method_common_metrics.csv` | Full comparison table |
| `outputs/11_rul_model_comparison/all_attempts.csv` | Every attempted prediction |

## Limitations

- Both cells are in the training set for XGBoost and LSTM; results are not independent
  external validation.
- Only 4 checkpoints × 2 cells = 8 scored attempts per method (very small sample).
- The LSTM has 1 hidden unit — a minimal proof-of-concept, not a production model.
- Actual EOL is 11 and 22 cycles respectively; most checkpoints leave ≤ 14 cycles of
  history to train on.
- RUL bias is positive (overestimate) for XGBoost and LSTM on 001_2 — the model
  extrapolates more cautiously than the cell actually degrades.
