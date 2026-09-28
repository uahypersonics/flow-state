"""Shared callbacks for the flow-state command-line interface."""

from __future__ import annotations

import logging

import typer

from flow_state import __version__


def configure_logging(debug: bool) -> None:
    """Configure console logging for CLI commands."""

    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=level, format="%(levelname)-8s %(message)s")


def version_callback(value: bool) -> None:
    """Print the installed package version and exit."""

    if value:
        typer.echo(f"flow-state version {__version__}")
        raise typer.Exit()
