# -*- coding: utf-8 -*-

import math
import time
from datetime import datetime
from typing import Iterator, Optional

import click
from structlog import get_logger

from slow_start_rewatch.config import Config
from slow_start_rewatch.exceptions import Abort

log = get_logger()


class Timer(object):
    """Handles waiting for the scheduled post."""

    def __init__(
        self,
        config: Config,
        start_time: Optional[datetime] = None,
        target_time: Optional[datetime] = None,
    ) -> None:
        """Initialize Timer."""
        self.refresh_interval: int = config["timer.refresh_interval"]
        self.start_time = start_time
        self.target_time = target_time

    def wait(self, target_time: datetime) -> None:
        """
        Wait until the target time.

        Show progress bar while waiting.

        The user can interrupt the waiting by pressing Ctrl+C.
        """
        self.start_time = datetime.utcnow()
        self.target_time = target_time

        if self.start_time > self.target_time:
            log.warning(
                "timer_invalid_time",
                start_time=self.start_time,
                target_time=target_time,
            )
            raise RuntimeError(
                "The target time cannot be in the past.",
            )

        try:
            self.countdown()
        except KeyboardInterrupt as exception:
            log.warning("timer_countdown_abort")
            raise Abort from exception

    def countdown(self) -> None:
        """Render the countdown progressbar."""
        log.debug("timer_countdown_start")
        with click.progressbar(
            self.ticks(),
            label="Waiting to submit the post (press Ctrl+C to quit):",
            fill_char=click.style("#", fg="bright_magenta"),
            item_show_func=self.time_left,
            show_eta=False,
            show_percent=False,
        ) as progressbar:
            for tick in progressbar:
                current_timestamp = datetime.utcnow().timestamp() * 1000

                if current_timestamp < tick:
                    time.sleep((tick - current_timestamp) / 1000)

        log.debug("timer_countdown_end")
        self.target_time = None

    def ticks(self) -> Iterator[int]:
        """
        Generate ticks for the countdown.

        The ticks are generated from the target time backwards.
        """
        if self.start_time is None or self.target_time is None:
            raise AttributeError(
                "'start_time' and 'target_time' must be set " +
                "before starting countdown.",
            )

        start_timestamp = round(self.start_time.timestamp() * 1000)
        target_timestamp = round(self.target_time.timestamp() * 1000)

        return reversed(range(
            target_timestamp,
            start_timestamp,
            -self.refresh_interval,
        ))

    def time_left(self, tick: Optional[int]) -> str:
        """Render remaining time."""
        if self.target_time is None:
            raise AttributeError(
                "'target_time' must be set to render remaning time.",
            )

        if tick is None:
            return ""

        current_timestamp = datetime.fromtimestamp(math.floor(tick / 1000))

        return str(self.target_time - current_timestamp)
