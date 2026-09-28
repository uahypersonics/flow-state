"""Tests for the flow-state command-line interface."""

from __future__ import annotations

import json

from typer.testing import CliRunner

from flow_state.cli import app, cli

runner = CliRunner()


def test_cli_alias_preserves_console_entry_point() -> None:
    """The historical ``flow_state.cli:cli`` entry point remains valid."""

    assert cli is app


def test_help_lists_commands_and_panels() -> None:
    """Top-level help presents the public command surface."""

    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "Calculators" in result.output
    assert "Workflow" in result.output
    assert "solve" in result.output
    assert "init" in result.output


def test_version_exits_successfully() -> None:
    """The eager version option does not require a command."""

    result = runner.invoke(app, ["--version"])

    assert result.exit_code == 0
    assert result.output.startswith("flow-state version ")


def test_init_creates_template(tmp_path) -> None:
    """The init command writes a usable starter configuration."""

    output_path = tmp_path / "flow_config.toml"
    result = runner.invoke(app, ["init", "--output", str(output_path)])

    assert result.exit_code == 0
    assert output_path.exists()
    assert "mach = 6.0" in output_path.read_text()


def test_init_refuses_to_overwrite_existing_file(tmp_path) -> None:
    """The init command protects existing configuration files."""

    output_path = tmp_path / "flow_config.toml"
    output_path.write_text("existing")
    result = runner.invoke(app, ["init", "--output", str(output_path)])

    assert result.exit_code == 1
    assert "Use --force to overwrite" in result.output
    assert output_path.read_text() == "existing"


def test_solve_reports_missing_config(tmp_path, monkeypatch) -> None:
    """The default workflow explains how to recover from a missing config."""

    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["solve"])

    assert result.exit_code == 1
    assert "flow_config.toml not found" in result.output
    assert "flow-state init" in result.output


def test_solve_direct_options_writes_json(tmp_path) -> None:
    """Direct inputs run the solver and write structured output."""

    output_path = tmp_path / "flow_state.json"
    result = runner.invoke(
        app,
        [
            "solve",
            "--mach",
            "2",
            "--pres",
            "101325",
            "--temp",
            "300",
            "--quiet",
            "--output",
            str(output_path),
        ],
    )

    assert result.exit_code == 0
    assert f"Wrote {output_path}" in result.output
    output_data = json.loads(output_path.read_text())
    assert output_data["mach"][0] == 2.0
