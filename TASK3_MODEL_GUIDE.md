# Capacity modelling - current merged submission

## Objective and data

The target is delivered high-current discharge capacity (Ah), not independently reference-tested SOH. The two input cells are `001_2` and `002_4`. Only their usable cycles 2-100 are used. Validation forecasts cycles 71-85 from fits through cycle 70; test forecasts 86-100 using history through cycle 85. Both are fixed-origin 15-cycle horizons. No future actual capacity enters the recursive ML forecasts.

Run `python 05_compare_capacity_models.py`; outputs are saved under `scripts/outputs/capacity_comparison_local`. The raw Excel files are not required when the cycle-feature CSV is present.

## Compared capacity-forecast models

- Exponential: bounded nonlinear regression against cycle count.
- Physics-constrained *phenomenological* surrogate: `q0 * exp(-a*sqrt(n)-b*n)`, with positive coefficients. This is not a fitted electrochemical ageing mechanism.
- Persistence: future capacity stays at its most recent observed value.
- Random Forest: normalized three-capacity change features, 200 trees / depth four / min leaf three, fitted per cell.
- **Updated LSTM:** one hidden unit and 18 parameters, three-cycle capacity windows, Adam 0.008, weight decay 0.0001, Huber loss, 130 epochs, seed 42. It uses the same `MinimalLSTM` architecture and `train()` function imported from `stage_10_estimate_rul_lstm_minimal.py`. This is a single-seed late-cycle capacity comparison, *not* the three-seed early-RUL exercise.

## Current saved test RMSE, Ah

| Model | Cell 001_2 | Cell 002_4 |
|---|---:|---:|
| Exponential | 0.075778 | 0.027380 |
| Phenomenological surrogate | 0.052220 | 0.027380 |
| Persistence | 0.030342 | 0.043391 |
| Random Forest | 0.012454 | 0.021403 |
| Updated minimal LSTM | 0.037969 | 0.051164 |

Values derive from `scripts/outputs/capacity_comparison_local/metrics.csv`. They do not establish superiority on unseen batteries; window overlap and the two-cell population are major limitations.

## Separate early-relative-RUL comparison

Run `stage_08_individual_curve_rul.py`, `stage_09_estimate_rul_xgboost_shared.py` and `stage_10_estimate_rul_lstm_minimal.py`, followed by `11_build_common_checkpoint_comparison.py`. The early-RUL endpoint is the first integer cycle below 80% of cycle-2 delivered capacity, not nominal-reference SOH. The fair comparison at checkpoints 8 and 10 uses common attempts and includes the minimal three-cycle LSTM seed runs, preserving failures and coverage. See `scripts/outputs/rul_common_checkpoint/README.md` and `output/pdf/Battery_RUL_Limitations_and_Validation.pdf`.
