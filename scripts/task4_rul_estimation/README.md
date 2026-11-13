# Task 4: Remaining useful life

Compare capacity-fade extrapolation, feature-based XGBoost, and LSTM sequence forecasts at early checkpoints, including unsuccessful crossings and forecast coverage.

## Run

From the project root:

```bash
python scripts/task4_rul_estimation/task4_rul_estimation.py
```

Run Tasks 1 and 2 first. The endpoint is 80% of cycle-2 delivered capacity, not verified nominal capacity; the 80%-nominal crossing cannot be dated from these observations.

This entry point runs the implementation files in this folder in order and stops on an error. Its authoritative results, plots and intermediate files are written directly to this folder’s `outputs/`. Some large preprocessing intermediates are kept locally and excluded from Git.

## Implementation

- [stage_08_individual_curve_rul.py](stage_08_individual_curve_rul.py)
- [stage_09_estimate_rul_xgboost_shared.py](stage_09_estimate_rul_xgboost_shared.py)
- [stage_10_estimate_rul_lstm_minimal.py](stage_10_estimate_rul_lstm_minimal.py)
- [11_build_common_checkpoint_comparison.py](11_build_common_checkpoint_comparison.py)

## Results and plots

- [outputs/08_rul_individual_curves/](outputs/08_rul_individual_curves/)
- [outputs/09_rul_xgboost/](outputs/09_rul_xgboost/)
- [outputs/10_rul_lstm/](outputs/10_rul_lstm/)
- [outputs/11_rul_model_comparison/](outputs/11_rul_model_comparison/)
- [outputs/12_rul_validation/](outputs/12_rul_validation/) — supplementary historical RUL validation

`test_rul_merged.py` tests the RUL methods. `12_build_rul_comprehensive_report.py` is a historical supplementary report builder; it is not run by default.
