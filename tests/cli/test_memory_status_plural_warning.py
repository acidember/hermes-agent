"""Regression tests for hermes memory status plural-provider warnings."""

from types import SimpleNamespace

from hermes_cli import memory_setup


def _run_status(monkeypatch, capsys, memory_config):
    monkeypatch.setattr(
        "hermes_cli.config.load_config",
        lambda: {"memory": memory_config},
    )
    monkeypatch.setattr(memory_setup, "_get_available_providers", lambda: [])

    memory_setup.cmd_status(SimpleNamespace())
    return capsys.readouterr().out


def test_status_reports_plural_providers_active_when_singular_blank(monkeypatch, capsys):
    out = _run_status(
        monkeypatch,
        capsys,
        {"provider": "", "providers": ["enzyme", "holographic"]},
    )

    assert "Provider:  (none" in out
    assert "Providers: enzyme, holographic" in out
    assert "memory.providers is active" in out
    assert "plural list is not active" not in out


def test_status_warns_plural_providers_override_singular_when_both_set(monkeypatch, capsys):
    out = _run_status(
        monkeypatch,
        capsys,
        {"provider": "honcho", "providers": ["enzyme", "holographic"]},
    )

    assert "Provider:  honcho" in out
    assert "Providers: enzyme, holographic" in out
    assert "memory.providers is active and overrides memory.provider (honcho)" in out
    assert "plural list is ignored" not in out


def test_status_has_no_plural_warning_for_singular_only(monkeypatch, capsys):
    out = _run_status(monkeypatch, capsys, {"provider": "honcho"})

    assert "Provider:  honcho" in out
    assert "memory.providers is configured" not in out
