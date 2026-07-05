<!-- this_file: README.md -->

# geminpy

<img src="docs/assets/icon.png" align="right" width="180" alt="geminpy icon: a browser tipping its hat and handing over a key">

**Automated OAuth wrapper for Google's Gemini CLI on macOS.**

Google's `gemini` CLI wants you to open a browser, pick your account, and click
"Sign in" — every time. `geminpy` does that clicking for you. It launches Chrome
for Testing, runs `gemini` with your arguments, drives the OAuth screens over the
Chrome DevTools Protocol, and hands you back a clean response. Your everyday
browser is never touched, and your default browser is restored exactly as it was.

> **macOS only.** `geminpy` switches the default browser during sign-in using a
> macOS-only utility. It will not run on Linux or Windows.

Full documentation: **<https://twardoch.github.io/geminpy/>**

## Three commands to get going

```bash
pip install geminpy                       # 1. install
playwright install chromium               # 2. one-time browser setup
geminpy -p "Explain Python decorators"    # 3. ask
```

The first authenticated call installs Chrome for Testing if it is missing (via
`@puppeteer/browsers`, so Node.js must be available). Every call after that signs
in on its own.

## Why geminpy

- **Hands-off auth** — the OAuth dance runs without you.
- **Your browser, untouched** — Chrome for Testing stays isolated; your default
  browser is put back afterwards.
- **Rate-limit fallback** — a `429` triggers an automatic retry on
  `gemini-2.5-flash` (with `--retry`).
- **Clean output** — authentication noise is stripped, so scripts get the answer,
  not the login chatter.
- **Current model aliases** — `pro` and `flash` resolve to whatever your installed
  `gemini` CLI currently ships, not hard-coded IDs.

## Command line

`geminpy` is a drop-in front for `gemini` — pass the same arguments.

```bash
geminpy -p "Explain Python decorators"          # ask a question
geminpy -m pro -p "Write a reverse() function"  # model shortcut: pro / flash
geminpy --user you@gmail.com -p "Hello"         # name the Google account
geminpy --retry -p "Summarise this"             # retry on rate limits
geminpy --quit-browser -p "What day is it?"     # quit Chrome when finished
geminpy --verbose -p "Hello world"              # watch the OAuth flow
```

Omit `-p` for interactive mode — `gemini` runs as usual, sign-in handled for you.

## Python

```python
from geminpy import ask

answer = ask("Explain quantum computing in simple terms")
print(answer)

# Named account, model shortcut, retry
answer = ask("Generate a Python function", user="you@gmail.com", model="pro", retry=True)
```

Inside an event loop, use `ask_async`. For raw `gemini` arguments, use
`call_gemini_cli`. See the [API reference](https://twardoch.github.io/geminpy/api-reference.html).

## Choosing an account

`geminpy` resolves the Google account in this order:

1. The `--user` argument (or `user=` in Python).
2. The `GEMINI_CLI_USER` environment variable.
3. The account stored from your last successful sign-in.
4. The first Google account it finds.

```bash
export GEMINI_CLI_USER="you@gmail.com"
geminpy -p "Now I don't need --user"
```

## Requirements

- **Platform**: macOS (Darwin).
- **Python**: 3.10 or newer.
- **Tools**: `brew install macdefaultbrowsy`, then `playwright install chromium`.
- **Node.js**: needed for the one-time Chrome for Testing install.

## How it works

Every call runs four phases — setup, authentication, execution, cleanup — and the
cleanup phase always runs, so your default browser ends up where it started. The
full walkthrough, including troubleshooting, lives in
[How it works](https://twardoch.github.io/geminpy/how-it-works.html).

## Development

Built with [Hatch](https://hatch.pypa.io/).

```bash
hatch run test:test        # run tests (all browser/network calls are mocked)
hatch run lint:style       # ruff check + format
hatch run lint:typing      # mypy
hatch build                # build wheel + sdist
```

CI runs the mocked test suite on macOS and Linux across Python 3.10–3.12. Tagging
`vX.Y.Z` builds and publishes to PyPI and GitHub Releases.

## License

MIT — see [LICENSE](LICENSE).
