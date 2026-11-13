# Merged submission - consistency validation

- Automated artifact checks: **69 PASS**, **0 FAIL**.
- Scientific caveats: **5** (not software errors).
- Source input cells: 001_2, 002_4; first relative EOL cycles: {'001_2': 13, '002_4': 24}.
- Models: individual curves, shared XGBoost, minimal LSTM.
- Fair RUL comparison: checkpoints 8 and 10, 44 attempts across all seven models (24 in the original four-method subset); 96 total attempts are documented.
- Raw Excel not included, so the raw-to-Gold pipeline was not re-executed in this audit.
- Parquet engine may be unavailable in some test environments; the original pipeline test can validate the equivalent saved Gold CSV if necessary.

See `consistency_checks.csv` for each check and `output/pdf/Battery_RUL_Limitations_and_Validation.pdf` for domain limitations.
