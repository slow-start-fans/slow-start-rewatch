# -*- coding: utf-8 -*-

import sys

import click

from slow_start_rewatch.version import distribution_name, version


@click.command()
@click.version_option(version=version(), prog_name=distribution_name)
def main() -> None:
    """Main entry point for CLI."""
    sys.exit(0)


if __name__ == "__main__":
    main()
