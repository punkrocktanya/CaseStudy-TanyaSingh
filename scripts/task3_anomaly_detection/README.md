# Task 3: Anomaly Detection

Screens cycles for anomalous capacity behaviour using exponential residuals, local
deviation scoring, and DBSCAN clustering. All results are review candidates, not
confirmed faults.

## Run

```bash
python scripts/task3_anomaly_detection/task3_anomaly_detection.py
```

## Method

**Step 1 — Exponential residuals**
Fits Q = q₀·exp(−k·n) to cycles 2–100 of each cell using the same `fit()` function as
Task 2 (n is passed as both cycle index and time, intentionally cycle-based here).
Computes `Capacity_Residual_Ah = observed − fitted`. Standardises residuals by their
robust scale (IQR); flags cycles where |z| > 3 as `Exponential_Flag`.

**Step 2 — Local deviation**
`Local_Deviation_Ah = Q_n − (Q_{n−1} + Q_{n+1})/2` — the signed gap between a cycle
and the mean of its neighbours. Flags cycles where |local_z| > 3 as `Local_Flag`.
Boundary cycles (first and last) cannot be scored.

**Step 3 — Trend candidate**
A cycle is a `Trend_Candidate` only when both `Exponential_Flag` AND `Local_Flag` are
set simultaneously. Neither cell produced any trend candidates.

**Step 4 — DBSCAN clustering**
Features: `Residual_Detrended_Ah` (residual minus 11-cycle rolling median),
`Change_Deviation_Pct` (cycle-to-cycle change minus rolling median), `CE_Deviation`
(deviation from median CE). Scaled with `RobustScaler`. Parameters: eps=0.8, min_samples=5.
Label −1 = noise (anomalous); other labels = clusters.

## Key results

| Cell | Exponential flags | Local flags | Trend candidates | DBSCAN noise cycles |
|---|---|---|---|---|
| 001_2 | 0 | 9 (cycles 4,5,6,8,9,10,12,26,27) | 0 | ~25 / 98 scored |
| 002_4 | 0 | 0 | 0 | ~45 / 98 scored |

- All 198 cycles have `Quality_Status=REVIEW` from upstream Gold flags.
- DBSCAN noise fraction is sensitive to eps: at eps=0.5 on 001_2, noise rises to 59/98.

## Outputs

| File | Description |
|---|---|
| `outputs/07_anomaly_detection/anomaly_features.csv` | 92-column per-cycle table with all scores and flags |
| `outputs/07_anomaly_detection/anomaly_summary.csv` | Per-cell summary counts |
| `outputs/07_anomaly_detection/dbscan_labels.csv` | Per-cycle DBSCAN labels |

## Limitations

- Local deviation cannot score the last cycle (no right neighbour); sudden end-of-life
  drops are invisible to the local scorer.
- A single unusual cycle will also flag its immediate neighbours via local deviation.
- DBSCAN results are highly sensitive to eps and min_samples; reported as a single
  configuration, not a stability study.
- All flags are unsupervised screening results with no ground-truth fault labels.
- `assert np.array_equal(g.Cycle_Index, np.arange(2, 101))` will crash if any cell
  has missing or out-of-range cycle indices.
