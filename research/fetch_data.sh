#!/usr/bin/env bash
# Download the raw research datasets (public GitHub mirrors) into data/raw/.
# Raw data is NOT committed to this repository (size + third-party licensing).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
RAW="$ROOT/data/raw"
mkdir -p "$RAW"
clone() {  # clone <github owner/repo> <dir>
  if [ ! -d "$RAW/$2/.git" ]; then
    GIT_LFS_SKIP_SMUDGE=1 git clone --depth 1 "https://github.com/$1" "$RAW/$2"
  fi
}
# A: Dukascopy-format XAUUSD M1 bid/ask, UTC, 2016-09-01 .. 2026-09-01
clone Dypoi/XAUUSD_Dataset dukascopy_m1
# B: MetaTrader 4 broker XAUUSD H1/D1 (bid), server time GMT+2/+3, 2004-06 .. 2025-06
clone FeziweMelvin/XAUUSD-Gold-Price mt4_h1
# C: MetaTrader 5 broker XAUUSD H1 (bid, integer-scaled), 2012-05 .. 2022-03 (cross-check only)
clone ejtraderLabs/historical-data mt5_ejtrader
# Macro: VIX (CBOE via DataHub), FX H.10 (FRED via DataHub), daily US Treasury par curve
clone datasets/finance-vix vix
clone datasets/exchange-rates fx_h10
clone fujiapple852/yield ust_curve
echo "raw data in $RAW"
