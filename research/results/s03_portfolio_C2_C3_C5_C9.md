# Cross-strategy complementarity (DEV+OOS 2010-2023)


## Daily return correlation
|    |   C2 |   C3 |   C5 |   C9 |
|:---|-----:|-----:|-----:|-----:|
| C2 | 1    | 0.45 | 0.43 | 0.79 |
| C3 | 0.45 | 1    | 0.34 | 0.32 |
| C5 | 0.43 | 0.34 | 1    | 0.33 |
| C9 | 0.79 | 0.32 | 0.33 | 1    |

## Pairwise overlap
| pair | corr_daily | time_in_market_a | time_in_market_b | overlap_share_of_time | overlap_expected_if_indep | same_direction_share_of_overlap | opposite_direction_share_of_overlap | drawdown_corr | joint_deep_dd_share | joint_deep_dd_if_indep |
|---|---|---|---|---|---|---|---|---|---|---|
| C2 / C3 | 0.451 | 0.452 | 0.271 | 0.182 | 0.122 | 1.000 | 0.000 | 0.699 | 0.141 | 0.040 |
| C2 / C5 | 0.427 | 0.452 | 0.325 | 0.188 | 0.147 | 0.989 | 0.011 | 0.670 | 0.148 | 0.040 |
| C2 / C9 | 0.794 | 0.452 | 0.275 | 0.273 | 0.124 | 1.000 | 0.000 | 0.864 | 0.158 | 0.040 |
| C3 / C5 | 0.341 | 0.271 | 0.325 | 0.113 | 0.088 | 0.987 | 0.013 | 0.684 | 0.161 | 0.040 |
| C3 / C9 | 0.322 | 0.271 | 0.275 | 0.097 | 0.075 | 1.000 | 0.000 | 0.696 | 0.156 | 0.040 |
| C5 / C9 | 0.332 | 0.325 | 0.275 | 0.117 | 0.089 | 0.987 | 0.013 | 0.870 | 0.168 | 0.040 |


## Simultaneous directional exposure
{
 "all_long_share": 0.017524190206926808,
 "all_short_share": 0.029954422481659315,
 "any_position_share": 0.6512101196714519,
 "max_simultaneous_same_direction": 4
}

## Regime overlap (expectancy in R by regime)
| regime | state | C2 | C3 | C5 | C9 |
|---|---|---|---|---|---|
| crisis | crisis (VIX>25) | -0.311 | -0.158 | -0.229 | -0.234 |
| crisis | normal | 0.147 | 0.095 | 0.077 | 0.178 |
| rates | falling yields | -0.006 | 0.069 | 0.105 | -0.029 |
| rates | rising yields | 0.171 | 0.054 | -0.028 | 0.281 |
| trend | ranging | -0.039 | 0.079 | 0.024 | 0.016 |
| trend | trending | 0.423 | -0.007 | 0.075 | 0.392 |
| usd | strong USD | 0.080 | 0.118 | 0.066 | 0.051 |
| usd | weak USD | 0.083 | -0.014 | 0.008 | 0.195 |
| vol | high vol | -0.088 | -0.114 | -0.148 | -0.229 |
| vol | low vol | 0.185 | 0.228 | 0.175 | 0.322 |


## Combined portfolio
| label | trades | expectancy_r | profit_factor | sharpe | sortino | cagr | max_dd | calmar | exposure | longest_underwater_days |
|---|---|---|---|---|---|---|---|---|---|---|
| portfolio, weights 1/4, limits ON | 1332 | 0.061 | 1.124 | 0.268 | 0.438 | 0.007 | 0.084 | 0.087 | 0.641 | 1239 |
| portfolio, 0.5% each, limits ON | 810 | 0.108 | 1.189 | 0.340 | 0.579 | 0.027 | 0.151 | 0.182 | 0.413 | 2164 |
| portfolio, 0.5% each, limits OFF | 1367 | 0.067 | 1.098 | 0.279 | 0.456 | 0.027 | 0.311 | 0.087 | 0.651 | 1239 |

risk-manager rejections (weighted run): {'spread too wide': 90}
meta (weighted run): {'halted': False, 'halt_reason': '', 'disabled': {}, 'open_positions_at_end': 2}
meta (0.5% each, limits ON): {'halted': True, 'halt_reason': 'portfolio drawdown stop at 2018-12-21 20:00:00', 'disabled': {}, 'open_positions_at_end': 0}


### Portfolio by year
| year | return | trades | win_rate | exp_r | pf |
|---|---|---|---|---|---|
| 2010 | -0.012 | 96 | 0.302 | -0.146 | 0.716 |
| 2011 | 0.027 | 98 | 0.439 | 0.284 | 1.647 |
| 2012 | -0.002 | 82 | 0.341 | -0.036 | 0.934 |
| 2013 | 0.032 | 89 | 0.371 | 0.314 | 1.677 |
| 2014 | 0.002 | 102 | 0.265 | 0.000 | 1.025 |
| 2015 | 0.020 | 91 | 0.363 | 0.187 | 1.331 |
| 2016 | 0.033 | 99 | 0.354 | 0.260 | 1.594 |
| 2017 | 0.029 | 92 | 0.391 | 0.088 | 1.191 |
| 2018 | -0.026 | 104 | 0.327 | -0.061 | 0.879 |
| 2019 | -0.002 | 91 | 0.264 | -0.099 | 0.822 |
| 2020 | 0.021 | 88 | 0.261 | 0.281 | 1.588 |
| 2021 | -0.025 | 94 | 0.234 | -0.241 | 0.598 |
| 2022 | -0.019 | 100 | 0.300 | -0.165 | 0.694 |
| 2023 | 0.028 | 106 | 0.406 | 0.203 | 1.435 |
