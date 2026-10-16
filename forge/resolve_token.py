#!/usr/bin/env python3
"""Resolve CA -> TICKER/CHAIN/THEME via DexScreener. Emits GITHUB_ENV lines.
If CA empty and TICKER_IN set, just passes through."""
import json, os, urllib.request

ca = os.environ.get("CA", "").strip()
ticker_in = os.environ.get("TICKER_IN", "").strip()
theme_in = os.environ.get("THEME_IN", "").strip()

if not ca:
    print(f"TICKER={ticker_in or 'TOKEN'}")
    print(f"THEME={theme_in}")
    raise SystemExit(0)

try:
    req = urllib.request.Request(
        f"https://api.dexscreener.com/latest/dex/tokens/{ca}",
        headers={"User-Agent": "banner-forge/1.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        d = json.loads(r.read().decode())
    pairs = d.get("pairs") or []
    best, bscore = None, -1
    for p in pairs:
        liq = ((p.get("liquidity") or {}).get("usd")) or 0
        vol = ((p.get("volume") or {}).get("h24")) or 0
        if liq + vol > bscore:
            best, bscore = p, liq + vol
    base = (best or {}).get("baseToken") or {}
    chg = (((best or {}).get("priceChange") or {}).get("h24")) or 0
    hint = "bullish green candle energy" if chg >= 0 else "stealth red and charcoal"
    ticker = base.get("symbol") or ticker_in or "TOKEN"
    chain = (best or {}).get("chainId") or ""
except Exception as e:
    print(f"::warning::DexScreener lookup failed: {e}")
    ticker, chain, hint = ticker_in or "TOKEN", "", ""

theme = theme_in or hint
print(f"TICKER={ticker}")
print(f"CHAIN={chain}")
print(f"THEME={theme}")
