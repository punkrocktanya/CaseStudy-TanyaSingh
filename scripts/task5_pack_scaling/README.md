# Task 5: Module and pack scaling

Explore illustrative 12S2P scenarios for cell-to-cell variation, temperature gradients and balancing, and discuss the computational trade-offs.

## Run

From the project root:

```bash
python scripts/task5_pack_scaling/task5_pack_scaling.py
```

Run Tasks 1 and 2 first. Pack scenarios use assumptions and are not validated measurements.

This entry point runs the implementation files in this folder in order and stops on an error. Its authoritative results, plots and intermediate files are written directly to this folder’s `outputs/`. Some large preprocessing intermediates are kept locally and excluded from Git.

## Implementation

- [stage_13_scale_module_pack.py](stage_13_scale_module_pack.py)

## Results and plots

- [outputs/13_pack_scaling/](outputs/13_pack_scaling/)

`test_pack_scaling.py` tests the pack-envelope logic.
