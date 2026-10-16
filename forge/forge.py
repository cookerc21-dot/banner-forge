#!/usr/bin/env python3
"""Forge engine — Agnes-powered token banner generator.

The API key is read ONLY from the AGNES_API_KEY environment variable
(GitHub Actions secret). It is never logged, echoed or written to disk.

Modes:
  forge.py --ca 0x... [--theme "..."] [--tag issue7] --out out
  forge.py --ticker TOKEN [--theme "..."] --out out
  forge.py --batch "$FORGE_BATCH" --out out/auto   # FORGE_BATCH="CA1|CA2|CA3"
"""
import argparse, json, os, re, sys, time, urllib.request

API = "https://apihub.agnes-ai.com/v1"
MODEL = "agnes-image-2.5-flash"
DEX = "https://api.dexscreener.com/latest/dex"

def dex_lookup(ca):
    """Best pair info for a CA -> (ticker, chain, theme hint)."""
    url = f"{DEX}/tokens/{ca}"
    req = urllib.request.Request(url, headers={"User-Agent": "banner-forge/1.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        d = json.loads(r.read().decode())
    pairs = d.get("pairs") or []
    best, bscore = None, -1
    for p in pairs:
        liq = ((p.get("liquidity") or {}).get("usd")) or 0
        vol = ((p.get("volume") or {}).get("h24")) or 0
        if liq + vol > bscore:
            best, bscore = p, liq + vol
    if not best:
        return None, None, None
    base = best.get("baseToken") or {}
    chg = ((best.get("priceChange") or {}).get("h24")) or 0
    theme_hint = "bullish green candle energy" if chg >= 0 else "stealth red and charcoal"
    return base.get("symbol") or "TOKEN", best.get("chainId"), theme_hint

def build_prompt(ticker, theme):
    t = re.sub(r"^[^A-Za-z0-9]+", "", ticker) or "TOKEN"
    th = theme or "premium crypto launch energy"
    return (
        f"Professional Web3 crypto token banner, dark premium style. Giant bold 3D chrome wordmark "
        f"'{t}' centered with neon glow accent, subtle hex grid pattern background, floating glass "
        f"3D coins and light particles, deep space gradient, cinematic rim lighting, ultra clean "
        f"composition, high contrast, no small text, no watermark, no URLs. Theme: {th}."
    )

def gen_image(prompt, out_path):
    key = os.environ.get("AGNES_API_KEY", "").strip()
    if not key:
        print("::error::AGNES_API_KEY not set — add it as an encrypted Actions secret")
        sys.exit(1)
    payload = json.dumps({"model": MODEL, "prompt": prompt, "n": 1}).encode()
    req = urllib.request.Request(API + "/images/generations", data=payload, method="POST")
    req.add_header("Authorization", "Bearer " + key)
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=180) as r:
        d = json.loads(r.read().decode())
    item = (d.get("data") or [{}])[0]
    if item.get("url"):
        urllib.request.urlretrieve(item["url"], out_path)
    elif item.get("b64_json"):
        import base64
        open(out_path, "wb").write(base64.b64decode(item["b64_json"]))
    else:
        raise RuntimeError("no image in response")
    return out_path

def slugify(s):
    return re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-").lower() or "token"

def forge_one(ca, ticker, theme, out_dir, tag):
    chain = None
    if ca and (not ticker or ticker == "TOKEN"):
        ticker, chain, hint = dex_lookup(ca)
        theme = theme or hint
    if not ticker:
        ticker = "TOKEN"
    ts = time.strftime("%Y%m%d-%H%M%S")
    fname = f"{slugify(ticker)}_{tag or ts}_{ts}.png"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, fname)
    prompt = build_prompt(ticker, theme)
    gen_image(prompt, out_path)
    meta = {"ticker": ticker, "chain": chain, "ca": ca or "", "theme": theme or "",
            "file": f"{out_dir}/{fname}", "prompt": prompt, "ts": ts}
    json.dump(meta, open(os.path.join(out_dir, "meta.json"), "w"), indent=1)
    print(f"FORGED {out_path}")
    return meta

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ca", default="")
    ap.add_argument("--ticker", default="")
    ap.add_argument("--theme", default="")
    ap.add_argument("--tag", default="")
    ap.add_argument("--out", default="out")
    ap.add_argument("--batch", default="", help="pipe-separated CAs for scheduled auto mode")
    a = ap.parse_args()

    if a.batch:
        cas = [c.strip() for c in a.batch.split("|") if c.strip()][:3]
        if not cas:
            print("FORGE_BATCH empty — nothing to do"); return
        metas = [forge_one(c, "", "", a.out, "auto") for c in cas]
        json.dump(metas, open(os.path.join(a.out, "meta.json"), "w"), indent=1)
    else:
        forge_one(a.ca, a.ticker, a.theme, a.out, a.tag)

if __name__ == "__main__":
    main()
