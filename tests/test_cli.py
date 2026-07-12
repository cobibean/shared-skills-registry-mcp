from __future__ import annotations

from shared_skills_registry_mcp import cli


def _capture_uvicorn(monkeypatch) -> dict:
    calls: dict = {}
    monkeypatch.setattr(cli.uvicorn, "run", lambda *args, **kwargs: calls.update(kwargs))
    return calls


def test_launcher_prints_control_panel_url_from_effective_settings(monkeypatch, capsys):
    calls = _capture_uvicorn(monkeypatch)
    monkeypatch.setenv("SSR_MCP_PORT", "18777")
    monkeypatch.delenv("SSR_MCP_BIND", raising=False)
    monkeypatch.delenv("SSR_MCP_AUTH_TOKEN", raising=False)

    cli.main()

    err = capsys.readouterr().err
    assert "Open SSR control panel: http://127.0.0.1:18777/ui" in err
    assert "WARNING" not in err
    assert calls["port"] == 18777
    assert calls["host"] == "127.0.0.1"


def test_launcher_warns_on_non_loopback_bind_without_token(monkeypatch, capsys):
    _capture_uvicorn(monkeypatch)
    monkeypatch.setenv("SSR_MCP_BIND", "192.168.1.10")
    monkeypatch.delenv("SSR_MCP_AUTH_TOKEN", raising=False)

    cli.main()

    err = capsys.readouterr().err
    assert "WARNING: non-loopback bind without SSR_MCP_AUTH_TOKEN" in err


def test_launcher_does_not_warn_when_token_is_set(monkeypatch, capsys):
    _capture_uvicorn(monkeypatch)
    monkeypatch.setenv("SSR_MCP_BIND", "192.168.1.10")
    monkeypatch.setenv("SSR_MCP_AUTH_TOKEN", "some-token-value")

    cli.main()

    err = capsys.readouterr().err
    assert "WARNING" not in err
