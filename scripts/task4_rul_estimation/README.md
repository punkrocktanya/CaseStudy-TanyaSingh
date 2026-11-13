# Task 4: Remaining useful life

Compare capacity-fade extrapolation, feature-based XGBoost, and LSTM sequence forecasts at early checkpoints, including unsuccessful crossings and forecast coverage.

## Run

From the project root:

```bash
python scripts/task4_rul_estimation/task4_rul_estimation.py
```

Run Tasks 1 and 2 first. The endpoint is 80% of cycle-2 delivered capacity, not verified nominal capacity; the 80%-nominal crossing cannot be dated from these observations.

This entry point runs the validated pipeline stages below in order and then copies their reviewable results into this folder. It stops on an error. The authoritative working outputs remain in `scripts/outputs/`; copies are refreshed only when this task runs. Intermediate Excel workbooks, cleaned Parquet files and per-row interval diagnostics are omitted from the copies to avoid duplicating large files.

## Implementation

- [stage_08_individual_curve_rul.py](../stage_08_individual_curve_rul.py)
- [stage_09_estimate_rul_xgboost_shared.py](../stage_09_estimate_rul_xgboost_shared.py)
- [stage_10_estimate_rul_lstm_minimal.py](../stage_10_estimate_rul_lstm_minimal.py)
- [11_build_common_checkpoint_comparison.py](../11_build_common_checkpoint_comparison.py)

## Results and plots

- [outputs/08_rul_individual_curves/](outputs/08_rul_individual_curves/)
- [outputs/09_rul_xgboost/](outputs/09_rul_xgboost/)
- [outputs/10_rul_lstm/](outputs/10_rul_lstm/)
- [outputs/11_rul_model_comparison/](outputs/11_rul_model_comparison/)
