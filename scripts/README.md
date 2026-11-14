# scripts/ — How This Pipeline Works

This folder contains all six analysis tasks and the utilities that tie them together.
Each task has its own entry script, implementation stages, outputs folder, and README.
Several tasks import shared code or read outputs from earlier tasks, so run them in order
for a fresh analysis.

---

## Interpretation limits

The EOL forecasts use 80% of each cell's cycle-2 delivered capacity, not verified nominal
capacity. The dV/dQ features do not uniquely identify LLI or LAM. Pack outcomes are
assumed scenarios, not validated pack measurements. See each task README for details.

---

## How to run

### Run everything (recommended first time)

From the **project root** (the folder containing the `.xlsx` files):

```bash
python scripts/run_six_tasks.py
```

This runs all six tasks in sequence. If one fails the whole run stops and shows the
error. Fix the problem and re-run from that task.

### Re-run a single task

```bash
python scripts/run_six_tasks.py --task 3
```

All earlier tasks must already have their outputs. Use this after fixing a bug in one
task without redoing everything.

### Run a task's entry script directly

```bash
python scripts/task2_degradation_modeling/task2_degradation_modeling.py
```

Same as `--task 2` but lets you run from any directory.

### Run with an execution report

```bash
python scripts/utilities/run_with_report.py task2_degradation_modeling/stage_04_fit_capacity_fade.py
```

Wraps any script in the `utilities/run_with_report.py` runner, which captures stdout,
records which output files changed, previews result CSVs, and writes a Markdown report
to `outputs/execution_reports/`.

---

## Folder structure

```
scripts/
├── run_six_tasks.py          ← orchestrator: runs tasks 1–6 in order
├── output_paths.py           ← maps output group names to their owning task folders
│
├── task1_data_engineering/   ── Task 1
├── task2_degradation_modeling/── Task 2
├── task3_anomaly_detection/  ── Task 3
├── task4_rul_estimation/     ── Task 4
├── task5_pack_scaling/       ── Task 5
├── task6_reporting/          ── Task 6
└── utilities/                ── shared helpers (not part of the analysis pipeline)
```

Each task folder follows the same layout:

```
taskN_name/
├── taskN_name.py             ← entry script (calls run_six_tasks.run_task(N))
├── stage_NN_*.py             ← implementation stages (numbered across all tasks)
├── test_*.py                 ← unit tests for that task's logic
├── __init__.py               ← package marker (keeps sys.path imports working)
├── README.md                 ← method, steps, outputs, limitations for this task
└── outputs/
    └── NN_group_name/        ← all results, plots, and CSVs for this stage
```

---

## Task 1 — Data Engineering

**Folder:** `task1_data_engineering/`  
**Entry:** `run_cleaning_pipeline.py`  
**Depends on:** The two source `.xlsx` files in the project root.

### What it does

Reads raw Excel cycling data for cells `001_2` and `002_4` and builds a clean,
integrated cycle-level dataset through three layers.

**Bronze (`01_clean_and_validate.py`)**  
Reads each Excel sheet, validates the 9 required columns, and applies 22 quality checks
per measurement row:
- Timestamp issues (gaps, reversals, repeated values)
- Voltage and current out of specification
- Counter resets and decreases within a phase
- Exact duplicate rows
- Cycle-index jumps or decreases

Every row gets a `row_quality_status` of REJECTED, FLAGGED, or OK, plus a
`quality_flags` string listing every triggered check. Nothing is silently dropped —
rejected rows are retained in the output for traceability.

**Silver (`02_silver_transform.py`)**  
Assigns a phase label (charge, discharge, rest) to each row based on the sign of the
current. Checks that phase boundaries and counters are consistent within each cycle.

**Gold (`03_build_cycle_features.py`)**  
Trapezoidal integration within valid phase intervals (same phase, 0 < dt ≤ 5 s, no
artifact). Calendar-clock reversals are flagged, but do not veto otherwise valid
test-clock intervals. Computes per-cycle:
- `Discharge_Capacity_Ah`, `Charge_Capacity_Ah`
- `Coulombic_Efficiency_pct` (discharge / charge × 100)
- `Discharge_Energy_Wh`, `Cycle_Duration_s`, C-rate (mean and P99)
- `Computationally_Complete` and `Discharge_Integration_Valid` flags

### Key outputs

| File | What it contains |
|---|---|
| `outputs/02_silver_phase_data/*_silver.parquet` | Phase-annotated measurement rows |
| `outputs/03_gold_cycle_features/battery_cycle_features_gold.parquet` | Cycle-level features — primary table for all downstream tasks |
| `outputs/03_gold_cycle_features/battery_cycle_features_gold.csv` | CSV copy of Gold |

---

## Task 2 — Degradation Modeling

**Folder:** `task2_degradation_modeling/`  
**Entry:** `task2_degradation_modeling.py`  
**Depends on:** Task 1 Gold parquet + Silver parquet files.

### What it does

Fits four capacity-fade models to cycles 2–100 of each cell, compares them on a
chronological split, and extracts differential-voltage signatures.

**Stage 04 — Capacity fade fitting (`stage_04_fit_capacity_fade.py`)**  
Uses `n = Cycle_Index − 2` and `t_days` from the Silver timestamps.

Four models:

| Model | Equation | Nonlinear parameter range |
|---|---|---|
| Linear | Q = q₀ − a·n | — |
| Exponential | Q = q₀·exp(−k·n) | k ∈ [0, 0.2] |
| Square-root time | Q = q₀ − a·√t | — |
| Power law | Q = q₀ − a·nᵇ | b ∈ [0.05, 2] |

Fitting: q₀ and a are found in closed form via profile least squares; nonlinear
exponents (k, b) are found by dense grid search with five iterative refinements. All
parameters constrained non-negative.

Chronological split: train on cycles 2–70, validate on 71–85, refit on 2–85, test on
86–100. The winner is selected by validation RMSE (Square-root time excluded because it
uses future timestamps).

**Stage 05 — Model comparison (`05_compare_capacity_models.py`)**  
Compares an exponential fit, physics-constrained phenomenological surrogate, Random
Forest and LSTM forecasts with a fixed-origin persistence baseline on the same split.

**Stage 06 — Differential voltage (`06_differential_voltage.py`)**  
Selects representative cycles (2, 10, 25, 50, 75, 100). Integrates current → Q,
interpolates V(Q) onto 301 points, smooths with three Savitzky-Golay windows (11, 21,
31 pts), detects interior dV/dQ peaks (10–90 % of Q range). A peak is considered
"stable" only if it appears in all three smoothing windows and in a neighbouring cycle.

### Key outputs

| File | What it contains |
|---|---|
| `outputs/04_capacity_fade/cycle_capacity_analysis.csv` | 198-row master table: all cycle features plus fitted fade rates |
| `outputs/04_capacity_fade/model_parameters.csv` | Fitted parameters for every model and scope |
| `outputs/04_capacity_fade/evaluation_metrics.csv` | MAE, RMSE, R² per model and scope |
| `outputs/04_capacity_fade/predictions.csv` | Per-cycle model predictions |
| `outputs/06_differential_voltage/feature_cycle_summary.csv` | dV/dQ candidate summary (read by Task 6) |

---

## Task 3 — Anomaly Detection

**Folder:** `task3_anomaly_detection/`  
**Entry:** `task3_anomaly_detection.py`  
**Depends on:** Task 1 Gold data and Task 2 model-fitting functions.

### What it does

Flags unusual cycles using three complementary methods. All results are review
candidates — not confirmed faults.

**Script: `07_detect_battery_anomalies.py`**

1. **Exponential residuals** — fits Q = q₀·exp(−k·n) to the full history; computes
   `Capacity_Residual_Ah = observed − fitted`; flags cycles where the robust z-score
   exceeds 3.

2. **Local deviation** — compares each cycle to the mean of its two neighbours:
   `Local_Deviation_Ah = Q_n − (Q_{n−1} + Q_{n+1}) / 2`. Flags cycles where the
   local z-score exceeds 3. First and last cycles cannot be scored.

3. **Trend candidate** — a cycle must trigger both the exponential flag AND the local
   flag simultaneously. Neither cell produced any trend candidates.

4. **DBSCAN clustering** — builds three robustly scaled features (detrended residual,
   change deviation, CE deviation) and clusters with DBSCAN (eps=0.8, min_samples=5).
   Label −1 means anomalous noise. Sensitive to parameter choice.

### Key outputs

| File | What it contains |
|---|---|
| `outputs/07_anomaly_detection/anomaly_features.csv` | Per-cycle table with scores, flags, and DBSCAN labels |
| `outputs/07_anomaly_detection/anomaly_summary.csv` | Per-cycle decisions and review reasons |
| `outputs/07_anomaly_detection/dbscan_labels.csv` | Per-cycle DBSCAN labels (read by Task 6) |

---

## Task 4 — RUL Estimation

**Folder:** `task4_rul_estimation/`  
**Entry:** `task4_rul_estimation.py`  
**Depends on:** Task 2 `cycle_capacity_analysis.csv`.

### What it does

Forecasts remaining useful life (RUL) from early cycle history using three model
families at four predeclared checkpoints (cycles 5, 8, 10, 12).

EOL definition: first cycle where discharge capacity falls strictly below 80 % of the
cell's own cycle-2 discharge capacity. RUL = predicted EOL − checkpoint.

**Stage 08 — Individual curve RUL (`stage_08_individual_curve_rul.py`)**  
At each checkpoint, fits all four fade models to the history available up to that cycle
and extrapolates the curve to the first predicted EOL crossing. If no crossing occurs
within 1,000 cycles the attempt is recorded as a failure.

**Stage 09 — XGBoost RUL (`stage_09_estimate_rul_xgboost_shared.py`)**  
Pools both cells. Features: last 3 discharge capacities, last/mean cycle-to-cycle
changes, cycles since BOL. Trains a shared XGBoost regressor at each checkpoint and
iterates predicted capacity changes forward until the threshold is crossed.

**Stage 10 — LSTM RUL (`stage_10_estimate_rul_lstm_minimal.py`)**  
Minimal shared LSTM (1 hidden unit). Sliding windows of size 1 or 3. Three seeds (42,
7, 123). Normalises each cell's capacity by its own cycle-2 value. Iterative
multi-step forecast; horizon 1,000 cycles.

**Stage 11 — Comparison (`11_build_common_checkpoint_comparison.py`)**  
Normalises all predictions to a common schema. Primary fair comparison: checkpoints 8
and 10 for four methods (Linear, Exponential, XGBoost, LSTM window=3). Reports MAE,
bias, and coverage (fraction of attempts that produced a valid prediction).

### Key outputs

| File | What it contains |
|---|---|
| `outputs/08_rul_individual_curves/predictions.csv` | Curve RUL forecasts |
| `outputs/09_rul_xgboost/predictions.csv` | XGBoost forecasts |
| `outputs/10_rul_lstm/predictions.csv` | LSTM forecasts (all seeds and windows) |
| `outputs/11_rul_model_comparison/all_method_common_metrics.csv` | Full comparison table (read by Task 6) |
| `outputs/11_rul_model_comparison/all_attempts.csv` | Every attempted prediction |

---

## Task 5 — Pack Scaling

**Folder:** `task5_pack_scaling/`  
**Entry:** `task5_pack_scaling.py`  
**Depends on:** Task 2 `cycle_capacity_analysis.csv`.

### What it does

Runs a Monte Carlo simulation of a synthetic 12S2P pack (4 series groups × 2 parallel
cells × 3 modules = 24 cells) using cell parameters extracted from the real data, plus
assumed manufacturing variation, temperature gradients, and balancing parameters.

**Script: `stage_13_scale_module_pack.py`**

1. Fits an exponential model to cycles ≤ 8 of each cell to get an illustrative cell-based scenario baseline
   (cycle-2 delivered capacity q₀ and fade rate k); two cells do not establish a population distribution.

2. Draws 100 ensemble samples for all 24 cell positions from lognormal distributions
   centred on q₀ (CV=3 %) and k (CV=15 %).

3. Applies a linear 0–10 K spatial temperature gradient across all cell positions via
   an Arrhenius factor (Ea=20,000 J/mol — assumed, not measured).

4. Assigns random SOC deficits before simulating three balancing strategies (none,
   passive resistive, active charge-transfer).

5. Computes pack capacity at each cycle using the topology envelope:
   - Within each series group: sum the parallel-cell capacities × SOC
   - Within each module: take the minimum group capacity
   - Across the pack: take the minimum module capacity
   
   This correctly models the weakest-group constraint. Pack EOL ≠ earliest individual
   cell EOL (a parallel partner partially compensates a weak cell within its group).

6. Records the first cycle below 80% of an ideal, fully charged identical-cell 2P
   reference (2 × cycle-2 delivered capacity). This is not each simulated pack’s own
   initial accessible capacity.

The methodology document (`outputs/13_pack_scaling/pack_scaling_methodology.md`)
explains the full proposed scaling approach including module-level intermediate steps,
pack-level RUL propagation, degradation mode interactions, and the accuracy vs.
scalability trade-off.

### Key outputs

| File | What it contains |
|---|---|
| `outputs/13_pack_scaling/scenario_summary.csv` | Mean/min/max EOL and balance loss per scenario (read by Task 6) |
| `outputs/13_pack_scaling/scenario_samples.csv` | Per-sample EOL for all 100 ensemble members |
| `outputs/13_pack_scaling/scenario_retention.png` | Retention curves for all four scenarios |
| `outputs/13_pack_scaling/assumptions.json` | All CONFIG values + source hash + interpretation note |
| `outputs/13_pack_scaling/pack_scaling_methodology.md` | Full methodology document (§A–G) |

---

## Task 6 — Reporting and Visualization

**Folder:** `task6_reporting/`  
**Entry:** `task6_report_and_visualizations.py`  
**Depends on:** Tasks 1–5 (reads saved CSVs from every earlier task).

### What it does

Reads saved results (no model retraining) and produces five figures, including the
four requested plots, plus a five-page PDF technical report.

**Stage 14 — Figures (`14_build_task6_visualizations.py`)**

| Figure | What it shows |
|---|---|
| `01_capacity_predictive_curves` | Measured discharge Ah + 4 model curves + 80 % threshold + observed EOL |
| `02_coulombic_efficiency` | CE % per cycle; flagged cycles > 100 % annotated |
| `03_deviation_clusters` | DBSCAN feature scatter (top) + flagged cycles on trajectory (bottom) |
| `04_forecasted_rul_distribution` | LSTM seed histogram + XGBoost + actual RUL at checkpoint 8 |
| `05_all_rul_models_checkpoints` | All 7 methods at checkpoints 5/8/10/12 |

**Report builder (`build_six_task_report.py`)**  
Builds a five-page A4 PDF with ReportLab. Page count is enforced: the script raises
`RuntimeError` if the output is not exactly 5 pages, so adding content requires careful
size budgeting.

| Page | Content |
|---|---|
| 1 | Data engineering — Bronze/Silver/Gold method, EOL table, capacity decline |
| 2 | Capacity fade figures, CE figure, winning model RMSE |
| 3 | Anomaly cluster figure, dV/dQ method and results |
| 4 | RUL distribution figure, method comparison table (MAE, bias, coverage) |
| 5 | Pack scaling table, fleet analytics, §D/E/F methodology extensions, limitations |

### Key outputs

| File | What it contains |
|---|---|
| `outputs/14_reporting_visualization/01–05_*.png/.pdf` | Figures in both formats |
| `outputs/Technical_Report.pdf` | Five-page technical report |
| `outputs/14_reporting_visualization/visualization_manifest.json` | SHA-256 provenance of every source file |

---

## Utilities

**Folder:** `utilities/`  
These scripts are helpers — they are not part of the analysis pipeline and are not
called by `run_six_tasks.py`.

| Script | What it does |
|---|---|
| `run_with_report.py` | Wraps any script: captures stdout, records changed files, previews CSVs, writes a Markdown execution report to `outputs/execution_reports/`. Use this to log a single-stage run. |
| `package_submission.py` | Collects all required files into a `.zip` for submission, writing a manifest. |
| `validate_submission_integrity.py` | Checks workspace files against the historical submission manifest; it does not validate the current scientific analysis. |

---

## How tasks share data

Each task writes to its own `outputs/` folder. Some scripts use `output_paths.py` to
resolve an output group; others reference task paths directly.

```python
# Example — how Task 4 reads Task 2's output
from output_paths import TaskOutputs
OUT = TaskOutputs()
df = pd.read_csv(OUT / "04_capacity_fade/cycle_capacity_analysis.csv")
```

The map is defined in `scripts/output_paths.py`. Renaming a task folder also requires
updating scripts and documentation that reference that folder directly.

---

## Dependency chain

```
Task 1 ──► battery_cycle_features_gold.parquet
              │
              ▼
Task 2 ──► cycle_capacity_analysis.csv ──────────────────► Task 4
         ► evaluation_metrics.csv                           │
         ► feature_cycle_summary.csv ──────────────────────►│
         ► feature_candidates_by_cycle.png ────────────────►│
              │                                             │
              ▼                                             │
Task 3 ──► anomaly_features.csv ──────────────────────────►│
         ► dbscan_labels.csv ─────────────────────────────►│
                                                           │
              │◄──────────────────────────────────────────►│
              │                                             │
              │          Task 2 CSV ◄──────── Task 5 ──► scenario_summary.csv
              │                                             │
              └─────────────────────────────────────────► Task 6
                                                        Technical_Report.pdf
```

---

## Common problems

**"ModuleNotFoundError: No module named X"**  
Run from the project root, not from inside a task folder. All scripts add the right
`sys.path` entries when run via `run_six_tasks.py` or directly from the root.

**"FileNotFoundError: ...battery_cycle_features_gold.parquet"**  
Task 1 has not been run yet, or it failed partway through. Run `--task 1` first.

**"assert len(g)==99" crashes Task 2**  
The Gold table does not have exactly 99 valid cycles for one of the cells. Re-run
Task 1 and check the Bronze/Gold quality report for rejected rows.

**"RuntimeError: Expected 5 pages, got 6" in Task 6**  
Text added to the report builder pushed it over 5 pages. Reduce font size, remove a
paragraph, or shorten a table in `build_six_task_report.py`.

**Task 5 "FileNotFoundError: stage_08_individual_curve_rul.py not found"**  
Check that the Task 4 stage 08 source file exists in `task4_rul_estimation/`; Task 5
imports its `INPUT` path constant. Also run Task 2 first so the referenced CSV exists.
