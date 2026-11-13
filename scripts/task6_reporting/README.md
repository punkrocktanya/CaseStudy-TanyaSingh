# Task 6: Reporting and Visualization

Produces four publication-quality figures and a five-page technical report covering all
pipeline stages.

## Run

```bash
python scripts/task6_reporting/task6_report_and_visualizations.py
```

Requires Tasks 1–5 to have succeeded first.

## Implementation

- [`14_build_task6_visualizations.py`](14_build_task6_visualizations.py) — figures
- [`build_six_task_report.py`](build_six_task_report.py) — PDF report (current)

Historical report builders (`build_battery_report.py`, `build_limitations_report.py`,
`build_short_report.py`) are retained for provenance; the active report is
`build_six_task_report.py`.

## Method

**Visualizations (`14_build_task6_visualizations.py`)**

Each figure reads from saved CSVs only — no model retraining.

| Figure | Content | Source data |
|---|---|---|
| `01_capacity_predictive_curves` | Measured discharge Ah + 4 model curves + 80% threshold + observed EOL marker | `cycle_capacity_analysis.csv`, `model_parameters.csv` |
| `02_coulombic_efficiency` | CE % per cycle; flagged cycles > 100% annotated | `cycle_capacity_analysis.csv` |
| `03_deviation_clusters` | DBSCAN feature scatter (top) + flagged cycles on capacity trajectory (bottom) | `anomaly_features.csv` |
| `04_forecasted_rul_distribution` | LSTM seed histogram + XGBoost and actual RUL at checkpoint 8 | `predictions.csv` from tasks 4 |
| `05_all_rul_models_checkpoints` | All 7 RUL methods at checkpoints 5/8/10/12 | `all_attempts.csv` |

**Report (`build_six_task_report.py`)**

Five A4 pages built with ReportLab, enforced by `assert pages == 5`.
Structure:

| Page | Content |
|---|---|
| 1 | Data engineering scope; medallion pipeline description; observed EOL table |
| 2 | Capacity fade figures; coulombic efficiency; best-model RMSE table |
| 3 | Anomaly cluster figure; dV/dQ process and results |
| 4 | RUL distribution figure; method comparison table (MAE, coverage) |
| 5 | Pack scaling scenario table; fleet/passport extension discussion |

## Key outputs

| File | Description |
|---|---|
| `outputs/14_reporting_visualization/01–05_*.png/.pdf` | Five figures (PNG + PDF) |
| `outputs/Technical_Report.pdf` | Five-page technical report |
| `outputs/14_reporting_visualization/rul_distribution_summary.csv` | RUL distribution statistics at checkpoint 8 |
| `outputs/14_reporting_visualization/visualization_manifest.json` | SHA-256 provenance hashes |

## Limitations

- `build_six_task_report.py` enforces exactly 5 pages; adding content requires careful
  size budgeting or the script will raise `RuntimeError`.
- `05_all_rul_models_checkpoints` uses a compact legend at the bottom; labels may
  overlap if figure width is reduced.
- The RUL histogram uses only 3 LSTM seeds — not a calibrated uncertainty distribution.
- `04_forecasted_rul_distribution` is fixed to checkpoint 8; earlier or later checkpoints
  require re-running with a different filter.
