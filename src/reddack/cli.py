# Future imports
from __future__ import (
    annotations
)

# Standard imports
import argparse
from typing import (
    Sequence
)
from pathlib import Path

# Local imports
import reddack.config

def create_arg_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the CLI"""

    parser = argparse.ArgumentParser(
        description=(
            "Moderate Reddit communities via Slack"
        ),
        argument_default=argparse.SUPPRESS
    )

    parser.add_argument(
        "--config",
        dest="config_path",
        required=True,
        help="The path to the config file."
    )

    return parser

def process_args(parsedargs):
    configpath = Path(parsedargs.configpath)
    if configpath.suffix == ".json":
        reddack.config.reddack(configpath)

def cli(sys_argv: Sequence[str] | None = None) -> None:
    """Parse the CLI arguments"""
    parser = create_arg_parser()
    parsed_args = parser.parse_args(sys_argv)
    process_args(parsed_args)

def main(sys_argv: Sequence[str] | None = None) -> None:
    """Run through the CLI."""
    cli(sys_argv)
