# Battery degradation analysis

This exploratory study examines two cells using cycle data, capacity-fade models, anomaly screening, relative remaining useful life (RUL), and illustrative module and pack scaling. The five-page report is [Technical_Report.pdf](Technical_Report.pdf).

## Repository contents

- [scripts/](scripts/) contains the Python analysis and tests; see the [scripts guide](scripts/README.md) for the analysis run order.
- [scripts/outputs/](scripts/outputs/) contains processed Silver and Gold data, saved results, figures, and experiment manifests.
- Two source Excel workbooks are included in the repository root. The saved analysis can be reviewed using the processed data; review the preprocessing scripts and their configuration before regenerating data from the workbooks.

## Install and check

From the project root, using Python 3.11 or later:

```bash
python -m pip install -r requirements.txt
python scripts/validate_submission_integrity.py
python -m unittest discover -s scripts -p "test_*.py"
```

The integrity check compares packaged files against [SUBMISSION_MANIFEST.json](SUBMISSION_MANIFEST.json) and checks Python syntax. Run it before modifying packaged files or outputs. A passing check does not validate the scientific conclusions. Individual model and visualization manifests retain historical source hashes as experiment provenance; they do not attest to the relocated scripts.

## Interpretation and limitations

The exploratory end-of-life threshold is 80% of each cell's cycle-2 delivered capacity; it is not verified nominal state of health. Temperature is missing, and only two cells were tested at different currents. Module and pack results are illustrative or proposed, not validated pack performance.

## GitHub Actions

The **Tests** workflow runs on pushes and pull requests. It installs CPU-only PyTorch, checks submission integrity, and runs the unit tests. The workflow has passed on the `main` branch.

The **Full analysis and report** workflow can be started manually from the Actions tab. It uses the packaged processed data and is configured to upload execution records, figures, and generated PDFs as a workflow artifact. It does not commit regenerated outputs or replace the root report. The full analysis workflow has not yet been run on GitHub, so its completion and artifacts are not yet verified there. See the [scripts guide](scripts/README.md) for local analysis and report-generation commands.

## Output folders

The numbered folders in `scripts/outputs/` follow the review process: data cleaning, Silver and Gold data, capacity and voltage analysis, anomaly screening, RUL models and comparisons, pack scaling, reporting, and consistency validation. The analyses are not all sequential; several independently use the Silver or Gold data. Historical experiment manifests preserve the paths and hashes recorded when those experiments were run.
