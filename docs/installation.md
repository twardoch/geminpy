---
title: Installation
layout: default
nav_order: 2
---

# Installation

macOS only.
{: .label .label-yellow }

`geminpy` switches your default browser during authentication using a macOS-only
utility. It will not run on Linux or Windows.

## Prerequisites

```bash
# macdefaultbrowsy — flips the default browser and back again
brew install macdefaultbrowsy

# Chromium for Playwright (one-time)
playwright install chromium
```

Chrome for Testing itself is installed automatically on first run if it is
missing, using `@puppeteer/browsers`. You need Node.js available for that step.

## Install geminpy

```bash
pip install geminpy
```

Or, with [uv](https://docs.astral.sh/uv/):

```bash
uv pip install geminpy
```

## Verify

```bash
geminpy --help
```

If you see the CLI help, you are ready. Run your first prompt:

```bash
geminpy -p "Say hello"
```

The first authenticated call may take a moment while Chrome for Testing is
fetched. Subsequent calls reuse it.
