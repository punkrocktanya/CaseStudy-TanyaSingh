"""Illustrative capacity-envelope scenarios for a synthetic 12S2P pack.

NOT a validated electrothermal pack model. All thermal, variation and balancing
parameters are assumed (not calibrated from the two supplied cells). Results are
sensitivity demonstrations only — see outputs/13_pack_scaling/pack_scaling_methodology.md.

Topology: M modules in series, each containing S series groups of P parallel cells.
Pack capacity = min over modules of [min over series groups of (sum of parallel cell
capacities × usable SOC)].  This is a charge-availability envelope: no OCV/voltage
model, no unequal parallel-cell current dynamics, no thermal ODE, no resistance growth,
no BMS voltage cutoff.
"""

import sys as _sys
from pathlib import Path as _Path

_scripts = _Path(__file__).resolve().parents[1]
for _d in ("task1_data_engineering", "task2_degradation_modeling",
           "task3_anomaly_detection", "task4_rul_estimation",
           "task5_pack_scaling", "task6_reporting"):
    _p = str(_scripts / _d)
    if _p not in _sys.path:
        _sys.path.append(_p)

import json
import hashlib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from stage_08_individual_curve_rul import INPUT   # path to cycle_capacity_analysis.csv
from stage_04_fit_capacity_fade import fit

ROOT = _Path(__file__).resolve().parents[2]
OUT  = _Path(__file__).resolve().parent / "outputs" / "13_pack_scaling"

# ── Assumed configuration (NOT fitted from data) ──────────────────────────────
# All values are illustrative. See methodology doc §A–C for calibration needs.
CONFIG = dict(
    series_groups_per_module  = 4,       # S: series groups per module
    parallel_cells            = 2,       # P: parallel cells per group
    modules_in_series         = 3,       # M: modules in series  → 24 cells total
    ensemble_size             = 100,     # Monte Carlo sample count
    seed                      = 42,
    # Cell-to-cell variation (assumed; literature manufacturing CVs)
    capacity_cv               = 0.03,    # 3 % lognormal CV for initial capacity
    rate_cv                   = 0.15,    # 15 % lognormal CV for fade rate k
    # Thermal gradient (assumed; not measured)
    reference_temperature_K   = 298.15,
    activation_energy_J_mol   = 20000,   # WARNING: low vs. literature (40–80 kJ/mol)
    maximum_temperature_offset_K = 10,
    # Balancing (assumed)
    initial_soc_spread        = 0.03,    # uniform [0, 3 %] SOC deficit before balancing
    balance_current_A         = 0.05,
    balance_hours             = 1,
    active_transfer_efficiency = 0.85,
    horizon                   = 300,
)


def envelope(capacities, usable_soc):
    """Topology-aware capacity envelope.

    Parameters
    ----------
    capacities : ndarray, shape (E, M, S, P)
        Cell capacities (Ah) for E ensemble members, M modules,
        S series groups per module, P parallel cells per group.
    usable_soc : ndarray, same shape
        Usable state-of-charge fraction [0, 1] for each cell.

    Returns
    -------
    module_caps : ndarray, shape (E, M)
        Capacity of each module = min over S groups of (sum of P parallel cells × SOC).
    pack_caps : ndarray, shape (E,)
        Pack capacity = min over M modules.

    Notes
    -----
    Parallel cells contribute additively (their Ah sums within a group).
    The weakest series group limits the module; the weakest module limits the pack.
    This is NOT the same as taking the minimum individual cell capacity.
    """
    group_caps  = (capacities * usable_soc).sum(axis=-1)   # (E, M, S)
    module_caps = group_caps.min(axis=-1)                   # (E, M)
    pack_caps   = module_caps.min(axis=-1)                  # (E,)
    return module_caps, pack_caps


def _lognormal(rng, centre, cv, shape):
    """Draw lognormal samples with given mean and coefficient of variation."""
    sigma = cv
    mu    = -0.5 * sigma ** 2          # median = centre after exp
    return centre * np.exp(rng.normal(mu, sigma, size=shape))


def main():
    OUT.mkdir(parents=True, exist_ok=True)

    data = pd.read_csv(INPUT, dtype={"Dataset_ID": str})
    rng  = np.random.default_rng(CONFIG["seed"])

    rows   = []     # one row per (cell, scenario, ensemble member)
    traces = []     # one row per (cell, scenario, cycle)

    shape = (
        CONFIG["ensemble_size"],
        CONFIG["modules_in_series"],
        CONFIG["series_groups_per_module"],
        CONFIG["parallel_cells"],
    )

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5), constrained_layout=True)

    for ax, (cell, g) in zip(axes, data.groupby("Dataset_ID")):

        # Fit exponential to early cycles to get a population baseline.
        h  = g[g.Cycle_Index <= 8].sort_values("Cycle_Index")
        q0 = float(h.Discharge_Capacity_Ah.iloc[0])
        k  = fit(
            "Exponential",
            h.Cycle_Index.to_numpy() - 2,
            h.Cycle_Index.to_numpy() - 2,
            h.Discharge_Capacity_Ah.to_numpy(),
        )[1]

        # Ensemble: lognormal draws for each cell position.
        initial = _lognormal(rng, q0, CONFIG["capacity_cv"], shape)
        rates   = _lognormal(rng, k,  CONFIG["rate_cv"],    shape)

        # SOC deficits: uniform [0, initial_soc_spread] before any balancing.
        deficit  = rng.uniform(0, CONFIG["initial_soc_spread"], size=shape)

        # Spatial temperature gradient (linear, assumed not measured).
        n_cells  = int(np.prod(shape[1:]))
        gradient = np.linspace(
            0, CONFIG["maximum_temperature_offset_K"], n_cells
        ).reshape((1,) + shape[1:])
        temp         = CONFIG["reference_temperature_K"] + gradient
        acceleration = np.exp(
            CONFIG["activation_energy_J_mol"] / 8.314
            * (1.0 / CONFIG["reference_temperature_K"] - 1.0 / temp)
        )

        # BOL reference: ideal fully-charged pack with no variation.
        # Used as the denominator so all scenarios share the same baseline.
        bol_initial = np.full(shape, q0)
        _, bol_pack = envelope(bol_initial, np.ones(shape))
        bol = bol_pack   # (E,) — same for all scenarios (rng-independent)

        scenarios = [
            ("uniform_no_balance",  False, "none"),
            ("gradient_no_balance", True,  "none"),
            ("gradient_passive",    True,  "passive"),
            ("gradient_active",     True,  "active"),
        ]

        for label, thermal, balancing in scenarios:

            eff_rate = rates * (acceleration if thermal else 1.0)

            # ── Balancing ────────────────────────────────────────────────────
            if balancing == "none":
                soc  = 1.0 - deficit
                loss = np.zeros(shape[0])

            elif balancing == "passive":
                # Passive (resistive): bleed excess charge from cells whose
                # deficit is BELOW the per-module maximum deficit down to that
                # maximum.  Cells with the least charge (most deficit) set the
                # target; cells with more charge are bled toward them.
                # Bounded by balance_current_A × balance_hours.
                target  = deficit.max(axis=(-2, -1), keepdims=True)   # most-deficient
                excess  = np.maximum(target - deficit, 0.0)           # surplus cells > 0
                removed = np.minimum(excess * initial,
                                     CONFIG["balance_current_A"] * CONFIG["balance_hours"])
                soc     = 1.0 - deficit - removed / initial
                loss    = (removed * 3.7).sum(axis=(1, 2, 3))         # Wh at 3.7 V (assumed)

            else:  # active
                # Active: redistribute from donors (below-mean deficit, i.e. more charge)
                # to recipients (above-mean deficit, i.e. less charge).
                target    = deficit.mean(axis=(-2, -1), keepdims=True)
                imbalance = (deficit - target) * initial               # +ve = needs more
                donor_cap = np.maximum(-imbalance, 0.0)                # cells giving charge
                recip_cap = np.maximum( imbalance, 0.0)                # cells receiving
                donor_tot = donor_cap.sum(axis=(-2, -1), keepdims=True)
                recip_tot = recip_cap.sum(axis=(-2, -1), keepdims=True)
                cap       = CONFIG["balance_current_A"] * CONFIG["balance_hours"]
                transferred = np.minimum(
                    np.minimum(donor_tot,
                               recip_tot / CONFIG["active_transfer_efficiency"]),
                    cap,
                )
                removed = np.where(
                    donor_tot > 0,
                    donor_cap * transferred / donor_tot,
                    0.0,
                )
                added = np.where(
                    recip_tot > 0,
                    recip_cap * transferred * CONFIG["active_transfer_efficiency"] / recip_tot,
                    0.0,
                )
                soc  = 1.0 - deficit + (added - removed) / initial
                loss = np.maximum(0.0,
                                  (removed - added).sum(axis=(1, 2, 3)) * 3.7)

            # Safety: soc must stay in [0, 1] (clamp floating-point overrun)
            soc = np.clip(soc, 0.0, 1.0)

            # ── Simulate pack capacity over horizon ──────────────────────────
            eol = np.full(shape[0], np.nan)

            for elapsed in range(CONFIG["horizon"] + 1):
                capacity    = initial * np.exp(-eff_rate * elapsed)
                _, pack_cap = envelope(capacity, soc)
                ratio       = pack_cap / bol

                # Record first cycle where pack capacity falls below 80 % of BOL.
                newly_eol = np.isnan(eol) & (ratio < 0.80)
                eol[newly_eol] = elapsed + 2   # +2 because n=0 corresponds to cycle 2

                traces.append(dict(
                    Dataset_ID     = cell,
                    Scenario       = label,
                    Cycle_Index    = elapsed + 2,
                    Mean_Retention = float(ratio.mean()),
                    P05_Retention  = float(np.quantile(ratio, 0.05)),
                    P95_Retention  = float(np.quantile(ratio, 0.95)),
                ))

            for i, v in enumerate(eol):
                rows.append(dict(
                    Dataset_ID            = cell,
                    Scenario              = label,
                    Sample                = i,
                    Predicted_EOL_Cycle   = v,
                    Initial_Balance_Loss_Wh = float(loss[i]),
                ))

            # Plot mean retention for this scenario.
            block = pd.DataFrame(traces)
            block = block[(block.Dataset_ID == cell) & (block.Scenario == label)]
            ax.plot(block.Cycle_Index, block.Mean_Retention,
                    label=label.replace("_", " "))

        ax.axhline(0.8, color="black", ls="--", lw=0.9)
        ax.set(
            title    = f"{cell}-based synthetic pack",
            xlabel   = "Cycle index",
            ylabel   = "Pack Ah / ideal BOL Ah",
            xlim     = (2, 50),
            ylim     = (0.3, 1.05),
        )
        ax.legend(fontsize=7)
        ax.grid(alpha=0.2)

    fig.savefig(OUT / "scenario_retention.png", dpi=180)
    plt.close(fig)

    # ── Write outputs ─────────────────────────────────────────────────────────
    result = pd.DataFrame(rows)
    result.to_csv(OUT / "scenario_samples.csv", index=False)
    pd.DataFrame(traces).to_csv(OUT / "scenario_trajectories.csv", index=False)

    summary = (
        result.groupby(["Dataset_ID", "Scenario"])
        .agg(
            Mean_EOL                  = ("Predicted_EOL_Cycle", "mean"),
            Min_EOL                   = ("Predicted_EOL_Cycle", "min"),
            Max_EOL                   = ("Predicted_EOL_Cycle", "max"),
            Mean_Initial_Balance_Loss_Wh = ("Initial_Balance_Loss_Wh", "mean"),
        )
        .reset_index()
    )
    summary.to_csv(OUT / "scenario_summary.csv", index=False)

    (OUT / "assumptions.json").write_text(
        json.dumps(
            dict(
                **CONFIG,
                source_sha256 = hashlib.sha256(INPUT.read_bytes()).hexdigest(),
                interpretation = (
                    "Synthetic illustrative scenarios only. All temperature, cell-variation "
                    "and balancing parameters are assumed (not calibrated from the two "
                    "supplied cells). Results are NOT validated pack performance."
                ),
            ),
            indent=2,
        ),
        encoding="utf-8",
    )

    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
