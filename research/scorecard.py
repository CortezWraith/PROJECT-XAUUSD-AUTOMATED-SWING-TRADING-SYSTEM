"""Literature-based candidate scorecard (written before any XAUUSD backtest was run).

Scores are 0-100 per criterion (higher = better; for cost sensitivity and
overfitting "higher" means *less* sensitive / *more* resistant; for data
requirements "higher" means *fewer* requirements). Each score is justified in
SCORE_NOTES and in the report (section 5).
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import RESULTS, fmt_table, save_json  # noqa: E402

WEIGHTS = {
    "evidence": 15, "rationale": 12, "regime_robustness": 12, "overfit_resistance": 12,
    "cost_robustness": 10, "clarity": 6, "sample_size": 8, "data_light": 5,
    "portability": 5, "xauusd_fit": 10, "risk_compat": 5,
}

# horizon_fit: does the natural holding period fit the project definition (4 h - 10 trading days)?
CANDIDATES = {
    "C1 tsmom_d1 (3m time-series momentum)": dict(evidence=85, rationale=75, regime_robustness=55, overfit_resistance=80, cost_robustness=85, clarity=90, sample_size=35, data_light=95, portability=95, xauusd_fit=60, risk_compat=70, horizon_fit=False),
    "C2 donchian_h4 (55/20 channel breakout)": dict(evidence=65, rationale=70, regime_robustness=50, overfit_resistance=75, cost_robustness=70, clarity=95, sample_size=70, data_light=95, portability=95, xauusd_fit=65, risk_compat=85, horizon_fit=True),
    "C3 ema_trend_h4 (20/100 EMA)": dict(evidence=60, rationale=70, regime_robustness=50, overfit_resistance=70, cost_robustness=70, clarity=95, sample_size=60, data_light=95, portability=95, xauusd_fit=60, risk_compat=75, horizon_fit=True),
    "C4 volbreak_d1 (range-expansion OCO)": dict(evidence=45, rationale=50, regime_robustness=40, overfit_resistance=55, cost_robustness=45, clarity=85, sample_size=85, data_light=95, portability=90, xauusd_fit=50, risk_compat=80, horizon_fit=True),
    "C5 squeeze_h4 (momentum after consolidation)": dict(evidence=30, rationale=45, regime_robustness=45, overfit_resistance=45, cost_robustness=60, clarity=85, sample_size=50, data_light=95, portability=95, xauusd_fit=50, risk_compat=80, horizon_fit=True),
    "C6 rsi2_pullback_d1 (trend-conditioned reversal)": dict(evidence=50, rationale=60, regime_robustness=55, overfit_resistance=60, cost_robustness=55, clarity=90, sample_size=60, data_light=95, portability=95, xauusd_fit=55, risk_compat=70, horizon_fit=True),
    "C7 zscore_mr_h1 (range-conditioned reversion)": dict(evidence=35, rationale=50, regime_robustness=35, overfit_resistance=45, cost_robustness=35, clarity=85, sample_size=90, data_light=95, portability=95, xauusd_fit=45, risk_compat=65, horizon_fit=True),
    "C8 session_drift_h1 (Asian-hours long / US-day short)": dict(evidence=65, rationale=60, regime_robustness=55, overfit_resistance=85, cost_robustness=40, clarity=95, sample_size=95, data_light=95, portability=70, xauusd_fit=80, risk_compat=85, horizon_fit=True),
    "C9 donchian_usd_h4 (USD-trend-filtered breakout)": dict(evidence=50, rationale=70, regime_robustness=40, overfit_resistance=55, cost_robustness=70, clarity=75, sample_size=50, data_light=50, portability=70, xauusd_fit=60, risk_compat=85, horizon_fit=True),
    "C10 autumn seasonal (long Sep+Nov)": dict(evidence=40, rationale=35, regime_robustness=40, overfit_resistance=60, cost_robustness=85, clarity=95, sample_size=10, data_light=95, portability=95, xauusd_fit=60, risk_compat=60, horizon_fit=False),
    "C11 ML direction classifier": dict(evidence=20, rationale=20, regime_robustness=20, overfit_resistance=10, cost_robustness=40, clarity=30, sample_size=80, data_light=60, portability=80, xauusd_fit=40, risk_compat=50, horizon_fit=True),
}

SCORE_NOTES = {
    "C1": "Strongest academic evidence (MOP 2012, HOP 2017, Han-Hu-Yang 2016) but holding weeks-months: outside the swing mandate -> benchmark only.",
    "C2": "Breakout = trend filter (Levine-Pedersen 2016). Negative: short-horizon trend decayed after 2009 on small-tick futures (Kurth-Eisler-Rej-Bouchaud 2026); gold is small-tick.",
    "C3": "Same economic bet as C2 (MA-cross ~ TSMOM); kept only as a control for C2.",
    "C4": "ORB evidence mostly crude oil / equity index intraday; little gold-specific peer-reviewed support; high turnover.",
    "C5": "Practitioner lore; volatility clustering is real but direction after a squeeze is not established.",
    "C6": "Gold contrarian next-day effect after abnormal moves (Caporale-Plastun 2019); short-term reversal well documented in futures; negative skew must be stop-controlled.",
    "C7": "Hourly reversion in ranges: high turnover, cost-dominated, regime definition fragile.",
    "C8": "Peer-reviewed gold-specific overnight-positive / day-negative effect (Blose-Gondhalekar-Kort 2018) + recent Asian-vs-US hours commentary; zero fitted parameters, but very cost-sensitive (~250 round trips/yr).",
    "C9": "USD-gold link is real but unstable (gold-real-yield link broke 2022-24); adds data dependency and a parameter.",
    "C10": "Baur 2013 autumn effect; ~2 trades/yr -> statistically untestable on 16 years; month-long holds.",
    "C11": "Excluded by mandate unless it improves a robust baseline without leakage; no such baseline yet.",
}


def score(c: dict) -> float:
    return sum(WEIGHTS[k] * c[k] for k in WEIGHTS) / sum(WEIGHTS.values())


def main() -> list[dict]:
    rows = []
    for name, c in CANDIDATES.items():
        r = {"candidate": name, "weighted": score(c), "horizon_fit": "yes" if c["horizon_fit"] else "NO"}
        r.update({k: c[k] for k in WEIGHTS})
        rows.append(r)
    rows.sort(key=lambda r: -r["weighted"])
    cols = ["candidate", "weighted", "horizon_fit"] + list(WEIGHTS)
    md = "Weights: " + ", ".join(f"{k} {v}%" for k, v in WEIGHTS.items()) + "\n\n" + fmt_table(rows, cols, "{:.1f}")
    md += "\n\nNotes:\n" + "\n".join(f"- {k}: {v}" for k, v in SCORE_NOTES.items())
    with open(os.path.join(RESULTS, "scorecard.md"), "w") as f:
        f.write(md)
    save_json("scorecard.json", rows)
    print(md)
    return rows


if __name__ == "__main__":
    main()
