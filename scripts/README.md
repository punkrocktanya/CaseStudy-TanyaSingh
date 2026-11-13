# Scripts organized by case-study task

Each task folder contains a runnable entry script, a README explaining its logic and prerequisites, and an `outputs/` folder with results and plots. Start at the [project README](../README.md) for the six commands and limitations.

The task entry scripts call the validated implementation stages stored alongside them in their respective task folders; they do not maintain separate copies of model logic. Authoritative working results are in `scripts/outputs/`, and each entry point refreshes that task folder's review copies after the task succeeds. Large intermediate workbooks and interval diagnostic files are left in the working output directories rather than duplicated.

Run all six tasks using `python scripts/run_six_tasks.py`. The scientific limitations, including relative rather than verified nominal RUL and uncalibrated pack scenarios, apply to all copied outputs.
