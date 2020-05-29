# -*- coding: utf-8 -*-

import logging
from logging.config import dictConfig

import click
import structlog

from slow_start_rewatch.app import App
from slow_start_rewatch.config import Config
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


@click.command()
@click.option("--debug", is_flag=True)
@click.version_option(version=version(), prog_name=distribution_name)
def main(debug) -> None:
    """Main entry point for CLI."""
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)

    config = Config()

    app = App(config)

    app.run()


if __name__ == "__main__":
    main()
