# Common-checkpoint evaluation

`all_attempts.csv` retains every attempted forecast from individual curves, shared XGBoost and minimal LSTM (both windows, all three seeds). `all_checkpoint_metrics.csv` reports MAE conditional on successful EOL crossing AND coverage.

The primary four-family comparison (`predictions.csv`, `metrics.csv`) predefines checkpoint cycles **8 and 10** for both cells. It compares individual Linear, individual Exponential, shared XGBoost and shared minimal three-cycle LSTM (three seeds). All attempts are retained, including failures. Each seed is a distinct initialization, **not** an independent battery. The common evaluation has two distinct cells, and is not external validation.

`all_method_common_predictions.csv` and `all_method_common_metrics.csv` extend the SAME checkpoints (8 and 10) to all four empirical curve models, shared XGBoost and both minimal-LSTM window lengths, with no model exclusions.

EOL is first integer cycle below 80% of *own cycle-2 high-current delivered capacity*, not nominal-condition SOH.
