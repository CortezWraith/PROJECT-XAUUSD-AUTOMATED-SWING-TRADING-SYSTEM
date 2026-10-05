# Cross-strategy complementarity (DEV+OOS 2010-2023)


## Daily return correlation
|    |   C3 |   C2 |   C5 |
|:---|-----:|-----:|-----:|
| C3 | 1    | 0.45 | 0.34 |
| C2 | 0.45 | 1    | 0.43 |
| C5 | 0.34 | 0.43 | 1    |

## Pairwise overlap
| pair | corr_daily | time_in_market_a | time_in_market_b | overlap_share_of_time | overlap_expected_if_indep | same_direction_share_of_overlap | opposite_direction_share_of_overlap | drawdown_corr | joint_deep_dd_share | joint_deep_dd_if_indep |
|---|---|---|---|---|---|---|---|---|---|---|
| C3 / C2 | 0.451 | 0.271 | 0.452 | 0.182 | 0.122 | 1.000 | 0.000 | 0.699 | 0.141 | 0.040 |
| C3 / C5 | 0.341 | 0.271 | 0.325 | 0.113 | 0.088 | 0.987 | 0.013 | 0.684 | 0.161 | 0.040 |
| C2 / C5 | 0.427 | 0.452 | 0.325 | 0.188 | 0.147 | 0.989 | 0.011 | 0.670 | 0.148 | 0.040 |


## Simultaneous directional exposure
{
 "all_long_share": 0.04008140583489727,
 "all_short_share": 0.04405420556191962,
 "any_position_share": 0.6493577713324722,
 "max_simultaneous_same_direction": 3
}

## Regime overlap (expectancy in R by regime)
| regime | state | C3 | C2 | C5 |
|---|---|---|---|---|
| crisis | crisis (VIX>25) | -0.158 | -0.311 | -0.229 |
| crisis | normal | 0.095 | 0.147 | 0.077 |
| rates | falling yields | 0.069 | -0.006 | 0.105 |
| rates | rising yields | 0.054 | 0.171 | -0.028 |
| trend | ranging | 0.079 | -0.039 | 0.024 |
| trend | trending | -0.007 | 0.423 | 0.075 |
| usd | strong USD | 0.118 | 0.080 | 0.066 |
| usd | weak USD | -0.014 | 0.083 | 0.008 |
| vol | high vol | -0.114 | -0.088 | -0.148 |
| vol | low vol | 0.228 | 0.185 | 0.175 |


## Combined portfolio
| label | trades | expectancy_r | profit_factor | sharpe | sortino | cagr | max_dd | calmar | exposure | longest_underwater_days |
|---|---|---|---|---|---|---|---|---|---|---|
| portfolio, weights 1/3, limits ON | 1107 | 0.052 | 1.104 | 0.239 | 0.393 | 0.007 | 0.075 | 0.087 | 0.640 | 2164 |
| portfolio, 0.5% each, limits ON | 918 | 0.059 | 1.099 | 0.244 | 0.404 | 0.017 | 0.151 | 0.110 | 0.531 | 2164 |
| portfolio, 0.5% each, limits OFF | 1139 | 0.057 | 1.097 | 0.264 | 0.433 | 0.020 | 0.231 | 0.087 | 0.650 | 2164 |

risk-manager rejections (weighted run): {'spread too wide': 79}
meta (weighted run): {'halted': False, 'halt_reason': '', 'disabled': {}, 'open_positions_at_end': 1}
meta (0.5% each, limits ON): {'halted': True, 'halt_reason': 'portfolio drawdown stop at 2021-11-04 02:00:00', 'disabled': {'squeeze_h4': 'strategy drawdown 10.4%'}, 'open_positions_at_end': 0}


### Portfolio by year
| year | return | trades | win_rate | exp_r | pf |
|---|---|---|---|---|---|
| 2010 | -0.012 | 82 | 0.305 | -0.139 | 0.715 |
| 2011 | 0.017 | 79 | 0.443 | 0.190 | 1.456 |
| 2012 | -0.005 | 71 | 0.338 | -0.059 | 0.880 |
| 2013 | 0.025 | 76 | 0.342 | 0.227 | 1.433 |
| 2014 | 0.007 | 82 | 0.280 | 0.051 | 1.092 |
| 2015 | 0.019 | 74 | 0.378 | 0.168 | 1.308 |
| 2016 | 0.031 | 85 | 0.353 | 0.209 | 1.506 |
| 2017 | 0.038 | 75 | 0.413 | 0.162 | 1.373 |
| 2018 | -0.028 | 88 | 0.330 | -0.077 | 0.845 |
| 2019 | 0.003 | 75 | 0.293 | -0.013 | 0.975 |
| 2020 | 0.010 | 74 | 0.284 | 0.114 | 1.305 |
| 2021 | -0.021 | 77 | 0.247 | -0.172 | 0.680 |
| 2022 | -0.017 | 80 | 0.300 | -0.141 | 0.743 |
| 2023 | 0.029 | 89 | 0.404 | 0.203 | 1.420 |
