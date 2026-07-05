---
title: Home
layout: default
nav_order: 1
---

# geminpy

Google's `gemini` CLI wants you to open a browser, pick your account, and click
"Sign in" — every time. `geminpy` does that clicking for you.

It launches Chrome for Testing, runs `gemini` with your arguments, drives the
OAuth screens over the Chrome DevTools Protocol, and hands you back a clean
response. Your real browser is never touched, and your default browser is put
back exactly where it was.

macOS only.
{: .label .label-yellow }

## Three commands to get going

```bash
pip install geminpy                 # 1. install
playwright install chromium         # 2. one-time browser setup
geminpy -p "Explain Python decorators"   # 3. ask
```

The first run installs Chrome for Testing if it is missing. After that, every
call authenticates itself.

## What you get

- **Hands-off auth** — the OAuth dance runs without you.
- **Your browser, untouched** — Chrome for Testing stays isolated; your default
  browser is restored afterwards.
- **Rate-limit fallback** — a `429` triggers an automatic retry on
  `gemini-2.5-flash`.
- **Clean output** — authentication noise is stripped so scripts get the answer,
  not the login chatter.

## Where to next

- [Installation](installation.md) — prerequisites and setup.
- [Usage](usage.md) — CLI and Python examples.
- [How it works](how-it-works.md) — the four-phase automation flow.
- [API reference](api-reference.md) — the public functions.
