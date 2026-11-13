# Silver transformation

- Silver reads the cleaned Parquet files and applies a consistent phase rule: positive current = charge, negative current = discharge, and values near zero = rest.
- A `Phase_ID` is created so integration never crosses a charge/discharge/rest boundary.
- Counter changes, timestamps, sign conventions, and phase transitions are reconciled. Suspicious rows remain available for review.
- No sudden current step is deleted: the switch into charging is abrupt, but the following current plateau is sustained and is treated as a real test condition.

## Outputs

- `*_silver.parquet`: row-level phase-labelled data.
- `silver_transformation_report.md` and `silver_transformation_summary.json`: counts and checks.
