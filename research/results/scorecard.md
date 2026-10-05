Weights: evidence 15%, rationale 12%, regime_robustness 12%, overfit_resistance 12%, cost_robustness 10%, clarity 6%, sample_size 8%, data_light 5%, portability 5%, xauusd_fit 10%, risk_compat 5%

| candidate | weighted | horizon_fit | evidence | rationale | regime_robustness | overfit_resistance | cost_robustness | clarity | sample_size | data_light | portability | xauusd_fit | risk_compat |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C1 tsmom_d1 (3m time-series momentum) | 73.7 | NO | 85 | 75 | 55 | 80 | 85 | 90 | 35 | 95 | 95 | 60 | 70 |
| C2 donchian_h4 (55/20 channel breakout) | 71.7 | yes | 65 | 70 | 50 | 75 | 70 | 95 | 70 | 95 | 95 | 65 | 85 |
| C8 session_drift_h1 (Asian-hours long / US-day short) | 71.5 | yes | 65 | 60 | 55 | 85 | 40 | 95 | 95 | 95 | 70 | 80 | 85 |
| C3 ema_trend_h4 (20/100 EMA) | 68.5 | yes | 60 | 70 | 50 | 70 | 70 | 95 | 60 | 95 | 95 | 60 | 75 |
| C6 rsi2_pullback_d1 (trend-conditioned reversal) | 62.7 | yes | 50 | 60 | 55 | 60 | 55 | 90 | 60 | 95 | 95 | 55 | 70 |
| C9 donchian_usd_h4 (USD-trend-filtered breakout) | 59.0 | yes | 50 | 70 | 40 | 55 | 70 | 75 | 50 | 50 | 70 | 60 | 85 |
| C4 volbreak_d1 (range-expansion OCO) | 58.8 | yes | 45 | 50 | 40 | 55 | 45 | 85 | 85 | 95 | 90 | 50 | 80 |
| C10 autumn seasonal (long Sep+Nov) | 55.7 | NO | 40 | 35 | 40 | 60 | 85 | 95 | 10 | 95 | 95 | 60 | 60 |
| C5 squeeze_h4 (momentum after consolidation) | 54.3 | yes | 30 | 45 | 45 | 45 | 60 | 85 | 50 | 95 | 95 | 50 | 80 |
| C7 zscore_mr_h1 (range-conditioned reversion) | 53.9 | yes | 35 | 50 | 35 | 45 | 35 | 85 | 90 | 95 | 95 | 45 | 65 |
| C11 ML direction classifier | 34.7 | yes | 20 | 20 | 20 | 10 | 40 | 30 | 80 | 60 | 80 | 40 | 50 |


Notes:
- C1: Strongest academic evidence (MOP 2012, HOP 2017, Han-Hu-Yang 2016) but holding weeks-months: outside the swing mandate -> benchmark only.
- C2: Breakout = trend filter (Levine-Pedersen 2016). Negative: short-horizon trend decayed after 2009 on small-tick futures (Kurth-Eisler-Rej-Bouchaud 2026); gold is small-tick.
- C3: Same economic bet as C2 (MA-cross ~ TSMOM); kept only as a control for C2.
- C4: ORB evidence mostly crude oil / equity index intraday; little gold-specific peer-reviewed support; high turnover.
- C5: Practitioner lore; volatility clustering is real but direction after a squeeze is not established.
- C6: Gold contrarian next-day effect after abnormal moves (Caporale-Plastun 2019); short-term reversal well documented in futures; negative skew must be stop-controlled.
- C7: Hourly reversion in ranges: high turnover, cost-dominated, regime definition fragile.
- C8: Peer-reviewed gold-specific overnight-positive / day-negative effect (Blose-Gondhalekar-Kort 2018) + recent Asian-vs-US hours commentary; zero fitted parameters, but very cost-sensitive (~250 round trips/yr).
- C9: USD-gold link is real but unstable (gold-real-yield link broke 2022-24); adds data dependency and a parameter.
- C10: Baur 2013 autumn effect; ~2 trades/yr -> statistically untestable on 16 years; month-long holds.
- C11: Excluded by mandate unless it improves a robust baseline without leakage; no such baseline yet.