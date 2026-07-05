---
title: API reference
layout: default
nav_order: 5
---

# API reference

Three public functions cover the range from "just ask" to "hand me the raw CLI".
All are importable from the top-level `geminpy` package.

## `ask`

```python
def ask(
    prompt: str,
    user: str | None = None,
    model: str | None = None,
    verbose: bool = False,
    retry: bool = False,
) -> str
```

Ask Gemini a question and get a clean string back. Runs the async machinery for
you via `asyncio.run`, so call it from ordinary synchronous code.

| Argument  | Meaning |
|-----------|---------|
| `prompt`  | The question to send. |
| `user`    | Google account email. Defaults to the resolution order (see [Usage](usage.md)). |
| `model`   | Model name, or a shortcut: `"pro"` → `gemini-2.5-pro`, `"flash"` → `gemini-2.5-flash`. |
| `verbose` | Emit debug logging of the OAuth flow. |
| `retry`   | Retry on rate limits, falling back to `gemini-2.5-flash`. |

Raises `GeminiError` if authentication or the API call fails.

## `ask_async`

```python
async def ask_async(
    prompt: str,
    user: str | None = None,
    model: str | None = None,
    verbose: bool = False,
    retry: bool = False,
) -> str
```

The awaitable form of `ask`, for use inside an existing event loop. Same
arguments, same `GeminiError` on failure.

## `call_gemini_cli`

```python
async def call_gemini_cli(
    gemini_args: list[str],
    user: str | None = None,
    gemini_executable: str | Path = "gemini",
    quit_browser: bool = False,
    verbose: bool = False,
    retry: bool = False,
) -> str | None
```

The lowest-level entry point. Pass `gemini_args` straight through to the `gemini`
CLI — use this when you need flags beyond a single prompt.

| Argument            | Meaning |
|---------------------|---------|
| `gemini_args`       | Arguments forwarded verbatim to `gemini`. |
| `user`              | Google account email. |
| `gemini_executable` | Path to the `gemini` binary. Defaults to `"gemini"` on `PATH`. |
| `quit_browser`      | Quit Chrome for Testing after the run. |
| `verbose`           | Emit debug logging. |
| `retry`             | Retry on rate limits. |

Returns the clean response, or `None` if the call failed. Raises `GeminiError`
on setup problems (for example, a missing dependency).

## Exceptions

`GeminiError` is the base error raised by the API. Authentication-specific
failures raise `AuthenticationError`, a subclass. Both live in
`geminpy.core.exceptions`.
