# Shared minimal LSTM experiment

Run `python estimate_rul_lstm_minimal.py` and `python -m unittest test_rul_lstm_minimal` from the project root after installing dependencies.

One shared model per checkpoint/window/seed, trained on both batteries' available histories only. Main input window: 3 cycles; separate baseline: 1 cycle. One LSTM layer, one hidden unit, one linear change output: 18 trainable parameters. Hidden state resets per input window; the 1-cycle baseline has no temporal memory across observations. Each cell is normalized by its own cycle-2 capacity. Windows never cross cell boundaries. Forecasts use predicted capacities recursively until the first strictly-below-0.8 crossing or 1,000 future steps. Raw predictions are not forced to decline. Both cells remain pre-EOL at checkpoints 5, 8, 10 and 12.

Fixed inherited training settings: Adam 0.008, weight decay 0.0001, Huber delta 0.02, 130 epochs, deterministic CPU, seeds 42/7/123. No tuning, validation-based selection or early stopping was performed. This is exploratory; the tiny available histories do not support strong independent validation. Existing separate-model outputs are preserved.

Plots show all three seeds, not a confidence interval. At checkpoint 8, the 3-cycle model has 8 pooled training examples: RUL predictions are 18/4/8 for 001_2 (actual 5) and 25/9/13 for 002_4 (actual 16). The 1-cycle baseline has 12 examples: predictions 8/3/6 and 13/7/10. Results are initialization-sensitive; minimum hidden size does not guarantee accuracy.

Across all four checkpoints and three seeds, the main 3-cycle setup scores 11/12 predictions per cell (one no-crossing result each). MAEs of 3.55 and 5.27 cycles are conditional on successful crossings. The 1-cycle baseline scores 12/12, with MAEs 1.25 and 6.08. These unequal-coverage aggregates are not a fair standalone ranking. See predictions.csv for all statuses and metrics.csv for coverage. Two batteries and overlapping windows do not establish fleet generalization.
