# Battery cleaning (Bronze)

- **Input:** the two original LR1865SZ Excel files. They are preserved unchanged.
- **Raw columns kept:** `Data_Point`, `Test_Time(s)`, `Current(A)`, `Capacity(Ah)`, `Voltage(V)`, `Energy(Wh)`, `Temperature(℃)`, `Date_Time`, and `Cycle_Index`.
- **Steps:** timestamps were parsed, rows were standardised, units/signs were retained, and quality flags were calculated. Measurement rows are retained in Parquet; flags are not silently deleted.
- **Reduced Excel:** `analysis_ready_minimal.xlsx` contains only the nine required measurement columns, split into one sheet per cell.
- **Important anomaly:** missing temperature values are observed in the source; they are reported, not invented.

## Outputs

- `*_clean.parquet`: cleaned measurement tables.
- `cleaning_manifest.json`: input/output hashes and row policy.
- `01_timestamp_normalized.xlsx`: timestamp-normalisation review workbook.
