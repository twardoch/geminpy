---
title: Usage
layout: default
nav_order: 3
---

# Usage

## Command line

`geminpy` is a drop-in front for `gemini`. Pass the same arguments; it adds the
authentication.

```bash
# Ask a question
geminpy -p "Explain Python decorators"

# Pick a model (shortcuts: "pro", "flash")
geminpy -m pro -p "Write a Python function that reverses a string"

# Name the Google account to sign in with
geminpy --user you@gmail.com -p "Hello"

# Retry on rate limits (falls back to gemini-2.5-flash)
geminpy --retry -p "Summarise this file"

# Quit Chrome for Testing when finished
geminpy --quit-browser -p "What day is it?"

# See the full OAuth flow
geminpy --verbose -p "Hello world"
```

Interactive mode works too — omit `-p` and `gemini` runs as usual, with the
sign-in handled for you.

## Python

The simplest entry point is `ask`:

```python
from geminpy import ask

answer = ask("Explain quantum computing in simple terms")
print(answer)
```

Named account, model shortcut, and retry:

```python
from geminpy import ask

answer = ask(
    "Generate a Python function",
    user="you@gmail.com",
    model="pro",
    retry=True,
)
```

### Async

Inside an event loop, use `ask_async`:

```python
import asyncio
from geminpy import ask_async

async def main():
    answer = await ask_async("Help me debug this", verbose=True)
    print(answer)

asyncio.run(main())
```

### Full control

`call_gemini_cli` passes raw arguments straight to `gemini`:

```python
import asyncio
from geminpy import call_gemini_cli

async def main():
    response = await call_gemini_cli(
        gemini_args=["-m", "gemini-2.5-pro", "-p", "Your prompt here"],
        user="you@gmail.com",
        quit_browser=True,
        verbose=True,
    )
    print(response)

asyncio.run(main())
```

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
