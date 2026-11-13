# Scripts organized by case-study task

Each task folder contains a runnable entry script, a README explaining its logic and prerequisites, and an `outputs/` folder with results and plots. Start at the [project README](../README.md) for the six commands and limitations.

The task entry scripts call the validated implementation stages stored alongside them in their respective task folders; they do not maintain separate copies of model logic. Each task writes its authoritative working results directly to its own `outputs/` folder. Large preprocessing intermediate workbooks and interval diagnostics remain local and are excluded from Git.

Run all six tasks using `python scripts/run_six_tasks.py`. The scientific limitations, including relative rather than verified nominal RUL and uncalibrated pack scenarios, apply to all task outputs.
