# Task 2 — capacity fade, modeling and differential voltage

## Method and sign convention

Discharge capacity Q is the positive trapezoidal integral of -I over the discharge phase. Voltage normally decreases as discharged Q increases, so dV/dQ is usually negative. The candidate detector finds positive local maxima of -dV/dQ, equivalent to local minima of signed dV/dQ. A voltage plateau has dV/dQ near zero; these candidates are not automatically electrode phase transitions.

For each representative cycle the pipeline consolidates duplicate capacity coordinates with median voltage, interpolates onto 301 evenly spaced capacity points, applies cubic Savitzky–Golay windows of 11, 21 and 31 points, and evaluates the numerical gradient. It excludes the first and last 10% from feature detection. A second grid uses 0.005 Ah spacing; its 11, 21 and 31 point windows span 0.050, 0.100 and 0.150 Ah. Half-prominence width describes a derivative feature, not an electrode capacity. Interpolation creates no new measurement resolution.

## Capacity and candidate counts

| Cell | Cycle | Discharge capacity (Ah) | Samples | Candidates | Repeated in checks | Fixed grid supported |
|---|---:|---:|---:|---:|---:|---|
| 001_2 | 2 | 1.5114 | 755 | 0 | 0 | no |
| 001_2 | 10 | 1.2635 | 629 | 0 | 0 | no |
| 001_2 | 25 | 0.8676 | 427 | 5 | 0 | no |
| 001_2 | 50 | 0.5338 | 268 | 8 | 7 | yes |
| 001_2 | 75 | 0.3659 | 184 | 10 | 6 | yes |
| 001_2 | 100 | 0.2700 | 135 | 10 | 7 | yes |
| 002_4 | 2 | 1.6878 | 1257 | 0 | 0 | yes |
| 002_4 | 10 | 1.5622 | 1137 | 0 | 0 | no |
| 002_4 | 25 | 1.3125 | 981 | 1 | 0 | yes |
| 002_4 | 50 | 0.8599 | 642 | 5 | 0 | yes |
| 002_4 | 75 | 0.5942 | 444 | 6 | 1 | no |
| 002_4 | 100 | 0.4526 | 335 | 9 | 2 | yes |

The repetition flag requires a nearby detection within 0.05 Q/Q_end in all three normalized-grid windows and at least one adjacent cycle, and excludes duplicate-affected candidates. It is a heuristic: it does not establish a physical feature identity or validate the fixed grid. Candidate positions and widths are shown without connecting points across cycles. Changes in peak spacing or apparent compression cannot be claimed as LLI or LAM without independently matched features, reference electrode data or validated electrode-level modelling.

## Held-out model comparison

All models below use a fixed-origin, recursive 15-cycle test after cycle 85. The test fit uses cycles through 85; the earlier validation uses data through cycle 70. The constrained exponential surrogate is phenomenological, not an identified SEI or other electrode mechanism. RF and LSTM use the available history of the same cell; this does not test performance on unseen cells.

| Cell | Approach | Test RMSE (Ah) | Test MAE (Ah) |
|---|---|---:|---:|
| 001_2 | Random Forest | 0.0125 | 0.0108 |
| 001_2 | Persistence | 0.0303 | 0.0265 |
| 001_2 | LSTM | 0.0380 | 0.0332 |
| 001_2 | Physics-constrained surrogate | 0.0522 | 0.0518 |
| 001_2 | Exponential | 0.0758 | 0.0754 |
| 002_4 | Random Forest | 0.0214 | 0.0197 |
| 002_4 | Physics-constrained surrogate | 0.0274 | 0.0263 |
| 002_4 | Exponential | 0.0274 | 0.0263 |
| 002_4 | Persistence | 0.0434 | 0.0373 |
| 002_4 | LSTM | 0.0512 | 0.0456 |

## Interpretation and limitations

Both cells show a substantial reduction in delivered capacity and evolving loaded-voltage derivatives. Different currents, missing temperature, measurement quantization and changing polarization confound the comparison. A stable detector candidate is a repeatable computational observation, not a verified degradation mechanism. Low-rate reference curves, verified voltage cutoffs, measured temperatures and validated electrode models or reference-electrode measurements are required for stronger LLI/LAM attribution.

### LLI and LAM: limits of interpretation

| Mechanism | Meaning | Possible evidence in validated electrode-related features |
|---|---|---|
| Loss of lithium inventory (LLI) | Less cyclable lithium is available to move between the electrodes. | Changes in the relative positions of identifiable electrode-related features, sometimes called electrode slippage. |
| Loss of active material (LAM) | Some electrode material becomes unavailable for reversible lithium storage. | Changes in the capacity span or shape of features associated with the affected electrode. |

The derivative curves and detected minima change as capacity declines. However, the minima have not been reliably matched as the same physical features across cycles, and the early selected cycles have no interior detections under the current settings. We therefore cannot measure a defensible feature shift or compression and attribute it to either mechanism.

The relatively high discharge currents introduce polarization into the measured voltage. Missing temperatures and the absence of electrode-specific reference curves add uncertainty. The decline in delivered capacity is not a direct measurement of LLI or LAM.

Further investigation would require low-rate reference tests at controlled temperatures, together with validated positive- and negative-electrode reference curves or reference-electrode measurements. These inputs can support electrode-level fitting; the resulting estimates must include their assumptions and uncertainty.

Use `overlays_<cell>.png` for voltage and derivative curves, `sensitivity_<cell>.png` for window and adjacent-cycle checks, `interior_comparison_<cell>.png` for physical-grid sensitivity, `feature_candidates_by_cycle.png` for unmatched candidate positions and widths, and `representative_features.csv` for individual values.
