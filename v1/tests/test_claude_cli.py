"""Unit tests for lib.claude_cli retry/backoff and cache short-circuit."""
import subprocess
import types

import pytest

from lib import claude_cli


class _FakeProc:
    def __init__(self, returncode, stdout="", stderr=""):
        self.returncode = returncode
        self._stdout = stdout
        self._stderr = stderr

    # for subprocess.run stub
    @property
    def stdout(self):
        return self._stdout

    @property
    def stderr(self):
        return self._stderr


@pytest.fixture(autouse=True)
def _no_sleep(monkeypatch):
    monkeypatch.setattr(claude_cli.time, "sleep", lambda *_a, **_k: None)


def test_retries_then_succeeds(monkeypatch):
    calls = {"n": 0}

    def fake_run(cmd, capture_output, text, timeout):
        calls["n"] += 1
        if calls["n"] < 3:
            return _FakeProc(returncode=1, stderr="transient")
        return _FakeProc(returncode=0, stdout="OK")

    monkeypatch.setattr(claude_cli.subprocess, "run", fake_run)

    out = claude_cli.call_claude("prompt-success", cache=False, retries=3)
    assert out == "OK"
    assert calls["n"] == 3


def test_raises_after_exhausting_retries(monkeypatch):
    calls = {"n": 0}

    def fake_run(cmd, capture_output, text, timeout):
        calls["n"] += 1
        return _FakeProc(returncode=1, stderr="always fails")

    monkeypatch.setattr(claude_cli.subprocess, "run", fake_run)

    with pytest.raises(RuntimeError):
        claude_cli.call_claude("prompt-fail", cache=False, retries=3)
    assert calls["n"] == 3


def test_timeout_is_retried(monkeypatch):
    calls = {"n": 0}

    def fake_run(cmd, capture_output, text, timeout):
        calls["n"] += 1
        if calls["n"] == 1:
            raise subprocess.TimeoutExpired(cmd, timeout)
        return _FakeProc(returncode=0, stdout="recovered")

    monkeypatch.setattr(claude_cli.subprocess, "run", fake_run)

    out = claude_cli.call_claude("prompt-timeout", cache=False, retries=3)
    assert out == "recovered"
    assert calls["n"] == 2


def test_cache_hit_skips_subprocess(monkeypatch):
    monkeypatch.setattr(claude_cli, "_cache_fresh", lambda *_a, **_k: True)

    key = claude_cli._cache_key(":" + ":" + "cached-prompt")
    key.write_text("cached-value")

    def boom(*_a, **_k):
        raise AssertionError("subprocess should not run on cache hit")

    monkeypatch.setattr(claude_cli.subprocess, "run", boom)

    out = claude_cli.call_claude("cached-prompt", cache=True)
    assert out == "cached-value"
