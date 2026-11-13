# Cell-level degradation and scaling case study

This repository analyzes two LR1865SZ laboratory cycle-test datasets, from raw Excel measurements to cycle features, degradation models, anomaly screening, exploratory RUL forecasts and illustrative pack scenarios. The analysis is diagnostic: protocol details, measurement uncertainty, nominal capacity and temperature are not verified.

## Run the six tasks

Use Python 3.11 or later and run from the repository root:

```bash
python -m pip install -r requirements.txt
python scripts/run_six_tasks.py
python -m unittest discover -s scripts -p "test_*.py"
```

The complete run starts from `LR1865SZ_cycles201217_001_2.xlsx` and `LR1865SZ_cycles201214_002_4.xlsx` in the project root. These source workbooks are ignored by Git, so obtain them separately when running from a fresh checkout. The preprocessing stage creates large local intermediate Excel and Parquet files. Set `BATTERY_EXPORT_REVIEW_XLSX=1` to also create the optional cleaned review workbook. Running the pipeline overwrites generated results. A single task can be run with `python scripts/run_six_tasks.py --task N` after its prerequisites have been generated.

| Task | Methods and main outputs |
|---|---|
| 1. Data engineering | `run_cleaning_pipeline.py`: timestamp normalization, source validation, Silver phase data and Gold cycle features, interval and counter audits. Outputs: `scripts/outputs/01_data_cleaning/` through `03_gold_cycle_features/`. |
| 2. Degradation | `stage_04_fit_capacity_fade.py`, `05_compare_capacity_models.py`, `06_differential_voltage.py`: empirical models, square-root elapsed time, physics-inspired and sequence baselines, and dV/dQ sensitivity. Outputs: `04_capacity_fade/` through `06_differential_voltage/`. |
| 3. Anomalies | `07_detect_battery_anomalies.py`: robust residual/local screening and DBSCAN with sensitivity analysis. Output: `07_anomaly_detection/`. |
| 4. RUL | `stage_08_individual_curve_rul.py`, `stage_09_estimate_rul_xgboost_shared.py`, `stage_10_estimate_rul_lstm_minimal.py`, `11_build_common_checkpoint_comparison.py`: curve extrapolation, XGBoost and LSTM, with forecast coverage and common-checkpoint comparisons. Outputs: `08_rul_individual_curves/` through `11_rul_model_comparison/`. |
| 5. Module/pack | `stage_13_scale_module_pack.py`: illustrative 12S2P capacity-envelope scenarios for cell variation, temperature and balancing. Output: `13_pack_scaling/`. |
| 6. Reporting | `14_build_task6_visualizations.py`, `build_six_task_report.py`: required figures and five-page report. Outputs: `14_reporting_visualization/` and `output/pdf/Technical_Report_Module_Outputs.pdf`. |

All output directories above are under `scripts/outputs/` unless otherwise stated. If local `scripts/task1_...` through `task6_...` files are present, they are a separate exploratory implementation and are not inputs to the pipeline above. See [scripts/README.md](scripts/README.md) for details.

## Interpretation

- The RUL endpoint is the first observed capacity below 80% of each cell's **cycle-2 delivered capacity**, not verified nominal state of health. At the provisional 2.5 Ah rating, the first complete measurements are already below 80% nominal; the nominal crossing cannot be dated from these data.
- Numerical coverage and counter agreement do not verify physical cycle completeness. Review flags are retained, and missing temperatures are not imputed.
- DBSCAN labels are screening candidates, not diagnoses. dV/dQ measured under load does not identify electrode mechanisms by itself.
- Model comparisons use very few histories from two cells and are not independent unseen-cell validation. Seed variation is not a calibrated fleet RUL distribution.
- Pack results use assumed cell variation, thermal acceleration and balancing, with no calibrated dynamic voltage or electrothermal/BMS model. They are scenario illustrations, not measured pack forecasts.

The report is written to `output/pdf/Technical_Report_Module_Outputs.pdf` and copied to `Technical_Report.pdf`. Checksums in `SUBMISSION_MANIFEST.json` are a historical package snapshot and will change when inputs or generated results change.
