## Review follow-up: forecast bias and parameter sensitivity

- These diagnostics were specified after inspecting the existing test results. They do not turn that test window into a fresh independent validation set.
- Original four-panel plots show descriptive full-series fits. New chronological_test_*.png figures show forecasts fitted only through cycle 85.
- Square-root predictions are explicitly conditional on observed future times and are shown separately from cycle-only forecasts.
- An asymptotic exponential is a reasonable future candidate, but it has not been fitted here. Choosing it after seeing these test results would require new rolling-origin validation; its asymptote would not be a guaranteed physical residual capacity.

**001_2**

- Recorded time span: 1.4052 days. This is a short cycling experiment; a square-root fit is not evidence of long-term calendar aging.
- Exponential test mean bias (prediction minus observation): -0.075402 Ah. Cycle 100 prediction: 0.196981 Ah; measured: 0.269956 Ah.
- Removing all CE-flagged cycles changes the power-law curve by up to 0.420170 Ah across the full original grid; the maximum occurs at cycle 2. Over retained fitting cycles the maximum is 0.131299 Ah.
- Power-law [q0,a,b] changes from [1.7067306190714704, 0.22675444563202843, np.float64(0.41298143396345677)] to [2.1269005556992338, 0.5156252386820864, np.float64(0.2852714971051852)]. The sensitivity is not evidence that the excluded capacities were erroneous.
- Free square-root intercept: 1.728421 Ah versus measured 1.511447 Ah (14.36% higher). Full-fit RMSE: 0.041890 Ah free versus 0.076866 Ah anchored.
- Anchoring forces the first point to match but can worsen the rest of the fit. Cycle 2 itself has uncertain SOC conditions; anchoring is a sensitivity exercise, not a correction.

**002_4**

- Recorded time span: 2.2733 days. This is a short cycling experiment; a square-root fit is not evidence of long-term calendar aging.
- Exponential test mean bias (prediction minus observation): -0.026322 Ah. Cycle 100 prediction: 0.417637 Ah; measured: 0.452649 Ah.
- Removing all CE-flagged cycles changes the power-law curve by up to 0.059465 Ah across the full original grid; the maximum occurs at cycle 2. Over retained fitting cycles the maximum is 0.038782 Ah.
- Power-law [q0,a,b] changes from [1.8201573069920287, 0.07332799528693003, np.float64(0.6514316236869135)] to [1.8796221236548913, 0.09401102688855294, np.float64(0.6049003959841975)]. The sensitivity is not evidence that the excluded capacities were erroneous.
- Free square-root intercept: 2.136900 Ah versus measured 1.687755 Ah (26.61% higher). Full-fit RMSE: 0.086440 Ah free versus 0.160350 Ah anchored.
- Anchoring forces the first point to match but can worsen the rest of the fit. Cycle 2 itself has uncertain SOC conditions; anchoring is a sensitivity exercise, not a correction.

**Test comparison (all models retained for transparency)**

| Cell | Model | RMSE Ah | Mean bias Ah |
|---|---|---:|---:|
| 001_2 | Exponential | 0.075778 | -0.075402 |
| 001_2 | Linear | 0.252195 | -0.248537 |
| 001_2 | Power law | 0.110441 | -0.108842 |
| 001_2 | Square-root time | 0.057135 | -0.055822 |
| 001_2 | Persistence | 0.030342 | 0.026472 |
| 002_4 | Exponential | 0.027380 | -0.026322 |
| 002_4 | Linear | 0.209611 | -0.205345 |
| 002_4 | Power law | 0.134143 | -0.131079 |
| 002_4 | Square-root time | 0.060233 | 0.060169 |
| 002_4 | Persistence | 0.043391 | 0.037143 |

- Negative bias means systematic underprediction. Negative predictions are still reported rather than clipped.
- Curvature in residuals means the model misses a changing trajectory shape. It does not identify an electrochemical mechanism.
- Parameter sensitivity tables separate removing cycle 2 from removing later flagged cycles. Large changes at the removed origin are extrapolation sensitivity; retained-domain differences must also be examined.
- These are deterministic deletion diagnostics, not statistical confidence intervals. They do not establish population robustness.
