# Capacity-fade modelling (Step 2)

- Input is Gold cycle capacity plus Silver discharge-completion time.
- Modelling uses complete cycles 2–100 (99 cycles per cell); cycle 1 and incomplete/out-of-range cycles are not used.
- Models fitted: linear `Q=a+bn`, exponential `Q=A exp(-kn)`, square-root time `Q=q0-k√t`, and power law `Q=q0-a n^b`.
- Metrics are MAE, RMSE, R², and negative-prediction count. A persistence baseline is included.
- Full-series fits are descriptive. Test forecasts expose late-cycle bias: exponential underpredicts all 15 late 001_2 cycles, while persistence is better there.
- Power-law sensitivity is dominated by whether cycle 2 is included; excluding only later CE-flagged cycles changes the curve only slightly.
- Square-root free intercepts start above the first measured capacity, so they must not be interpreted as a physical initial capacity. The time fit is retrospective because future completion timestamps are used.
- Added fade-rate analysis: `ΔQ_n = Q_n − Q_(n−1)`. The report stores both signed change and positive loss (`−ΔQ`) plus a centred 7-cycle rolling mean. `capacity_fade_rate_001_2.png` and `capacity_fade_rate_002_4.png` show the raw cycle changes and smoothed trend.

See the CSV metrics, PNG plots, `capacity_fade_report.md`, and follow-up model review files.
