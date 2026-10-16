#!/usr/bin/env python3
"""Scheduled auto mode: fetch tokens born <30min ago (DexScreener boosts/profiles),
rank by traction, emit FORGE_BATCH="CA1|CA2|CA3" for forge.py --batch."""
import json, time, urllib.request

UA = {"User-Agent": "banner-forge/1.0"}
NOW = int(time.time() * 1000)
WINDOW_MIN = 30
TOP = 3

def get(url):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=15) as r:
            return json.loads(r.read().decode())
    except Exception:
        return None

addrs = []
for ep in ("token-boosts/latest/v1", "token-profiles/latest/v1"):
    for it in get(f"https://api.dexscreener.com/{ep}") or []:
        a = it.get("tokenAddress")
        if a:
            addrs.append(a)
seen = set()
addrs = [a for a in addrs if not (a in seen or seen.add(a))][:60]

cands = []
for i in range(0, min(len(addrs), 60), 30):
    d = get("https://api.dexscreener.com/latest/dex/tokens/" + ",".join(addrs[i:i+30]))
    for p in (d or {}).get("pairs") or []:
        created = p.get("pairCreatedAt") or 0
        age = (NOW - created) / 60000 if created else 1e9
        liq = ((p.get("liquidity") or {}).get("usd")) or 0
        vol = ((p.get("volume") or {}).get("h24")) or 0
        tx = ((p.get("txns") or {}).get("h24") or {}).get("buys") or 0
        base = p.get("baseToken") or {}
        if age <= WINDOW_MIN and liq >= 3000:
            cands.append({"ca": base.get("address"), "score": vol + tx * 100, "ticker": base.get("symbol")})
    time.sleep(0.3)

# dedup by ca, top by score
byca = {}
for c in cands:
    if c["ca"] and (c["ca"] not in byca or c["score"] > byca[c["ca"]]["score"]):
        byca[c["ca"]] = c
top = sorted(byca.values(), key=lambda c: -c["score"])[:TOP]
batch = "|".join(c["ca"] for c in top)
print(f"candidates: {[(c['ticker'], int(c['score'])) for c in top]}")
print(f"FORGE_BATCH={batch}")
