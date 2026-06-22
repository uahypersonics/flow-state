"""
Command-line interface for flow_state.

Commands:
    flow-state init     - Generate a template config file (flow_config.toml)
    flow-state examples - List or copy bundled example configs
    flow-state solve    - Compute flow state from config, output to JSON
"""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------

from __future__ import annotations

import logging
from importlib.metadata import version as _pkg_version
from pathlib import Path
from typing import Annotated

import typer

from flow_state.io import read_config, write_flow_conditions_dat, write_json
from flow_state.solvers import solve

# read version from installed package metadata (set by git tag via setuptools-scm)
__version__ = _pkg_version("flow-state-calculator")

# --------------------------------------------------
# default file names
# --------------------------------------------------

# set a default config file name
DEFAULT_CONFIG = "flow_config.toml"
# set a default output file name
DEFAULT_OUTPUT = "flow_state.json"


# --------------------------------------------------
# set up cli using typer (reference: https://typer.tiangolo.com/)
# --------------------------------------------------

cli = typer.Typer(
    # set name of cli command
    name="flow-state",
    # set help text shown when running `flow-state --help`
    help="Compute flow state",
    # disable shell completion command (not needed for this rudimentary cli)
    add_completion=False,
    # show help when no command is given
    no_args_is_help=True,
)


# --------------------------------------------------
# module-level logger
# --------------------------------------------------

logger = logging.getLogger(__name__)


# --------------------------------------------------
# helper: configure console logging
# --------------------------------------------------


def _configure_logging(debug: bool) -> None:
    """Configure root logger level and format."""
    # set DEBUG level when -v is passed, otherwise INFO
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(levelname)-8s %(message)s",
    )


# --------------------------------------------------
# version callback
# --------------------------------------------------

# define a callback function to print version and exit when --version is used
# this function is called by typer when the --version option is passed
def version_callback(value: bool) -> None:
    """Print version and exit"""
    # only run if --version was actually passed (value=True)
    if value:
        # print version to stdout
        typer.echo(f"flow-state version {__version__}")
        # exit with code 0 (success): nothing else to do after printing version
        raise typer.Exit()


# --------------------------------------------------
# cli callback (runs before any command)
# --------------------------------------------------

# the @cli.callback() decorator marks this function to run on every cli invocation
# this is where we handle global options like --version that apply to all commands
# without this, --version would only work if attached to a specific command
@cli.callback()
def main(
    # version option:
    # - whether to print version and exit
    # - type: bool | None (None means not provided)
    # - cli flags to set this option: --version or -v
    # - callback: version_callback runs immediately when this option is passed
    # - is_eager: True means run callback before parsing other arguments
    #   (so `flow-state --version solve --config missing.toml` still works)
    # - default if option not provided in cli: None (do nothing)
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
    # debug option:
    # - enables verbose output: resolved inputs, builder selected, provenance
    # - cli flags: --debug or -v
    debug: Annotated[
        bool,
        typer.Option(
            "--debug",
            "-v",
            help="Enable verbose/debug output.",
        ),
    ] = False,
) -> None:
    """flow-state: Compute flow states"""
    # configure logging level based on --debug flag
    _configure_logging(debug)
    # pass means "do nothing" - the callback just handles --version
    # actual work happens in the commands (init, solve)
    pass


# --------------------------------------------------
# template for flow_config.toml
# --------------------------------------------------

CONFIG_TEMPLATE = '''\
# flow_state configuration file
# =============================
# Edit the values below and run: flow-state solve

# Supported units:
#   pressure    : Pa, psi, atm, bar, torr
#   temperature : K, C, F, R (Rankine)
#   length      : m, ft, km, mi
#   velocity    : m/s, ft/s, kts, mph, kph

# Use [value, "unit"] tuples for non-SI units, e.g.:
#   pres_stag = [140, "psi"]
#   altitude = [30000, "ft"]

# --------------------------------------------------
# Input mode: Choose ONE of the following sections
# --------------------------------------------------

# Option 1: Mach + stagnation conditions (wind tunnel)
mach = 6.0
pres_stag = [140, "psi"]  # or 965266.0 for Pa
temp_stag = 420           # Kelvin

# Option 2: Altitude + Mach (flight conditions)
# altitude = [30000, "ft"]
# mach = 0.8

# Option 3: Static conditions
# pres = 101325    # Pa
# temp = 300       # K
# mach = 2.0

# --------------------------------------------------
# Reference length scale (for turbulence scales)
# --------------------------------------------------
lref = 1.0  # [m]

# --------------------------------------------------
# Gas model (optional, default: "air")
# --------------------------------------------------
# gas = "air"       # calorically perfect air (gamma=1.4, R=287.05)
# gas = "n2"        # nitrogen (gamma=1.4, R=296.8, Sutherland nitrogen)

# --------------------------------------------------
# Optional notes
# --------------------------------------------------
# notes = "BAM6QT Mach 6 tunnel conditions"
'''


# --------------------------------------------------
# examples command: list or copy bundled example config files
# --------------------------------------------------


@cli.command("examples")
def cmd_examples(
    # name option:
    # - short name of the example to copy (e.g. "bam6qt")
    # - if omitted, command lists all available examples
    # - cli flags: --name or -n
    name: Annotated[
        str | None,
        typer.Option(
            "--name", "-n",
            help="Example name to copy (e.g. bam6qt). Omit to list all.",
        ),
    ] = None,
    # output option:
    # - path to write the copied config file
    # - default: flow_config.toml in CWD
    # - cli flags: --output or -o
    output: Annotated[
        Path,
        typer.Option(
            "--output", "-o",
            help="Output config file path",
        ),
    ] = Path(DEFAULT_CONFIG),
    # force option:
    # - whether to overwrite an existing output file
    # - cli flags: --force or -f
    force: Annotated[
        bool,
        typer.Option(
            "--force", "-f",
            help="Overwrite existing file",
        ),
    ] = False,
) -> None:
    """
    List available example configs, or copy one to the current directory.
    """
    # import helpers here to keep top-level imports light
    from flow_state.io.examples import available_example_names, get_example_text, list_examples

    # -- list mode: no name provided, print all examples --
    if name is None:
        examples = list_examples()
        typer.echo("Available examples:")
        typer.echo("")
        for ex_name, desc in examples.items():
            typer.echo(f"  {ex_name:<20} {desc}")
        typer.echo("")
        typer.echo("Copy an example:  flow-state examples --name <name>")
        return

    # -- copy mode: resolve name and write to output file --

    # validate name against registry
    if name.lower() not in available_example_names():
        valid = ", ".join(available_example_names())
        typer.echo(f"Error: unknown example '{name}'. Available: {valid}", err=True)
        raise typer.Exit(1)

    # check for existing output file
    if output.exists() and not force:
        typer.echo(f"Error: {output} already exists. Use --force to overwrite.", err=True)
        raise typer.Exit(1)

    # read bundled TOML and write to output path
    text = get_example_text(name)
    output.write_text(text)
    typer.echo(f"Created {output}")
    typer.echo("Edit the file, then run: flow-state solve")


# --------------------------------------------------
# register cli command "init"
#
# init is used to generate a template config file (flow_config.toml) with example inputs and documentation
#
# NOTE: in typer, the function signature is the cli interface:
# - each parameter becomes a cli option (--name) or argument
# - type hints define validation and conversion
# - typer.Option() sets flag names, help text, etc
# - default values make options optional
# - the docstring becomes the help text for the command
# --------------------------------------------------

# register command using a decorator
@cli.command("init")
# define function for "init" command
def cmd_init(
    # output option:
    # - set path to write the config file
    # - type: Path (automatically validated)
    # - cli flags to set this option: --output or -o
    # - default if option not provided in cli: flow_config.toml
    output: Annotated[
        Path,
        typer.Option(
            "--output", "-o",
            help="Output config file path",
        ),
    ] = Path(DEFAULT_CONFIG),
    # force option:
    # - whether to overwrite existing file
    # - type: bool (becomes a flag, no value needed)
    # - cli flags to set this option: --force or -f
    # - default if option not provided in cli: False (don't overwrite)
    force: Annotated[
        bool,
        typer.Option(
            "--force", "-f",
            help="Overwrite existing file",
        ),
    ] = False,
) -> None:
    """
    Generate a template configuration file (flow_config.toml) with example inputs and documentation
    """
    if output.exists() and not force:
        typer.echo(f"Error: {output} already exists. Use --force to overwrite", err=True)
        raise typer.Exit(1)

    output.write_text(CONFIG_TEMPLATE)
    typer.echo(f"Created {output}")
    typer.echo("Edit the file, then run: flow-state solve")


# --------------------------------------------------
# solve command: compute flow state from config or direct options
# --------------------------------------------------


@cli.command("solve")
def cmd_solve(
    # ----- Direct input options -----
    mach: Annotated[
        float | None,
        typer.Option(
            "--mach", "-m",
            help="Mach number",
        ),
    ] = None,
    pres_stag: Annotated[
        float | None,
        typer.Option(
            "--pres-stag",
            help="Stagnation pressure (default: Pa)",
        ),
    ] = None,
    pres_stag_unit: Annotated[
        str | None,
        typer.Option(
            "--pres-stag-unit",
            help="Stagnation pressure unit (Pa, psi, atm, bar)",
        ),
    ] = None,
    temp_stag: Annotated[
        float | None,
        typer.Option(
            "--temp-stag",
            help="Stagnation temperature (K)",
        ),
    ] = None,
    altitude: Annotated[
        float | None,
        typer.Option(
            "--altitude", "-a",
            help="Altitude (default: m)",
        ),
    ] = None,
    altitude_unit: Annotated[
        str | None,
        typer.Option(
            "--altitude-unit",
            help="Altitude unit (m, ft, km)",
        ),
    ] = None,
    pres: Annotated[
        float | None,
        typer.Option(
            "--pres",
            help="Static pressure (default: Pa)",
        ),
    ] = None,
    pres_unit: Annotated[
        str | None,
        typer.Option(
            "--pres-unit",
            help="Static pressure unit (Pa, psi, atm, bar)",
        ),
    ] = None,
    temp: Annotated[
        float | None,
        typer.Option(
            "--temp",
            help="Static temperature (default: K)",
        ),
    ] = None,
    temp_unit: Annotated[
        str | None,
        typer.Option(
            "--temp-unit",
            help="Static temperature unit (K, C, F, R)",
        ),
    ] = None,
    re1: Annotated[
        float | None,
        typer.Option(
            "--re1",
            help="Unit Reynolds number [1/m]",
        ),
    ] = None,
    gas: Annotated[
        str | None,
        typer.Option(
            "--gas",
            help="Gas type (air, n2)",
        ),
    ] = None,
    atm: Annotated[
        str | None,
        typer.Option(
            "--atm",
            help="Atmosphere model (ussa76, cira86)",
        ),
    ] = None,
    lref: Annotated[
        float | None,
        typer.Option(
            "--lref",
            help="Reference length (m)",
        ),
    ] = None,
    # ----- Config file option -----
    config: Annotated[
        Path | None,
        typer.Option(
            "--config", "-c",
            help="Input config file (TOML). Ignored if direct options provided.",
        ),
    ] = None,
    # ----- Output options -----
    output: Annotated[
        Path,
        typer.Option(
            "--output", "-o",
            help="Output file (JSON). Defaults to flow_conditions.json in the current directory.",
        ),
    ] = Path("flow_conditions.json"),
    dat: Annotated[
        bool,
        typer.Option(
            "--dat",
            help="Write legacy .dat file (flow_conditions.dat).",
        ),
    ] = False,
    quiet: Annotated[
        bool,
        typer.Option(
            "--quiet", "-q",
            help="Suppress summary output.",
        ),
    ] = False,
) -> None:
    """
    Compute flow state from direct options or config file.

    Examples:
        flow-state solve --mach 6 --pres-stag 140 --pres-stag-unit psi --temp-stag 420
        flow-state solve --mach 7 --altitude 25000
        flow-state solve --mach 8 --re1 10e6 --temp 55
        flow-state solve --config myconfig.toml
    """
    # Check if any direct options are provided
    has_direct_options = any([mach, pres_stag, temp_stag, altitude, pres, temp, re1])

    if has_direct_options:
        # Build kwargs from direct options
        kwargs = {}
        if mach is not None:
            kwargs["mach"] = mach
        if pres_stag is not None:
            if pres_stag_unit:
                kwargs["pres_stag"] = (pres_stag, pres_stag_unit)
            else:
                kwargs["pres_stag"] = pres_stag
        if temp_stag is not None:
            kwargs["temp_stag"] = temp_stag
        if altitude is not None:
            if altitude_unit:
                kwargs["altitude"] = (altitude, altitude_unit)
            else:
                kwargs["altitude"] = altitude
        if pres is not None:
            if pres_unit:
                kwargs["pres"] = (pres, pres_unit)
            else:
                kwargs["pres"] = pres
        if temp is not None:
            if temp_unit:
                kwargs["temp"] = (temp, temp_unit)
            else:
                kwargs["temp"] = temp
        if re1 is not None:
            kwargs["re1"] = re1
        if gas is not None:
            kwargs["gas"] = gas
        if atm is not None:
            kwargs["atm"] = atm
        if lref is not None:
            kwargs["lref"] = lref
    else:
        # Fall back to config file
        config_path = config if config else Path(DEFAULT_CONFIG)
        if not config_path.exists():
            typer.echo(f"Error: {config_path} not found.", err=True)
            typer.echo("Provide direct options (--mach, etc.) or run 'flow-state init' to create a config.", err=True)
            raise typer.Exit(1)

        try:
            kwargs = read_config(config_path)
        except Exception as e:
            typer.echo(f"Error parsing {config_path}: {e}", err=True)
            raise typer.Exit(1)

    # solve for flow state
    try:
        state = solve(**kwargs)
    except (ValueError, TypeError) as e:
        typer.echo(f"Error computing flow state: {e}", err=True)
        raise typer.Exit(1)

    # debug output: log resolved inputs and builder selected
    if state.provenance:
        for key, val in state.provenance.items():
            logger.debug("%s: %s", key, val)
    logger.debug("gas_model:       %s", state.gas_model)
    logger.debug("transport_model: %s", state.transport_model)

    # write JSON output if requested
    if output:
        write_json(state, output)
        typer.echo(f"Wrote {output}")

    # write legacy .dat output if requested
    if dat:
        dat_path = Path("flow_conditions.dat")
        write_flow_conditions_dat(state, dat_path)
        typer.echo(f"Wrote {dat_path}")

    # print summary unless quiet
    if not quiet:
        typer.echo("")
        typer.echo(str(state))


# --------------------------------------------------
# main entry point (for testing, allows running cli.py directly)
# --------------------------------------------------

if __name__ == "__main__":
    cli()
