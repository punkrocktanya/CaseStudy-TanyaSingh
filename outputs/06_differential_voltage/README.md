# Differential voltage analysis

- Source: Silver discharge phases; representative cycles 2, 10, 25, 50, 75, 100. Adjacent cycles support sensitivity checks.
- Q = cumulative trapezoidal integral of -I dt / 3600. No integration across phases. Repeated times add zero capacity; duplicate capacity coordinates use median voltage; spreads above 5 mV are flagged in duplicate_capacity_audit.csv (a provisional review threshold).
- Voltage is interpolated to 301 evenly spaced capacity points. Cubic Savitzky–Golay windows 11, 21 and 31 are compared; numerical gradient gives dV/dQ. Window 21 is the overlay default.
- Negative derivative means falling voltage. Peaks are local maxima of -dV/dQ; edge regions are excluded. Width is half-prominence width, not electrode capacity.
- Peak candidates are stable only when matched within 5% discharged fraction in all three windows and at least one available adjacent cycle. This is a heuristic, not statistical confidence or electrode identification.
- Normalized x axes use Q/Q_end; derivative units remain V/Ah. Grid interpolation does not add measurement resolution.
- The shrinking capacity span and derivative changes describe apparent loaded-voltage behaviour. Polarization and changing accessible capacity confound electrode interpretation. LLI and LAM cannot be quantified from these high-current curves alone.
- Files: twelve trace CSVs/PNGs, cell overlay PNGs, sensitivity PNGs, peak_candidates.csv and integration_audit.csv.

## Revised checks

- Full diagnostic overlays are retained. Interior comparison plots show only 10–90% discharged capacity.
- Detection and half-prominence widths are computed within the interior; thresholds use its 5th–95th percentile range.
- Fixed-grid comparison uses 0.005 Ah spacing and windows spanning 0.050, 0.100 and 0.150 Ah. Sampling support is recorded in physical_grid_sensitivity.csv; interpolation adds no resolution.
- Duplicate-affected features cannot receive the stability flag. Median aggregation remains exploratory where voltage spread is significant; original trace data are retained.
- representative_features.csv reports position, signed amplitude, width and repeatability. Cross-cycle feature identities and shifts are left unassigned: proximity alone does not establish the same electrode feature.
- Stability refers only to normalized-window and adjacent-cycle checks, not physical-grid validation or confirmed degradation.
