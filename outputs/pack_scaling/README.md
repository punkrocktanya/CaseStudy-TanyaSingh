# Illustrative module/pack capacity envelopes

4S2P modules, three in series (12S2P, 24 cells). Positive capacity and fade-rate spreads are sampled from explicitly assumed lognormal distributions. Early cell exponential fits through cycle 8 supply rate baselines. Assumed 0-10 K gradients modify rates through an uncalibrated Arrhenius factor. These are sensitivity inputs, NOT estimated thermal parameters or manufacturing distributions.

Parallel capacities are summed and series-group capacities limited by the minimum. This is a charge-availability envelope: no voltage/OCV model, unequal parallel current dynamics, thermal ODE, calendar ageing, resistance growth or BMS voltage cutoff is simulated. Actual delivered pack capacity can be lower. Independent cell envelopes do not validate real pack lifetime.

No balancing retains initial SOC deficits. Passive balancing bleeds excess charge toward the lowest SOC, bounded by current and duration; it does not create usable charge. Active redistribution is bounded by donor charge, recipient deficit, current, time and transfer efficiency. Loss uses an illustrative 3.7 V constant. The corrected SOC margins are held fixed over ageing; balance heat and repeated balancing are not fed back into degradation. This isolates initial-accessibility scenarios rather than claiming a full balancing lifetime benefit. All scenarios use the same ideal fully charged BOL denominator.

Report these plots only as synthetic sensitivity demonstrations. Needed for validation: more matched cells, current/voltage traces, temperature/cooling data, interconnection resistances and measured balancer behaviour. Ensemble bands are assumed scenario spread, not calibrated probability intervals. No actual pack EOL is claimed.
