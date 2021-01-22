# -*- coding: utf-8 -*-

import logging
import sys
import traceback
from logging.config import dictConfig
from typing import Optional

import click
import structlog

from slow_start_rewatch.app import App
from slow_start_rewatch.exceptions import SlowStartRewatchException
from slow_start_rewatch.version import distribution_name, version

# Set up logging:
timestamper = structlog.processors.TimeStamper(
    fmt="%Y-%m-%d %H:%M:%S",  # noqa: WPS323
)
pre_chain = [
    # Add the log level and a timestamp to the event_dict if the log entry
    # is not from structlog.
    structlog.stdlib.add_log_level,
    timestamper,
]
dictConfig({
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "colored": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.dev.ConsoleRenderer(colors=True),
            "foreign_pre_chain": pre_chain,
        },
    },
    "handlers": {
        "default": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "colored",
        },
    },
    "loggers": {
        "": {
            "handlers": ["default"],
            "level": "CRITICAL",
            "propagate": True,
        },
    },
})
structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        timestamper,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)
log = structlog.get_logger()


@click.command()
@click.option("--debug", is_flag=True)
@click.option("-w", "--schedule_wiki_url")
@click.option("-f", "--schedule_file")
@click.version_option(version=version(), prog_name=distribution_name)
def main(
    debug: bool,
    schedule_wiki_url: Optional[str],
    schedule_file: Optional[str],
) -> None:
    """Main entry point for CLI."""
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        App(
            schedule_wiki_url=schedule_wiki_url,
            schedule_file=schedule_file,
        ).run()
    except SlowStartRewatchException as exception:
        click.echo(click.style(str(exception), fg="red"), err=True)

        if exception.hint:
            click.echo(exception.hint)

        sys.exit(exception.exit_code)
    except Exception:
        log.exception("unhandled_exception")
        click.echo(
            click.style("An unexpected error has occurred:\n", fg="red") +
            traceback.format_exc(),
            err=True,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
