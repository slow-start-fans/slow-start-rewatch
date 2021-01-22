# -*- coding: utf-8 -*-

import os

from structlog import get_logger

from slow_start_rewatch.config import Config
from slow_start_rewatch.exceptions import MissingPost, MissingSchedule
from slow_start_rewatch.schedule.schedule_storage import ScheduleStorage

log = get_logger()


class ScheduleFileStorage(ScheduleStorage):
    """Stores data about scheduled posts in local files."""

    def __init__(self, config: Config) -> None:
        """Initialize ScheduleFileStorage."""
        super().__init__()

        schedule_file: str = config["schedule_file"]

        if not schedule_file:
            raise RuntimeError(
                "The config must contain 'schedule_file' item.",
            )

        self.schedule_file = schedule_file
        self.schedule_directory = os.path.dirname(schedule_file)

    def load_schedule_data(self) -> str:
        """Load Schedule data from the file."""
        log.info("schedule_file_read", path=self.schedule_file)
        try:
            with open(self.schedule_file, encoding="utf-8") as schedule_file:
                schedule_data = schedule_file.read()
        except FileNotFoundError as error:
            log.exception("schedule_file_missing")
            raise MissingSchedule(
                "The schedule file not found: {0}".format(self.schedule_file),
            ) from error

        return schedule_data

    def load_post_body(self, body_template_source: str) -> str:
        """Load a post body from the file."""
        path = os.path.join(
            self.schedule_directory,
            body_template_source,
        )
        log.info("post_file_read", path=path)

        try:
            with open(path) as post_body_file:
                post_body = post_body_file.read()
        except FileNotFoundError as error:
            log.exception("post_file_missing")
            raise MissingPost(
                "The post file not found: {0}".format(path),
            ) from error

        return post_body

    def save_schedule_data(self, schedule_data: str) -> None:
        """Save the Schedule data to the file."""
        log.info("schedule_file_update", path=self.schedule_file)

        with open(self.schedule_file, "w") as schedule_file:
            schedule_file.write(schedule_data)
