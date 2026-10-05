"""Build the processed research datasets from the raw sources (see fetch_data.sh).

Outputs (data/processed/):
    A_{TF}.parquet   Dukascopy bid/ask, server time, TF in M30,H1,H2,H3,H4,H6,D1
    B_{TF}.parquet   MT4 broker bid + modelled ask, server time, TF in H1,H2,H3,H4,H6,D1
    macro_daily.parquet  vix, usd_index (DXY-weighted, H.10), ust_3m, ust_2y, ust_10y
    data_quality.json    coverage / gaps / spread statistics

The spread model used to synthesise ask prices for dataset B is estimated on
dataset A over 2016-09-01 .. 2018-12-31 only (inside the development window),
so no out-of-sample information leaks into the development data.
"""
from __future__ import annotations

import glob
import json
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from tradingsystem.data.bars import resample_bidask, m1_utc_to_server  # noqa: E402

RAW = os.environ.get("XTS_RAW", os.path.join(ROOT, "data", "raw"))
OUT = os.path.join(ROOT, "data", "processed")
TFS_A = ["M30", "H1", "H2", "H3", "H4", "H6", "D1"]
TFS_B = ["H1", "H2", "H3", "H4", "H6", "D1"]
SPREAD_CAL = ("2016-09-01", "2018-12-31")


def find(*cands: str) -> str:
    for c in cands:
        hits = glob.glob(c)
        if hits:
            return hits[0]
    raise FileNotFoundError(cands)


def load_a_m1() -> pd.DataFrame:
    files = sorted(glob.glob(os.path.join(RAW, "dukascopy_m1", "XAUUSD_M1_*.csv")))
    if not files:
        raise FileNotFoundError("dataset A not found - run research/fetch_data.sh")
    df = pd.concat([pd.read_csv(f, engine="pyarrow") for f in files], ignore_index=True)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp").drop_duplicates("timestamp").set_index("timestamp")
    df["volume"] = df["volume_bid"] + df["volume_ask"]
    df = df.drop(columns=["volume_bid", "volume_ask"])
    return df


def build_a(quality: dict) -> pd.DataFrame:
    m1 = load_a_m1()
    spread = m1["close_ask"] - m1["close_bid"]
    quality["A"] = {
        "source": "Dypoi/XAUUSD_Dataset (Dukascopy-format M1 bid/ask)",
        "timezone": "UTC (verified: Sunday open 22:00/23:00 UTC, Friday close 21:00/22:00 UTC)",
        "price_type": "bid and ask OHLC per minute",
        "first": str(m1.index.min()), "last": str(m1.index.max()),
        "rows_m1": int(len(m1)),
        "negative_spreads": int((spread < 0).sum()),
        "spread_usd_median_by_year": spread.groupby(m1.index.year).median().round(3).to_dict(),
        "spread_bps_median_by_year": (spread / m1["close_bid"] * 1e4).groupby(m1.index.year).median().round(2).to_dict(),
    }
    srv = m1_utc_to_server(m1)
    srv["source"] = "A"
    # weekday gaps longer than 2h (outside the daily break / weekend) = missing data
    idx = srv.index.to_series()
    gaps = idx.diff()
    wk = gaps[(gaps > pd.Timedelta("2h")) & (gaps < pd.Timedelta("40h"))]
    quality["A"]["weekday_gaps_over_2h"] = int(len(wk))
    quality["A"]["weekday_gaps_examples"] = [str(t) for t in wk.sort_values().tail(8).index]
    out = {}
    for tf in TFS_A:
        bars = resample_bidask(srv, tf)
        bars.to_parquet(os.path.join(OUT, f"A_{tf}.parquet"))
        out[tf] = bars
        quality["A"][f"bars_{tf}"] = int(len(bars))
    return out["H1"]


def build_b(a_h1: pd.DataFrame, quality: dict) -> None:
    path = os.path.join(RAW, "mt4_h1", "XAU_1h_data.csv")
    b = pd.read_csv(path, sep=";")
    b["Date"] = pd.to_datetime(b["Date"], format="%Y.%m.%d %H:%M")
    b = b.set_index("Date").sort_index()
    b = b[~b.index.duplicated()]
    b = b.rename(columns={"Open": "open_bid", "High": "high_bid", "Low": "low_bid", "Close": "close_bid", "Volume": "volume"})
    # MT4 server time is already NY+7 (verified by return correlation with dataset A).
    cal = a_h1.loc[SPREAD_CAL[0]:SPREAD_CAL[1]]
    sp_bps = ((cal["close_ask"] - cal["close_bid"]) / cal["close_bid"] * 1e4).groupby(cal.index.hour).median()
    for c in ("open", "high", "low", "close"):
        b[f"{c}_ask"] = b[f"{c}_bid"] * (1.0 + b.index.hour.map(sp_bps).astype(float).values * 1e-4)
    b["source"] = "B"
    b = b[b.index.dayofweek < 5]
    # consistency check vs A on the development overlap only
    ov = pd.concat([np.log(b["close_bid"]).diff().rename("b"), np.log(a_h1["close_bid"]).diff().rename("a")], axis=1, join="inner")
    ov = ov.loc[SPREAD_CAL[0]:SPREAD_CAL[1]].dropna()
    lvl = pd.concat([b["close_bid"].rename("b"), a_h1["close_bid"].rename("a")], axis=1, join="inner").loc[SPREAD_CAL[0]:SPREAD_CAL[1]].dropna()
    quality["B"] = {
        "source": "FeziweMelvin/XAUUSD-Gold-Price (MetaTrader 4 export, nvn01 script)",
        "timezone": "broker server time = New York + 7h (GMT+2/+3); verified by H1 return correlation vs A",
        "price_type": "bid OHLC; ask synthesised with A's median spread (bps) by server hour, 2016-09..2018-12",
        "first": str(b.index.min()), "last": str(b.index.max()), "rows_h1": int(len(b)),
        "h1_return_corr_vs_A_2016_09_2018_12": round(float(ov.corr().iloc[0, 1]), 4),
        "median_abs_price_diff_vs_A_usd": round(float((lvl["b"] - lvl["a"]).abs().median()), 3),
        "modelled_spread_bps_by_server_hour": sp_bps.round(2).to_dict(),
    }
    for tf in TFS_B:
        bars = b if tf == "H1" else resample_bidask(b, tf)
        bars.to_parquet(os.path.join(OUT, f"B_{tf}.parquet"))
        quality["B"][f"bars_{tf}"] = int(len(bars))


def build_macro(quality: dict) -> None:
    vix = pd.read_csv(os.path.join(RAW, "vix", "data", "vix-daily.csv"), parse_dates=["DATE"]).set_index("DATE")["CLOSE"].rename("vix")
    fx = pd.read_csv(os.path.join(RAW, "fx_h10", "data", "daily.csv"), parse_dates=["Date"])
    fx = fx.pivot_table(index="Date", columns="Country", values="Exchange rate")
    # all H.10 series here are quoted as foreign currency per USD -> DXY weights with + sign
    w = {"Euro": 0.576, "Japan": 0.136, "United Kingdom": 0.119, "Canada": 0.091, "Sweden": 0.042, "Switzerland": 0.036}
    sub = fx[list(w)].dropna()
    usd = 50.14348112 * np.exp(sum(wt * np.log(sub[c]) for c, wt in w.items()))
    ust = pd.read_csv(os.path.join(RAW, "ust_curve", "data", "us_treasury_yield_curve_history.csv"), parse_dates=["date"]).set_index("date")
    ust = ust[["3M", "2Y", "10Y"]].rename(columns={"3M": "ust_3m", "2Y": "ust_2y", "10Y": "ust_10y"}) / 100.0
    macro = pd.concat([vix, usd.rename("usd_index"), ust], axis=1).sort_index()
    macro = macro.loc["2000-01-01":]
    macro.to_parquet(os.path.join(OUT, "macro_daily.parquet"))
    quality["macro"] = {
        "vix": "CBOE VIX close via github.com/datasets/finance-vix",
        "usd_index": "DXY-weighted geometric index from Fed H.10 noon rates via github.com/datasets/exchange-rates",
        "ust": "US Treasury daily par yield curve via github.com/fujiapple852/yield",
        "usage": "all macro values are lagged by one business day before use (publication timing)",
        "first": str(macro.index.min()), "last": str(macro.index.max()),
        "missing_share": macro.isna().mean().round(4).to_dict(),
    }


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    quality: dict = {}
    a_h1 = build_a(quality)
    build_b(a_h1, quality)
    build_macro(quality)
    with open(os.path.join(OUT, "data_quality.json"), "w") as f:
        json.dump(quality, f, indent=2, default=str)
    os.makedirs(os.path.join(ROOT, "research", "results"), exist_ok=True)
    with open(os.path.join(ROOT, "research", "results", "data_quality.json"), "w") as f:
        json.dump(quality, f, indent=2, default=str)
    print(json.dumps(quality, indent=2, default=str)[:4000])


if __name__ == "__main__":
    main()
