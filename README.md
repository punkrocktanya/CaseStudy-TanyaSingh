# Cell-level degradation and scaling case study

This repository analyzes two LR1865SZ laboratory cycle-test datasets, from raw Excel measurements to cycle features, degradation models, anomaly screening, exploratory RUL forecasts and illustrative pack scenarios. The analysis is diagnostic: protocol details, measurement uncertainty, nominal capacity and temperature are not verified.

## Run the six tasks

Use Python 3.11 or later and run from the project root:

```bash
python -m pip install -r requirements.txt
python scripts/task1_data_engineering/task1_preprocess.py
python scripts/task2_degradation_modeling/task2_degradation_modeling.py
python scripts/task3_anomaly_detection/task3_anomaly_detection.py
python scripts/task4_rul_estimation/task4_rul_estimation.py
python scripts/task5_pack_scaling/task5_pack_scaling.py
python scripts/task6_reporting/task6_report_and_visualizations.py
```

Each task folder has its own runnable entry script, README and `outputs/` containing its reviewable tables and plots. The entry scripts run the validated stages in their task folders. Each task writes its authoritative results, plots and intermediate data directly to its own `outputs/` folder. Shared imports between tasks support the existing analysis logic. Large preprocessing intermediates are kept locally and excluded from Git.

To run all tasks in order, use `python scripts/run_six_tasks.py`. Run tests with `python -m unittest discover -s scripts -p "test_*.py"`. Individual tasks require the outputs of earlier tasks; see their READMEs for prerequisites.

| Task | Folder | Key contents |
|---|---|---|
| 1. Data engineering | [task1_data_engineering](scripts/task1_data_engineering/) | Cleaning, cycle features, missing data and quality checks |
| 2. Degradation modeling | [task2_degradation_modeling](scripts/task2_degradation_modeling/) | Capacity fade, model comparisons, dV/dQ analysis and limitations |
| 3. Anomaly detection | [task3_anomaly_detection](scripts/task3_anomaly_detection/) | Residual screening, DBSCAN and sensitivity |
| 4. RUL estimation | [task4_rul_estimation](scripts/task4_rul_estimation/) | Extrapolation, XGBoost, LSTM and coverage |
| 5. Pack scaling | [task5_pack_scaling](scripts/task5_pack_scaling/) | Cell variation, temperature and balancing scenarios |
| 6. Reporting | [task6_reporting](scripts/task6_reporting/) | Required plots and the five-page report |

The complete run starts from `LR1865SZ_cycles201217_001_2.xlsx` and `LR1865SZ_cycles201214_002_4.xlsx` in the project root. The source workbooks are ignored by Git and must be obtained separately for a fresh checkout. Set `BATTERY_EXPORT_REVIEW_XLSX=1` to create the optional cleaned review workbook. Running the pipeline overwrites generated outputs.

## Interpretation

- The RUL endpoint is the first observed capacity below 80% of each cell's **cycle-2 delivered capacity**, not verified nominal state of health. At the provisional 2.5 Ah rating, the first complete measurements are already below 80% nominal; the nominal crossing cannot be dated from these data.
- Numerical coverage and counter agreement do not verify physical cycle completeness. Review flags are retained, and missing temperatures are not imputed.
- DBSCAN labels are screening candidates, not diagnoses. dV/dQ measured under load does not identify electrode mechanisms by itself.
- Model comparisons use very few histories from two cells and are not independent unseen-cell validation. Seed variation is not a calibrated fleet RUL distribution.
- Pack results use assumed cell variation, thermal acceleration and balancing, with no calibrated dynamic voltage or electrothermal/BMS model. They are scenario illustrations, not measured pack forecasts.

The report is written to `scripts/task6_reporting/outputs/Technical_Report.pdf`, with convenience copies at `output/pdf/Technical_Report_Module_Outputs.pdf` and `Technical_Report.pdf`. Checksums in `SUBMISSION_MANIFEST.json` are a historical package snapshot and will change when inputs or generated results change.
