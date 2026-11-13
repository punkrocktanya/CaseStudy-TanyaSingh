# Silver Transformation Report

The two cleaned battery datasets were transformed without sorting, deleting, interpolating, clipping, or rounding source measurements.

## Configuration

- Rest-current deadband: ±0.05 A
- Sampling-gap threshold: 5.0 s using `Test_Time(s)`
- Charge-current screening limit: 2.4 A
- Discharge-current screening limit: 7.2 A
- Voltage screening window: 3.0–4.2 V

## LR1865SZ_cycles201217_001_2_clean.parquet

- Rows in / out: **126,648 / 126,648**
- Cycle range: **1–101** (101 observed)
- Phase segments: **401**
- Output: `LR1865SZ_cycles201217_001_2_silver.parquet`

### Phase rows

| Phase | Rows |
|---|---:|
| CHARGE | 32,148 |
| DISCHARGE | 32,896 |
| REST | 61,604 |
| UNKNOWN | 0 |

### Quality flags

| Flag | Rows |
|---|---:|
| Missing_Flag | 126,648 |
| Critical_Missing_Flag | 0 |
| Capacity_Missing_Flag | 0 |
| Energy_Missing_Flag | 0 |
| Temperature_Missing_Flag | 126,648 |
| Timestamp_Duplicate_Flag | 12,220 |
| Timestamp_Reversal_Flag | 25 |
| Test_Time_Reversal_Flag | 0 |
| Sampling_Gap_Flag | 0 |
| Current_Plausibility_Flag | 44,092 |
| Voltage_Plausibility_Flag | 135 |
| Capacity_Plausibility_Flag | 0 |
| Energy_Plausibility_Flag | 0 |

### Current-sign evidence

- Positive-current-as-charge supported: **True**
- Median charge-segment voltage change: **0.39354999999999984 V**
- Median discharge-segment voltage change: **-0.5891499999999998 V**

### Validation

| Check | Result |
|---|---|
| row_count_preserved | PASS |
| row_order_preserved | PASS |
| all_original_measurements_preserved | PASS |
| phase_values_valid | PASS |
| phase_ids_consecutive | PASS |
| one_phase_per_phase_id | PASS |
| phase_transition_count_matches_segments | PASS |
| cycle_index_preserved | PASS |
| temperature_missing_not_filled | PASS |

## LR1865SZ_cycles201214_002_4_clean.parquet

- Rows in / out: **202,516 / 202,516**
- Cycle range: **1–101** (101 observed)
- Phase segments: **401**
- Output: `LR1865SZ_cycles201214_002_4_silver.parquet`

### Phase rows

| Phase | Rows |
|---|---:|
| CHARGE | 70,172 |
| DISCHARGE | 70,939 |
| REST | 61,405 |
| UNKNOWN | 0 |

### Quality flags

| Flag | Rows |
|---|---:|
| Missing_Flag | 202,516 |
| Critical_Missing_Flag | 0 |
| Capacity_Missing_Flag | 0 |
| Energy_Missing_Flag | 0 |
| Temperature_Missing_Flag | 202,516 |
| Timestamp_Duplicate_Flag | 28,364 |
| Timestamp_Reversal_Flag | 29 |
| Test_Time_Reversal_Flag | 0 |
| Sampling_Gap_Flag | 0 |
| Current_Plausibility_Flag | 70,172 |
| Voltage_Plausibility_Flag | 121 |
| Capacity_Plausibility_Flag | 0 |
| Energy_Plausibility_Flag | 0 |

### Current-sign evidence

- Positive-current-as-charge supported: **True**
- Median charge-segment voltage change: **0.4817500000000001 V**
- Median discharge-segment voltage change: **-0.7110000000000001 V**

### Validation

| Check | Result |
|---|---|
| row_count_preserved | PASS |
| row_order_preserved | PASS |
| all_original_measurements_preserved | PASS |
| phase_values_valid | PASS |
| phase_ids_consecutive | PASS |
| one_phase_per_phase_id | PASS |
| phase_transition_count_matches_segments | PASS |
| cycle_index_preserved | PASS |
| temperature_missing_not_filled | PASS |

## Assumptions and cautions

- Positive current is classified as charge and negative current as discharge, with voltage-direction evidence reported above.
- Repeated and reversed timestamps are retained. `Test_Time(s)` remains the primary elapsed-time axis.
- Missing temperature remains null and is explicitly flagged; no temperature values were invented.
- Plausibility flags are screening indicators, not automatic deletion criteria.
