---
title: How it works
layout: default
nav_order: 4
---

# How it works

Every call runs through four phases. If anything fails, the cleanup phase still
runs, so your default browser always ends up where it started.

## 1. Setup

- Check for Chrome for Testing; install it via `@puppeteer/browsers` if missing.
- Record your current default browser.
- Set Chrome for Testing as the temporary default so OAuth links open there, not
  in your everyday browser.

## 2. Authentication

- Launch Chrome for Testing with remote debugging on port 9222.
- Start the `gemini` CLI, which opens the Google OAuth URL in that Chrome.
- Connect to Chrome over the Chrome DevTools Protocol (CDP) with Playwright.
- Find the Google Accounts tab, pick your account, and click **Sign in**.

The account picker and sign-in button are the only screens driven automatically.
Nothing is typed; no password is entered or stored.

## 3. Execution

- Wait for the OAuth success redirect.
- Watch the `gemini` process. In non-interactive mode, stderr is scanned live for
  rate-limit signals (`429`, `Quota exceeded`, `rateLimitExceeded`).
- On a rate limit with `--retry`, the run restarts on `gemini-2.5-flash`.
- Parse stdout to strip authentication noise and return the clean answer.

## 4. Cleanup

- Restore the original default browser.
- Optionally quit Chrome for Testing (`--quit-browser`).
- Return the response text.

## Where things live

Settings persist in the macOS application-support directory:

```
~/Library/Application Support/com.twardoch.chrometesting/settings.json
```

It holds the Chrome for Testing path and your preferred email. It is written
automatically — no manual editing needed.

## When it breaks

**"Chrome CDP did not become available"**
: Another Chrome may be holding port 9222 without remote debugging. Check with
  `curl http://localhost:9222/json/version`.

**"macdefaultbrowsy utility missing"**
: Run `brew install macdefaultbrowsy`.

**Authentication fails**
: Re-run with `--verbose` to watch each step. Confirm the account has Gemini
  access.

**Rate limits persist**
: `--retry` already falls back to flash. Wait a few minutes and check your quota
  in the Google Cloud Console.
