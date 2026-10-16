#!/usr/bin/env python3
"""Parse GitHub issue-form body -> GITHUB_OUTPUT (ca, ticker, theme).
Issue forms render as '### Label\n\n\nvalue\n\n---'."""
import os, re, sys

body = os.environ.get("ISSUE_BODY", "")

def section(label):
    m = re.search(rf"###\s*{re.escape(label)}\s*\n+([\s\S]*?)(?:\n\n---|\Z)", body, re.I)
    if not m:
        return ""
    v = m.group(1).strip()
    # drop "_No response_" placeholders
    if v.lower().startswith("_no response_"):
        return ""
    return v.splitlines()[0].strip()

ca = section("Token CA (contract address)") or section("Token CA")
theme = section("Theme (optional)") or section("Theme")
ticker = section("Wordmark (optional)") or ""

# basic sanity: CA-ish string (hex/base58)
if ca and not re.match(r"^[A-Za-z0-9:_\-]{20,80}$", ca):
    print(f"::warning::CA looks malformed: {ca[:12]}...")

out = []
out.append(f"ca={ca}")
out.append(f"ticker={ticker}")
out.append(f"theme={theme}")
print("\n".join(out))
