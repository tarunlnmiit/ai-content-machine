#!/usr/bin/env python3
"""macOS completion notifications for long-running pipelines.

Fail-silent by design: a notification must NEVER crash or block a pipeline —
any osascript error (missing binary, sandbox, timeout) is swallowed.

Usage:
    from lib.notify import notify
    notify("Blog pipeline", "All 7 stages complete")
"""

import subprocess


def _esc(text: str) -> str:
    """Escape for embedding inside an AppleScript double-quoted string."""
    return str(text).replace("\\", "\\\\").replace('"', '\\"')


def notify(title: str, message: str, sound: bool = True) -> None:
    """Show a macOS banner via `osascript -e 'display notification ...'`."""
    script = f'display notification "{_esc(message)}" with title "{_esc(title)}"'
    if sound:
        script += ' sound name "Glass"'
    try:
        subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            timeout=10,
            check=False,
        )
    except Exception:
        pass  # fail-silent: notifications are best-effort
