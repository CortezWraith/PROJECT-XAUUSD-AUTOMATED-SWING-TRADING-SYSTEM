# Pooled 2004-07 .. 2026-08 (PRE + DEV + OOS + HOLDOUT), baseline costs

| strategy | trades | exp_r | t_stat | pf | sharpe | positive_segments | exp_PRE | exp_DEV | exp_OOS | exp_HOLDOUT | long_exp_r | short_exp_r |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C3 ema_trend_h4 | 412 | 0.067 | 1.250 | 1.195 | 0.269 | 4 | 0.064 | 0.074 | 0.038 | 0.106 | 0.101 | 0.035 |
| C2 donchian_h4 (reference) | 595 | 0.149 | 1.707 | 1.245 | 0.403 | 4 | 0.316 | 0.064 | 0.094 | 0.197 | 0.384 | -0.147 |
| C5 squeeze_h4 | 810 | 0.074 | 1.462 | 1.156 | 0.325 | 3 | 0.122 | 0.109 | -0.092 | 0.162 | 0.136 | 0.009 |
| C9 donchian_usd_h4 | 371 | 0.125 | 1.121 | 1.194 | 0.258 | 3 | 0.123 | 0.192 | -0.013 | 0.180 | 0.335 | -0.120 |
| C8b session_asia_london_h1 (cost-conditional) | 11281 | -0.006 | -2.145 | 0.949 | -0.460 | 1 | -0.005 | 0.003 | -0.017 | -0.015 | -0.001 | -0.010 |
