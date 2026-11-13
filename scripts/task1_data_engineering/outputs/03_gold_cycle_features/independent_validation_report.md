# Battery pipeline corrective-action report

- **Result:** The code checks have been strengthened. The results remain a diagnostic dataset.
- Original files and the previous results are preserved in `scripts/outputs/validation_baseline_20261111`.
- Gold now reads Silver and keeps its source row IDs, phase IDs, and cycle membership.
- Repeated test times are counted separately. They represent zero elapsed time, not automatically lost charge.
- Calendar-clock reversals are warnings. A valid test-clock interval is no longer discarded just because the calendar clock goes backwards.
- Every source row has an interval diagnostic with its previous row ID, clocks, flags, and integration decision.
- Coverage and counter comparisons are saved for each cycle. Negative counter jumps remain visible; they are not silently repaired.
- Diagnostic efficiency is separate from protocol-verified efficiency. Efficiencies above 100% are flagged and kept unchanged.
- Duration now explicitly separates the test-time span, integrated seconds, boundary time, and long gaps.
- No raw measurements were sorted, deleted, interpolated, clipped, or replaced.

**Most useful finding**

- The **13,858** previously excluded within-phase intervals have zero elapsed test time.
- No positive within-phase time was lost in these files. Coverage is 100% on that defined basis; this does not prove the physical protocol was complete.
- Phase/cycle boundary intervals are kept separate from within-phase coverage.
- The rebuilt metrics match the baseline apart from floating-point rounding.
- The largest before/after change in efficiency is not available.
- The important changes are traceability, measured coverage, and stricter quality labels.

**Dataset 001_2**

- Source, cleaned, and Silver measurement rows reconciled: **126,648**.
- Gold cycles: **101**; **99 need review** and **2 have incomplete/invalid pairs**.
- Lowest charge/discharge time coverage: **100.000000%**.
- Omitted positive within-phase time: **0.000000 seconds**.
- Zero-time intervals: **5,394**.
- Calendar reversals in source order: **25**.
- Cycles above the efficiency review threshold: **[2, 63, 87, 89, 93]**.
- Counter negative jumps: **0**.
- Largest capacity/energy counter difference: **0.624199%**.
- Typical diagnostic efficiency: **99.1078%**.
- Typical mean charge C-rate: **2.879083C**.

- Adjacent rows with an unchanged calendar timestamp but increasing test time: **5,076** in this replay. The supplied PDF lists **3,610**; that figure was not reproduced.
- This count uses original source order and the rule: calendar-time difference equals zero AND test-time difference is positive. Current source hashes are saved in the manifest.

- Cycle 2 efficiency: **100.523790%** from integration and **100.531915%** from positive counter increments. Both remain diagnostic values.

- Discharge capacity from cycle 2 to 100: **1.511447 to 0.269956 Ah** by integration; **1.512000 to 0.269000 Ah** by counters.
- The counters support the declining measured capacity trend. Its physical cause and SOH interpretation remain unverified.

**Dataset 002_4**

- Source, cleaned, and Silver measurement rows reconciled: **202,516**.
- Gold cycles: **101**; **99 need review** and **2 have incomplete/invalid pairs**.
- Lowest charge/discharge time coverage: **100.000000%**.
- Omitted positive within-phase time: **0.000000 seconds**.
- Zero-time intervals: **8,464**.
- Calendar reversals in source order: **29**.
- Cycles above the efficiency review threshold: **[2]**.
- Counter negative jumps: **0**.
- Largest capacity/energy counter difference: **0.256801%**.
- Typical diagnostic efficiency: **99.2582%**.
- Typical mean charge C-rate: **1.922750C**.

- Adjacent rows with an unchanged calendar timestamp but increasing test time: **12,318** in this replay. The supplied PDF lists **4,830**; that figure was not reproduced.
- This count uses original source order and the rule: calendar-time difference equals zero AND test-time difference is positive. Current source hashes are saved in the manifest.

- Cycle 2 efficiency: **100.958554%** from integration and **100.897129%** from positive counter increments. Both remain diagnostic values.

- Discharge capacity from cycle 2 to 100: **1.687755 to 0.452649 Ah** by integration; **1.687000 to 0.453000 Ah** by counters.
- The counters support the declining measured capacity trend. Its physical cause and SOH interpretation remain unverified.

**Audit action status**

- **G01 / G03 / G07 / G08 - implemented:** phase coverage, zero-time separation, severity-based quality, boundary-gap accounting, elapsed and integrated duration fields.
- **G02 / R01 - implemented and replayed:** Gold reads Silver; row order, measurements, phase IDs, cycle membership and file hashes are checked.
- **T01 - implemented:** calendar warnings are separate from test-clock integration. No negative test-clock steps or long gaps were found in these source files.
- **G04 - implemented with evidence pending:** partial edges, computational completeness, endpoint checks, and protocol verification are separate fields. Full protocol verification is false.
- **G05 / G06 - diagnostics implemented:** named-cycle review, unclamped efficiency flags, counter increments, negative-jump detection, and per-phase comparisons. Instrument semantics and calibrated uncertainty remain pending.
- **P01 / V01 - partial:** active Silver/Gold thresholds and core cleaning thresholds use a versioned configuration. Current-limit flags are recommendations, not physics-impossibility claims. Controlled datasheet/protocol confirmation remains pending.
- **B01 - implemented:** elapsed-time parser edge tests, configurable raw paths, source hashes and normalization manifest. Source workbook copies preserve original time strings.
- **S01 - deferred deliberately:** exact Silver segmentation is preserved and sign is checked against voltage trends. Hysteresis/dwell changes need the pulse protocol.
- **D01 - recorded:** temperature is unavailable and is never filled with an assumed value.
- Regression checks are in `test_battery_validated_pipeline.py`; run `python -m unittest test_battery_validated_pipeline -v`.

**What still needs evidence**

- Exact cycling protocol, stop conditions, phase pairing rules, and the original instrument model/calibration.
- A controlled cell datasheet and confirmation of the 2.5 Ah capacity basis and recommended current limits.
- Confirmation of what the instrument capacity/energy counters mean and an uncertainty-based reconciliation tolerance.
- A reference performance test before calculating SOH or treating capacity changes as confirmed degradation.
- Measured temperature logs for any temperature-dependent analysis. Missing temperature has not been filled.
- Sign/dwell/hysteresis changes are deferred until the pulse protocol is known; Silver phase labels are preserved exactly.
- The coverage threshold (99.5%), existing counter tolerance (5%), and >100% efficiency review trigger are processing conventions, not instrument accuracy claims.
- All protocol-unverified cycles stay REVIEW or FAIL. No cycle is certified for SOH training.

**Files to inspect**

- `battery_cycle_features_gold.parquet` and `.csv`: revised cycle metrics and quality flags.
- `interval_diagnostics_*.parquet`: source-pair coverage, counter deltas, and exclusion reasons.
- `phase_counter_audit.csv`: phase-level counter reconciliation.
- `phase_coverage_audit.csv`: phase-level time budgets and excluded interval counts by reason.
- `named_anomaly_review.csv`: both cycle-2 cases, the other efficiencies above 100%, and partial boundary cycles.
- `baseline_comparison.csv`: before/after metrics for every cycle.
- `validation_manifest.json`: source/configuration/code hashes, measurement reconciliation, active settings, and release limits.
