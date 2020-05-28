# -*- coding: utf-8 -*-

import sys

import click


@click.command()
def main() -> None:
    """Main entry point for CLI."""
    sys.exit(0)


if __name__ == "__main__":
    main()
