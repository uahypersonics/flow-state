"""Typer application for the flow-state command-line interface."""

from __future__ import annotations

from typing import Annotated

import typer

from flow_state.cli.callbacks import configure_logging, version_callback
from flow_state.cli.cmd_init import cmd_init
from flow_state.cli.cmd_solve import cmd_solve

app = typer.Typer(
    name="flow-state",
    help="Compute flow states.",
    add_completion=False,
    no_args_is_help=True,
)


@app.callback()
def main(
    version: Annotated[
        bool | None,
        typer.Option(
            "--version",
            "-V",
            help="Show version and exit.",
            callback=version_callback,
            is_eager=True,
        ),
    ] = None,
    debug: Annotated[
        bool,
        typer.Option("--debug", "-v", help="Enable verbose/debug output."),
    ] = False,
) -> None:
    """Compute flow states from freestream, stagnation, or atmospheric inputs."""

    del version
    configure_logging(debug)


app.command(name="init", rich_help_panel="Workflow")(cmd_init)
app.command(name="solve", rich_help_panel="Calculators")(cmd_solve)


if __name__ == "__main__":
    app()
