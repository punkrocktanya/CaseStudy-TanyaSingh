# Task 5: Module and pack scaling

Explore illustrative 12S2P scenarios for cell-to-cell variation, temperature gradients and balancing, and discuss the computational trade-offs.

## Run

From the project root:

```bash
python scripts/task5_pack_scaling/task5_pack_scaling.py
```

Run Tasks 1 and 2 first. Pack scenarios use assumptions and are not validated measurements.

This entry point runs the validated pipeline stages below in order and then copies their reviewable results into this folder. It stops on an error. The authoritative working outputs remain in `scripts/outputs/`; copies are refreshed only when this task runs. Intermediate Excel workbooks, cleaned Parquet files and per-row interval diagnostics are omitted from the copies to avoid duplicating large files.

## Implementation

- [stage_13_scale_module_pack.py](../stage_13_scale_module_pack.py)

## Results and plots

- [outputs/13_pack_scaling/](outputs/13_pack_scaling/)
