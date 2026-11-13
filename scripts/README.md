# Six-task analysis scripts

Run from the project root after installing `requirements.txt`.

```bash
python scripts/run_six_tasks.py              # Tasks 1–6 in order
python scripts/run_six_tasks.py --task 3     # one task; earlier outputs required
python -m unittest discover -s scripts -p "test_*.py"
```

The [project README](../README.md) maps each task to its scripts, output folders, required inputs and limitations. Task 1 reads the two raw Excel workbooks from the root, normalizes timestamps, cleans and classifies rows, builds Silver phase data and integrates diagnostic Gold cycle features. Task 2 fits and evaluates fade models and performs differential-voltage analysis; Task 3 screens unusual cycles; Task 4 compares early RUL methods and records failed crossings; Task 5 performs synthetic pack sensitivity scenarios; Task 6 builds the requested figures and current five-page report.

If local `task1_preprocess.py` through `task6_report_and_visualizations.py` files are present, they are for reference only; they are a separate exploratory implementation, not the inputs to this runner. The root PDF is refreshed by the report builder; the historical submission manifest is not proof that a regenerated run is consistent. Do not interpret forecast seeds as a calibrated RUL distribution or synthetic pack scenarios as pack test measurements.
