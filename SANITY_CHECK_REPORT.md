> **Local correction update:** The four requested documentation/report corrections have since been applied locally: pack EOL uses the topology envelope, the ideal identical-cell reference is explicit, the current temperature-gradient differences are 1.14 and 2.54 cycles, and the report now uses a 0.05 A deadband and relative EOL cycles 13 and 24. The validation R² label and square-root-cycle/time distinction have also been corrected. The report was regenerated as five pages and 35 tests passed. The historical observations below record the earlier audited revision; see the correction update above before interpreting them.

> **Local recheck after audit:** At the time of the recheck, the Task 5 simulation, entry point and tests had been restored locally. An isolated Task 5 → Task 6 run passed, and the regenerated Task 5 summary exactly matched the saved local summary. The audited commit `9858bf6` did not contain the simulation. The original findings below describe that committed revision; see the recheck section at the end for remaining local issues.

# Sanity, code and dependency audit — battery case study

**Audited branch:** `codex/six-task-validation`
**Audited commit:** `9858bf6191e7719e70db4987263f87beb8af93f8`
**Scope:** Task 1–6 scripts, saved outputs, notebook, five-page technical report, README, tests and GitHub configuration. The audit is observational: it does not alter the analysis or restore removed files.

## Overall result

**Not ready for an end-to-end submission.** The normal pipeline stops at Task 5 because its simulation script is missing. The report can display an existing Task 5 summary, but the current branch cannot regenerate that summary. The current technical report also contains demonstrable numerical and methodological inconsistencies. All 30 currently discoverable tests pass, but they do not include the removed pack-scaling tests or exercise the complete pipeline.

## Dependency map

```text
Source Excel workbooks
  → Task 1 normalization / cleaning → Silver measurement and phase data
  → Task 1 validated Gold per-cycle features
       ├→ Task 2 capacity fade and comparisons → cycle capacity / model CSVs
       │     └→ Task 4 extrapolation, shared XGBoost, LSTM → comparison CSVs
       ├→ Task 2 differential-voltage analysis (uses Silver traces)
       └→ Task 3 residual and DBSCAN screening (Gold, plus Task 2 model functions)
  → Task 5 pack scaling: intended to use Task 2 cell-capacity data; source script missing
  → Task 6: figures use Task 2–4 saved files; report also reads Gold, dV/dQ and
    the pre-existing Task 5 scenario summary. Normal orchestrated run stops before Task 6.
```

Dependencies are inputs, not claims of independent validation: Task 3 and Task 4 reuse upstream data, and Task 6 mostly summarizes earlier outputs. Tasks can sometimes run independently if saved prerequisites already exist; that does not prove a fresh end-to-end run works.

## Confirmed findings

### 1. Task 5 is missing, but the orchestrator and documentation still require it — critical

`scripts/run_six_tasks.py` invokes `scripts/task5_pack_scaling/stage_13_scale_module_pack.py`; that file, `task5_pack_scaling.py`, and the pack test were removed in commit `9858bf6`. Executing `python scripts/run_six_tasks.py --task 5` fails with a file-not-found error (the child exits 2 and the orchestrator exits 1). The Task 5 README still links to both missing scripts and describes running a 100-sample simulation. Because the full runner uses `check=True`, Task 5 stops the sequence and Task 6 is not reached.

`scenario_summary.csv` remains, and Task 6 reads it. Its figures are therefore historical saved scenario results, not a simulation reproducible from the current branch. The methodology document is a proposal and does not replace runnable code or the removed ensemble samples and trajectories. Restore and validate the simulation, or revise the runner, report and deliverables to clearly present Task 5 as a non-executable proposal; choose based on the intended submission.

### 2. Technical report contains conflicting endpoint and preprocessing claims — high

The saved Gold/fade data give cycle-2 delivered capacities of 1.511447 Ah and 1.687755 Ah. The first crossings of 80% of those values are **cycle 13 for 001_2 and cycle 24 for 002_4**. The report's opening table reflects these cycle indices, but its RUL limitations paragraph calls the actual EOL “11 and 22 cycles.” Those are offsets from cycle 2, not the cycle-index EOL; the wording conflicts with the table.

The report and Task 1 README state a 0.005 A rest deadband. `battery_thresholds.json` sets `rest_current_threshold_a` to **0.05 A**, and the Silver script reads that value: the documentation differs by a factor of ten. The report also says integration excludes timestamp reversals; `battery_validated_pipeline.build_intervals` explicitly audits calendar-clock reversals without vetoing an otherwise valid monotonic test-clock interval. Correct the narrative from the configuration and code.

### 3. The report mislabels validation metrics and misstates the square-root RUL model — high

The page-2 table titled “Full-series R²” is populated from rows filtered to `Scope == 'validation'`; the displayed R² values therefore refer to the validation interval. For 001_2, the lowest empirical validation RMSE is **square-root time, 0.0274 Ah** (validation R² ≈ −1.218); for 002_4 it is **exponential, 0.00777 Ah**. The root README instead names exponential as 001_2's best validation model (0.064 Ah).

The Task 2 *square-root elapsed-time* comparison uses observed future timestamps, as its own report acknowledges. The Task 4 *square-root cycle* RUL curve uses cycle index (`sqrt(n)`), not future timestamps. The current technical report conflates these distinct models when claiming the square-root cycle RUL forecast uses future timestamps.

### 4. Pack and fleet claims go beyond the available evidence — high

The technical report presents a removed simulation's saved outputs as computed pack behavior while the current branch cannot reproduce them. Its statement that pack EOL is the minimum of all cell EOLs is inconsistent with a 12S2P capacity envelope that first sums parallel cells and then limits on series groups: the first individual cell crossing does not generally equal the parallel-group or pack crossing.

Claims that centroid inference saves >99% while retaining weakest-link sensitivity, a specified activation-energy range is universally appropriate, or plating/mechanical-fatigue effects have particular directions are not demonstrated by the two cell datasets. Treat these as hypotheses or cite and validate a context-specific model; do not report them as findings. This audit does not validate whether a proposed fleet method would be safe or accurate.

### 5. RUL is relative to cycle 2, not verified nominal capacity — case-study limitation

The scripts use first capacity below 80% of the cell's own cycle-2 delivered Ah. The configured 2.5 Ah capacity is explicitly provisional; if taken as nominal, the 2.0 Ah threshold is already above both cells' first complete measured discharge capacities, so the nominal crossing cannot be established from these complete observations. State this as a data limitation rather than claiming nominal RUL is measured. The XGBoost and LSTM are trained on histories of both evaluated cells, so the reported error is not unseen-cell validation; seed variation is not a calibrated population RUL distribution.

### 6. Differential-voltage features are exploratory — interpretation limitation

Task 2 integrates discharge current, smooths/interpolates the measured voltage and screens interior dV/dQ candidates. Candidate repeatability is a smoothing/neighbor heuristic; detected extrema have not been matched to a physical electrode feature across cycles. Loaded-voltage polarization, missing temperature and uncertain reference conditions mean that LLI/LAM cannot be uniquely identified or quantified from these curves. `task2_analysis.md` states this limitation.

### 7. Test and GitHub coverage do not establish full pipeline health — high

`python -m unittest discover -s scripts -p 'test_*.py'` reports **30 tests passed**, but the Task 5 test file was removed and discovery does not test that every orchestrator target exists. `python -m compileall -q scripts` passes; neither check detects the missing Task 5 script. Add an orchestrator/entry-point existence test and restore targeted pack tests if executable scaling is intended.

GitHub's default branch is `main`; the audited changes are on `codex/six-task-validation`, not the default branch. The local HEAD is `9858bf6`, and the GitHub branch's `run_six_tasks.py` has the same Git blob hash (`8d1c5cf...`) and still contains the missing Task 5 invocation. The GitHub Actions **Tests** workflow for this exact commit [completed successfully](https://github.com/punkrocktanya/Casestudy-2/actions/runs/43517931930). It runs unit tests and syntax compilation, but it does not run the six-task pipeline or check the missing Task 5 entry point. The manual analysis workflow invokes Tasks 2–6 and will stop when the missing Task 5 file is reached.

## Additional technical checks

- Gold has 202 rows: per cell, 99 are `REVIEW` and 2 are `FAIL`; “99 complete” refers to computationally paired cycles, not protocol-verified complete cycles. Missing temperatures are not replaced. Each cell has 99 valid discharge integrations and zero protocol-verified full cycles. Median diagnostic coulombic efficiencies are 99.1078% and 99.2582%; five and one cycles, respectively, exceed 100% and need review.
- The Task 2 recursive 15-step test RMSE for Random Forest is 0.01245 Ah (001_2) and 0.02140 Ah (002_4), lower than its LSTM on this particular late-cycle split. The dataset has only two cells; this does not establish general superiority. Recursive LSTM forecasts show increasing error over this example horizon, but error need not grow exponentially.
- Fade-rate columns use opposite signs: unsmoothed fade is `-ΔQ`, while the smoothed column is a centered rolling mean of `ΔQ`; the centered smoother also uses future neighboring points. Both conventions are described in the report but require care in downstream use.
- The four plots and a five-page PDF exist. The three saved PDF copies have identical SHA-256 hashes; visual inspection found five rendered pages. Page count and identical files do not validate the scientific claims.
- The repository tracks both source Excel workbooks at this commit (`git ls-files`); a `.gitignore` entry does not untrack a file already committed. Check data-sharing authorization before distributing the repository.
- `SUBMISSION_MANIFEST.json` is a historical package snapshot and should not be represented as integrity proof for this changed branch.

## Recommended correction order

1. Decide whether Task 5 must be executable. If yes, restore a reviewed implementation and tests, or implement a new validated scenario model; keep assumptions and the data limits explicit.
2. Make the runner and task READMEs match the chosen Task 5 scope. Add a preflight test that every referenced entry script and required input exists.
3. Correct report and README claims: deadband, calendar reversals, validation R², best model per cell, cycle EOL versus elapsed-cycle offsets, and square-root-time versus square-root-cycle.
4. Remove or qualify unsupported electrode, pack RUL and fleet-cost claims; label historical pack results and the lack of measured thermal or balancing data.
5. Regenerate the Task 6 report and its copies from checked inputs, re-run the complete pipeline from workbooks in an isolated checkout, run all tests and verify GitHub Actions on the resulting commit.

## Reproduction notes

The audit checked local code and GitHub metadata without changing the user's analyses. In an isolated temporary copy, Task 1 was run from both source workbooks, followed by Tasks 2, 3, 4, 5 and 6 individually:

| Stage | Result | Qualification |
|---|---|---|
| Task 1 | Passed | Rebuilt source-to-Gold from the two workbooks. |
| Task 2 | Passed | Used the rebuilt Task 1 outputs. |
| Task 3 | Passed | Used available rebuilt upstream outputs. |
| Task 4 | Passed | Used the rebuilt Task 2 capacity data. |
| Task 5 | **Failed** | Referenced simulation script is absent. |
| Task 6 | Passed independently | It consumed the pre-existing Task 5 scenario summary, because Task 5 could not regenerate it. |

The real all-tasks runner stops at Task 5; the independent Task 6 result does not change that. The current saved PDF was separately checked as five pages, with identical copies and visible layout. Scientific conclusions require independent experimental validation and should not be inferred from software tests alone.

## Historical local Task 5 recheck (before corrections)

- At the recheck, the Task 5 script, entry point, test file and `__init__.py` had been restored locally, while the audited commit `9858bf6` did not contain them.
- In an isolated copy, `python scripts/run_six_tasks.py --task 5` and `--task 6` both exited successfully. An independent Task 5 run in a temporary output directory reproduced the local `scenario_summary.csv` exactly. It produced 800 samples (100 per cell and scenario), with no missing crossings in these scenarios. The complete Tasks 1–6 run was not repeated as part of this recheck.
- All 35 currently discoverable unit tests pass, including five topology-envelope tests. These tests check capacity aggregation, not thermal calibration, balancing dynamics or all end-to-end cases.
- The local report builder and the three identical five-page PDF copies now state the correct parallel-sum/series-minimum pack envelope; pack EOL is not defined as the earliest individual-cell crossing. However, `pack_scaling_methodology.md` section E still defines pack EOL as the minimum of cell EOLs, so the documents remain inconsistent.
- The simulation compares capacity to an **ideal, identical-cell fully charged baseline** (`2 × q0`), not each simulated pack's own initial accessible capacity. Initial variation and SOC deficit therefore contribute to crossing the 80% reference. If the intended metric is retention relative to each actual simulated pack's BOL, a per-sample denominator and rerun are needed; at minimum the current assumption must be explicit.
- Current mean EOL (uniform → gradient, no balance): 001_2 `10.11 → 8.97` cycles (−1.14); 002_4 `19.45 → 16.91` (−2.54). Task 5 README and report still state approximately 1.5 and 3 cycles, based on earlier results. Their table is data-driven but explanatory text is stale. The README also calls `q0` cycle-1 capacity, while the input analysis starts at cycle 2.
- Existing report discrepancies from the original audit remain, including 0.005 A versus configured 0.05 A, R² labeling and “actual EOL is 11 and 22 cycles.” The three report copies match each other, but matching copies do not make those statements correct.
- The sample count is illustrative. Temperature, capacity spread, fade-rate spread and balancing remain assumed; no electrothermal pack measurements validate the scenarios. An asserted universal activation-energy range, weakest-link preservation by clustering, and electrode mechanism claims require evidence and qualification.
