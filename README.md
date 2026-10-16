# 🔥 banner-forge

**Forge a token banner on the spot — free.** Powered by the EYE banner studio.

No waiting, no DMs. Open one issue, the AI forges your banner in ~2 minutes
and posts it right back into the issue.

## How to use (30 seconds)

1. **[Open a Forge request](../../issues/new?template=forge-request.yml)**
2. Paste your **token CA** (contract address) — we auto-pull the ticker & chain from DexScreener
3. (Optional) add a few **theme words** — e.g. `golden dragon treasure`, `neon cyberpunk city`
4. Submit. The forge bot commits your banner to [`out/`](./out) and comments on your issue with the image.

Want a different vibe? **Edit your issue body** (theme words) and the forge re-runs automatically.

## What you get

| File | Use |
|---|---|
| `out/<TICKER>_<ts>.png` | AI-forged banner, post-ready for X / Telegram / DEX update requests |

Fresh launches: the forge also runs **every 30 minutes** on its own — it auto-fetches
tokens born in the last 30 minutes from DexScreener and forges banners for the
highest-traction ones into `out/auto/`. If your coin is brand new, there's a good
chance your banner is already here — browse [`out/auto/`](./out/auto).

## Prefer a human-crafted one?

Order the hand-tuned dex banner (exact 1920×640, VLM-checked lettering) in 30 seconds:
**https://cookerc21-dot.github.io** — or just mention **@aikitapp** on X.

## Security

The generation key lives **only** in encrypted repository Actions secrets
(`AGNES_API_KEY`). It is never written into code, logs, issues or commits.

---
*Banner outputs are AI-generated previews — free to use for your token's socials.*
