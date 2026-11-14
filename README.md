# Battery Degradation & RUL Analysis — Case Study 2

Two LR1865SZ laboratory cells (`001_2`, `002_4`) each have 99 computationally complete paired cycles, all marked for review. They are processed
through a six-task pipeline that takes raw Excel measurements from source to pack-level
degradation projections and a five-page technical report.

---

## Repository layout

```
Casestudy-2/
├── LR1865SZ_cycles201217_001_2.xlsx   ← raw source data (cell 001_2)
├── LR1865SZ_cycles201214_002_4.xlsx   ← raw source data (cell 002_4)
├── battery_thresholds.json             ← shared quality thresholds (voltages, currents)
├── battery_specification.md            ← cell datasheet / spec notes
├── requirements.txt                    ← Python dependencies
├── Technical_Report.pdf                ← copy of the final five-page report
│
├── scripts/
│   ├── run_six_tasks.py               ← orchestrator — runs all tasks in order
│   ├── output_paths.py                ← maps output group names → owning task folders
│   │
│   ├── task1_data_engineering/        ── Task 1
│   ├── task2_degradation_modeling/    ── Task 2
│   ├── task3_anomaly_detection/       ── Task 3
│   ├── task4_rul_estimation/          ── Task 4
│   ├── task5_pack_scaling/            ── Task 5
│   ├── task6_reporting/               ── Task 6
│   └── utilities/                     ── shared helpers
│
├── output/pdf/                         ← report copies placed here by Task 6
├── notebooks/                          ← exploratory notebooks (not part of pipeline)
└── deliverables/                       ← submission artefacts
```

---

## Quick start

```bash
# Run the full pipeline (Tasks 1 → 6 in order)
python scripts/run_six_tasks.py

# Re-run a single task (prerequisites must already exist)
python scripts/run_six_tasks.py --task 4
```

> **Task 1 requires** the two source `.xlsx` files in the project root.  
> **Tasks 2–6** read from the outputs of earlier tasks — run in order on first use.

---

## Notebooks

- [Preprocessing and model diagnostics](notebooks/preprocessing_and_models.ipynb): inspect quality flags, derived cycle features, capacity-model forecasts, RUL coverage and pack scenarios.
- [Visualization report](notebooks/visualization_report.ipynb): review the required capacity, efficiency, anomaly and RUL figures, plus dV/dQ and pack results.

The notebooks read saved pipeline outputs and do not retrain models. Install `requirements.txt`, generate the relevant task outputs, and run `jupyter lab` from the project root. Open either notebook and run its cells in order.

## Pipeline flow

```
Excel workbooks (001_2, 002_4)
        │
        ▼
┌─────────────────────────────┐
│  TASK 1 — Data Engineering  │  Bronze → Silver → Gold ETL
│  run_cleaning_pipeline.py   │  22 quality checks per row
└────────────┬────────────────┘
             │  outputs/03_gold_cycle_features/battery_cycle_features_gold.parquet
             ▼
┌──────────────────────────────────┐
│  TASK 2 — Degradation Modeling   │  4 capacity-fade models + dV/dQ analysis
│  stage_04 → 05 → 06 → summary   │
└────────────┬─────────────────────┘
             │  outputs/04_capacity_fade/cycle_capacity_analysis.csv
             │  outputs/06_differential_voltage/feature_cycle_summary.csv
             ▼
┌──────────────────────────────────┐
│  TASK 3 — Anomaly Detection      │  Residual scoring + DBSCAN clustering
│  07_detect_battery_anomalies.py  │
└────────────┬─────────────────────┘
             │  outputs/07_anomaly_detection/anomaly_features.csv
             │  outputs/07_anomaly_detection/dbscan_labels.csv
             ▼
┌──────────────────────────────────┐
│  TASK 4 — RUL Estimation         │  Individual curve, XGBoost, LSTM at 4 checkpoints
│  stage_08 → 09 → 10 → 11        │
└────────────┬─────────────────────┘
             │  outputs/11_rul_model_comparison/all_method_common_metrics.csv
             ▼
┌──────────────────────────────────┐
│  TASK 5 — Pack Scaling           │  Monte Carlo 12S2P + methodology doc
│  stage_13_scale_module_pack.py   │
└────────────┬─────────────────────┘
             │  outputs/13_pack_scaling/scenario_summary.csv
             ▼
┌──────────────────────────────────────────┐
│  TASK 6 — Reporting & Visualizations     │  4 figures + 5-page PDF report
│  14_build_task6_visualizations.py        │
│  build_six_task_report.py                │
└──────────────────────────────────────────┘
             │
             ├── outputs/14_reporting_visualization/01–05_*.png/.pdf
             └── outputs/Technical_Report.pdf
```

---

## Task-by-task reference

### Task 1 — Data Engineering
**Folder:** `scripts/task1_data_engineering/`  
**Entry point:** `run_cleaning_pipeline.py`  
**Scripts in order:**
| Script | Role |
|---|---|
| `01_clean_and_validate.py` | Bronze: schema check, 22 quality flags, REJECTED/FLAGGED/OK per row |
| `02_silver_transform.py` | Silver: phase labelling (charge/discharge/rest), counter checks |
| `03_build_cycle_features.py` | Gold: trapezoidal integration, per-cycle capacity/energy/CE |

**Key outputs:**

| File | Description |
|---|---|
| `outputs/02_silver_phase_data/*_silver.parquet` | Phase-annotated measurement rows |
| `outputs/03_gold_cycle_features/battery_cycle_features_gold.parquet` | Cycle-level features (primary Gold table) |
| `outputs/03_gold_cycle_features/battery_cycle_features_gold.csv` | CSV copy of Gold |

**What you get:** 198 validated cycle records (99 per cell), discharge/charge capacity (Ah),
coulombic efficiency (%), energy throughput (Wh), C-rate, quality flags.

---

### Task 2 — Degradation Modeling
**Folder:** `scripts/task2_degradation_modeling/`  
**Entry point:** `task2_degradation_modeling.py`  
**Scripts in order:**
| Script | Role |
|---|---|
| `stage_04_fit_capacity_fade.py` | Fits 4 models (Linear, Exponential, Square-root, Power law); chronological split |
| `05_compare_capacity_models.py` | Side-by-side model comparison on same train/val/test split |
| `06_differential_voltage.py` | dV/dQ extraction across 6 representative cycles |
| `task2_analysis_summary.py` | Writes `feature_cycle_summary.csv` consumed by Task 6 |

**Key outputs:**

| File | Description |
|---|---|
| `outputs/04_capacity_fade/cycle_capacity_analysis.csv` | 198-row master table (all cycle features + fade rates) |
| `outputs/04_capacity_fade/model_parameters.csv` | Fitted parameters per model/scope |
| `outputs/04_capacity_fade/evaluation_metrics.csv` | MAE, RMSE, R² per model/scope |
| `outputs/04_capacity_fade/predictions.csv` | Per-cycle model predictions |
| `outputs/06_differential_voltage/feature_cycle_summary.csv` | dV/dQ candidate summary |

**What you get:** Lowest empirical validation RMSE is square-root time for 001_2 (0.0274 Ah) and exponential for 002_4 (0.0078 Ah). The square-root-time validation uses observed future timestamps, so it is a conditional retrospective comparison.

---

### Task 3 — Anomaly Detection
**Folder:** `scripts/task3_anomaly_detection/`  
**Entry point:** `task3_anomaly_detection.py`  
**Scripts in order:**
| Script | Role |
|---|---|
| `07_detect_battery_anomalies.py` | Exponential residuals + local deviation + DBSCAN |

**Key outputs:**

| File | Description |
|---|---|
| `outputs/07_anomaly_detection/anomaly_features.csv` | 92-column per-cycle table with all scores/flags |
| `outputs/07_anomaly_detection/anomaly_summary.csv` | Per-cycle decisions and review reasons |
| `outputs/07_anomaly_detection/dbscan_labels.csv` | Per-cycle DBSCAN cluster labels |

**What you get:** 001_2 has 9 local flags (early cycles), 0 trend candidates, ~25/98
DBSCAN noise cycles. 002_4 has 0 local/exponential flags, ~45/98 DBSCAN noise cycles.

---

### Task 4 — RUL Estimation
**Folder:** `scripts/task4_rul_estimation/`  
**Entry point:** `task4_rul_estimation.py`  
**Scripts in order:**
| Script | Role |
|---|---|
| `stage_08_individual_curve_rul.py` | Per-cell curve extrapolation at checkpoints 5/8/10/12 |
| `stage_09_estimate_rul_xgboost_shared.py` | Shared XGBoost trained on pooled windows |
| `stage_10_estimate_rul_lstm_minimal.py` | Minimal LSTM (1 unit), windows 1&3, 3 seeds |
| `11_build_common_checkpoint_comparison.py` | Normalises all predictions; fair comparison at checkpoints 8&10 |

**Key outputs:**

| File | Description |
|---|---|
| `outputs/08_rul_individual_curves/predictions.csv` | Curve RUL forecasts per checkpoint |
| `outputs/09_rul_xgboost/predictions.csv` | XGBoost RUL forecasts |
| `outputs/10_rul_lstm/predictions.csv` | LSTM forecasts (all seeds/windows) |
| `outputs/11_rul_model_comparison/all_method_common_metrics.csv` | Full comparison table |
| `outputs/11_rul_model_comparison/all_attempts.csv` | Every attempted prediction |

**What you get:** At checkpoints 8&10 — Exponential MAE 0.5 cycles (001_2), Linear MAE
0.5 cycles (002_4). XGBoost MAE 2.5/2.0 cycles. LSTM window=3 MAE 3.7/5.3 cycles.

---

### Task 5 — Pack Scaling
**Folder:** `scripts/task5_pack_scaling/`  
**Entry point:** `task5_pack_scaling.py`  
**Scripts in order:**
| Script | Role |
|---|---|
| `stage_13_scale_module_pack.py` | Monte Carlo 12S2P envelope; 4 thermal/balancing scenarios |
| `test_pack_scaling.py` | Unit tests for the topology envelope function |

**Key outputs:**

| File | Description |
|---|---|
| `outputs/13_pack_scaling/scenario_summary.csv` | Mean/min/max EOL and balance loss per scenario |
| `outputs/13_pack_scaling/pack_scaling_methodology.md` | Full methodology (§A–G): cell variation, thermal gradients, balancing, module step, RUL propagation, degradation modes, worked example |

**What you get:** Synthetic 12S2P pack. Temperature gradient cuts mean EOL by ~1.14 cycles (001_2) and ~2.54 cycles (002_4) in these assumed scenarios.
Passive balancing (~1.6 Wh loss) underperforms active (~0.07 Wh loss).

---

### Task 6 — Reporting & Visualization
**Folder:** `scripts/task6_reporting/`  
**Entry point:** `task6_report_and_visualizations.py`  
**Scripts in order:**
| Script | Role |
|---|---|
| `14_build_task6_visualizations.py` | Generates 5 publication figures from saved CSVs |
| `build_six_task_report.py` | Builds the 5-page PDF technical report |

**Key outputs:**

| File | Description |
|---|---|
| `outputs/14_reporting_visualization/01_capacity_predictive_curves.png` | Measured capacity + 4 model fits + EOL marker |
| `outputs/14_reporting_visualization/02_coulombic_efficiency.png` | CE % per cycle, flagged cycles annotated |
| `outputs/14_reporting_visualization/03_deviation_clusters.png` | DBSCAN scatter + flagged cycles on trajectory |
| `outputs/14_reporting_visualization/04_forecasted_rul_distribution.png` | LSTM seed histogram + XGBoost + actual RUL |
| `outputs/14_reporting_visualization/05_all_rul_models_checkpoints.png` | All 7 methods at all 4 checkpoints |
| `outputs/Technical_Report.pdf` | Five-page technical report (also copied to `output/pdf/` and root) |

---

## Key results summary

| Cell | Cycle-2 capacity | Observed EOL | Best model | Val RMSE | Exp. k |
|---|---|---|---|---|---|
| 001_2 | 1.511 Ah | Cycle 13 | Square-root time* | 0.0274 Ah | 0.0195 /cycle |
| 002_4 | 1.688 Ah | Cycle 24 | Exponential | 0.008 Ah | 0.0145 /cycle |

Capacity decline cycle 2→100: 001_2 −82 %, 002_4 −73 %.

---

## Data flow between tasks

```
Task 1 → battery_cycle_features_gold.parquet  ─────────────────────────────┐
                                                                            │
Task 2 → cycle_capacity_analysis.csv ──────────────┬────────────────────── │──→ Task 4
       → evaluation_metrics.csv                    │                       │
       → feature_cycle_summary.csv ────────────────│───────────────────────│──→ Task 6
       → feature_candidates_by_cycle.png ──────────│───────────────────────│──→ Task 6
                                                   │                       │
Task 3 → anomaly_features.csv ─────────────────────│───────────────────────│──→ Task 6
       → dbscan_labels.csv ─────────────────────────│───────────────────────│──→ Task 6
                                                   ▼                       │
                                   Task 4 → all_method_common_metrics.csv  │──→ Task 6
                                          → all_attempts.csv ──────────────│──→ Task 6
                                          ← (also reads Task 2 CSV)         │
                                                                            │
Task 5 → scenario_summary.csv ──────────────────────────────────────────────│──→ Task 6
                                                                            │
                                                                   Task 6 ←─┘
                                                              Technical_Report.pdf
```

---

--

## Limitations

- Only two cells from non-matched conditions; no population inference is valid.
- Temperature is missing throughout; thermal effects cannot be quantified from data.
- Nominal capacity (2.5 Ah) is provisional — both cells are below 80% of nominal at cycle 2.
- Pack scenarios use assumed manufacturing CVs, not measured fleet distributions.
- XGBoost and LSTM train on both cells — not independent external validation.
- No external validation on unseen cells or packs.

