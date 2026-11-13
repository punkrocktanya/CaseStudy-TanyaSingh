# Gold cycle features

Gold contains one row per cycle and cell for modelling.

- Capacity is integrated with the trapezoidal rule: `Q = Σ 0.5*(Iᵢ+Iᵢ₊₁)*Δt/3600`.
- Coulombic efficiency is `100 × discharge capacity / charge capacity`.
- C-rate is `|current| / rated capacity`; charge/discharge duration is the elapsed phase time.
- Energy throughput per cycle is charge energy plus discharge energy (absolute discharge energy).
- Counter-based increments are retained beside independently integrated values.
- `Cycle_Status`/`Quality_Status` distinguish complete cycles, review cases, and failures; flags are diagnostic, not silent exclusions.

## Main anomalies

- Six cycles have integrated CE above 100%: 001_2 cycles 2, 63, 87, 89, 93 and 002_4 cycle 2. They are explained by small charge/discharge integration and counter differences, not by deleting the cycles automatically.
- Absolute SOC is unavailable from the files, so SOC is discussed only through relative charge balance and rest-voltage checks.
- The current transition is sudden but the plateau is sustained. It is an observed accelerated-aging condition, not evidence of random impulse noise.
- Delivered capacity falls about 82.1% for 001_2 and 73.2% for 002_4 from cycle 2 to cycle 100. This is consistent with a combination of irreversible ageing and high-current polarisation; the data alone cannot uniquely separate the two.

## Outputs

`battery_cycle_features_gold.parquet/csv`, coverage and counter audits, anomaly review, validation manifest, and corrective-action reports.
