"""Summarize Task 2 models and exploratory differential-voltage candidates.

Candidate positions are not linked across cycles: proximity and normalized
capacity alone cannot establish that two extrema are the same electrode feature.
"""

# Make shared task modules importable when running this file directly.
import sys as _task_sys
from pathlib import Path as _TaskPath
_task_scripts = _TaskPath(__file__).resolve().parents[1]
for _task_dir in ("task1_data_engineering", "task2_degradation_modeling", "task3_anomaly_detection", "task4_rul_estimation", "task5_pack_scaling", "task6_reporting"):
    _task_path = str(_task_scripts / _task_dir)
    if _task_path not in _task_sys.path:
        _task_sys.path.append(_task_path)

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
OUTPUTS = ROOT / 'scripts' / 'outputs'
OUT = OUTPUTS / '06_differential_voltage'
SELECT = (2, 10, 25, 50, 75, 100)


def summarize_features(features, audit, physical):
    """Return one record per representative cell/cycle, including no detections."""
    base = audit[audit['cycle'].isin(SELECT)][['cell', 'cycle', 'capacity_Ah', 'samples', 'zero_dt']].copy()
    selected = features[(features['window'] == 21) & features['cycle'].isin(SELECT)]
    counts = selected.groupby(['cell', 'cycle']).agg(
        candidate_count=('stable', 'size'), stable_count=('stable', 'sum'),
        duplicate_affected_count=('duplicate_affected', 'sum')).reset_index()
    support = (physical[physical['cycle'].isin(SELECT)]
               .groupby(['cell', 'cycle'], as_index=False)['sampling_supported'].all())
    result = base.merge(counts, on=['cell', 'cycle'], how='left').merge(support, on=['cell', 'cycle'], how='left')
    for col in ('candidate_count', 'stable_count', 'duplicate_affected_count'):
        result[col] = result[col].fillna(0).astype(int)
    return result.sort_values(['cell', 'cycle']).reset_index(drop=True)


def plot_features(features, summary):
    """Plot detections, not trajectories: no cross-cycle identities are assumed."""
    cells = sorted(summary.cell.unique())
    fig, axes = plt.subplots(len(cells), 2, figsize=(12, 4.2 * len(cells)), squeeze=False, constrained_layout=True)
    for row, cell in enumerate(cells):
        g = features[(features.cell == cell) & (features.window == 21) & features.cycle.isin(SELECT)]
        for stable, label, color, marker in [(False, 'Other candidates', '#d99034', 'x'), (True, 'Repeated in checks', '#176b87', 'o')]:
            sub = g[g.stable == stable]
            axes[row, 0].scatter(sub.cycle, sub.q_fraction, label=label, color=color, marker=marker, s=32, alpha=.8)
            axes[row, 1].scatter(sub.cycle, sub.width_Ah, label=label, color=color, marker=marker, s=32, alpha=.8)
        axes[row, 0].set(title=f'{cell}: candidate position', xlabel='Cycle index', ylabel='Q / Q_end', xticks=SELECT, ylim=(.1, .9))
        axes[row, 1].set(title=f'{cell}: half-prominence width', xlabel='Cycle index', ylabel='Width (Ah)', xticks=SELECT)
        for ax in axes[row]: ax.grid(alpha=.2); ax.legend(fontsize=8)
    fig.suptitle('dV/dQ interior candidates by cycle — points are not matched identities', fontsize=12)
    fig.savefig(OUT / 'feature_candidates_by_cycle.png', dpi=180)
    plt.close(fig)


def build_analysis(summary):
    scores = pd.read_csv(OUTPUTS / '05_capacity_model_comparison' / 'metrics.csv', dtype={'Dataset_ID': str})
    lines = ['# Task 2 — capacity fade, modeling and differential voltage', '',
        '## Method and sign convention', '',
        'Discharge capacity Q is the positive trapezoidal integral of -I over the discharge phase. '
        'Voltage normally decreases as discharged Q increases, so dV/dQ is usually negative. '
        'The candidate detector finds positive local maxima of -dV/dQ, equivalent to local minima of signed dV/dQ. '
        'A voltage plateau has dV/dQ near zero; these candidates are not automatically electrode phase transitions.', '',
        'For each representative cycle the pipeline consolidates duplicate capacity coordinates with median voltage, '
        'interpolates onto 301 evenly spaced capacity points, applies cubic Savitzky–Golay windows of 11, 21 and 31 points, '
        'and evaluates the numerical gradient. It excludes the first and last 10% from feature detection. '
        'A second grid uses 0.005 Ah spacing; its 11, 21 and 31 point windows span 0.050, 0.100 and 0.150 Ah. '
        'Half-prominence width describes a derivative feature, not an electrode capacity. Interpolation creates no new measurement resolution.', '',
        '## Capacity and candidate counts', '',
        '| Cell | Cycle | Discharge capacity (Ah) | Samples | Candidates | Repeated in checks | Fixed grid supported |',
        '|---|---:|---:|---:|---:|---:|---|']
    for r in summary.itertuples():
        support = 'yes' if r.sampling_supported == True else ('no' if r.sampling_supported == False else 'unknown')
        lines.append(f'| {r.cell} | {r.cycle} | {r.capacity_Ah:.4f} | {r.samples} | {r.candidate_count} | {r.stable_count} | {support} |')
    lines += ['', 'The repetition flag requires a nearby detection within 0.05 Q/Q_end in all three normalized-grid windows '
        'and at least one adjacent cycle, and excludes duplicate-affected candidates. It is a heuristic: it does not establish '
        'a physical feature identity or validate the fixed grid. Candidate positions and widths are shown without connecting '
        'points across cycles. Changes in peak spacing or apparent compression cannot be claimed as LLI or LAM without '
        'independently matched features, reference electrode data or validated electrode-level modelling.', '',
        '## Held-out model comparison', '',
        'All models below use a fixed-origin, recursive 15-cycle test after cycle 85. The test fit uses cycles through 85; '
        'the earlier validation uses data through cycle 70. The constrained exponential surrogate is phenomenological, '
        'not an identified SEI or other electrode mechanism. RF and LSTM use the available history of the same cell; '
        'this does not test performance on unseen cells.', '',
        '| Cell | Approach | Test RMSE (Ah) | Test MAE (Ah) |', '|---|---|---:|---:|']
    for r in scores[scores.Stage.eq('test')].sort_values(['Dataset_ID','RMSE_Ah']).itertuples():
        lines.append(f'| {r.Dataset_ID} | {r.Model} | {r.RMSE_Ah:.4f} | {r.MAE_Ah:.4f} |')
    lines += ['', '## Interpretation and limitations', '',
        'Both cells show a substantial reduction in delivered capacity and evolving loaded-voltage derivatives. '
        'Different currents, missing temperature, measurement quantization and changing polarization confound the comparison. '
        'A stable detector candidate is a repeatable computational observation, not a verified degradation mechanism. '
        'Low-rate reference curves, verified voltage cutoffs, measured temperatures and validated electrode models or reference-electrode '
        'measurements are required for stronger LLI/LAM attribution.', '',
        '### LLI and LAM: limits of interpretation', '',
        '| Mechanism | Meaning | Possible evidence in validated electrode-related features |',
        '|---|---|---|',
        '| Loss of lithium inventory (LLI) | Less cyclable lithium is available to move between the electrodes. | Changes in the relative positions of identifiable electrode-related features, sometimes called electrode slippage. |',
        '| Loss of active material (LAM) | Some electrode material becomes unavailable for reversible lithium storage. | Changes in the capacity span or shape of features associated with the affected electrode. |', '',
        'The derivative curves and detected minima change as capacity declines. However, the minima have not been reliably '
        'matched as the same physical features across cycles, and the early selected cycles have no interior detections under '
        'the current settings. We therefore cannot measure a defensible feature shift or compression and attribute it to either mechanism.', '',
        'The relatively high discharge currents introduce polarization into the measured voltage. Missing temperatures and the '
        'absence of electrode-specific reference curves add uncertainty. The decline in delivered capacity is not a direct '
        'measurement of LLI or LAM.', '',
        'Further investigation would require low-rate reference tests at controlled temperatures, together with validated '
        'positive- and negative-electrode reference curves or reference-electrode measurements. These inputs can support '
        'electrode-level fitting; the resulting estimates must include their assumptions and uncertainty.', '',
        'Use `overlays_<cell>.png` for voltage and derivative curves, `sensitivity_<cell>.png` for window and adjacent-cycle checks, '
        '`interior_comparison_<cell>.png` for physical-grid sensitivity, `feature_candidates_by_cycle.png` for '
        'unmatched candidate positions and widths, and `representative_features.csv` for individual values.']
    return '\n'.join(lines) + '\n'


def main():
    features = pd.read_csv(OUT / 'representative_features.csv', dtype={'cell': str})
    audit = pd.read_csv(OUT / 'integration_audit.csv', dtype={'cell': str})
    physical = pd.read_csv(OUT / 'physical_grid_sensitivity.csv', dtype={'cell': str})
    summary = summarize_features(features, audit, physical)
    summary.to_csv(OUT / 'feature_cycle_summary.csv', index=False)
    plot_features(features, summary)
    (OUT / 'task2_analysis.md').write_text(build_analysis(summary), encoding='utf8')
    print(summary.to_string(index=False))
    print('Task 2 analysis:', OUT / 'task2_analysis.md')

if __name__ == '__main__':
    main()
