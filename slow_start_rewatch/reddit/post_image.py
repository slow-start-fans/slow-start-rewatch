# -*- coding: utf-8 -*-

import io
import os
from typing import Optional
from urllib.parse import urlparse

from structlog import get_logger

log = get_logger()


class PostImage(object):
    """Represents an image in a Reddit post."""

    def __init__(
        self,
        source_url: str,
        link_content: str,
    ) -> None:
        """Initialize PostImage."""
        log.info(
            "post_image_create",
            source_url=source_url,
            link_content=link_content,
        )

        if not all([source_url, link_content]):
            raise AttributeError("All Post Image fields must be set.")

        filename = os.path.basename(urlparse(source_url).path)
        extension = os.path.splitext(filename.lower())[1][1:]

        self.source_url = source_url
        self.link_content = link_content
        self.filename = filename
        self.extension = extension
        self.reddit_asset_id: Optional[str] = None

        self._mime_type: Optional[str] = None
        self._image_content: Optional[io.BytesIO] = None

    @property
    def mime_type(self) -> str:
        """Get the MIME type."""
        if not self._mime_type:
            raise AttributeError("This property has not been set yet.")

        return self._mime_type

    @mime_type.setter
    def mime_type(self, mime_type: str) -> None:
        """Set the MIME type."""
        self._mime_type = mime_type

    @property
    def image_content(self) -> io.BytesIO:
        """Get the Image Content."""
        if not self._image_content:
            raise AttributeError("This property has not been set yet.")

        return self._image_content

    @image_content.setter
    def image_content(self, image_content: io.BytesIO) -> None:
        """Set the Image Content."""
        self._image_content = image_content

    def __eq__(self, other: object) -> bool:
        """
        Compare this instance to other object.

        Only :attr:`source_url` and :attr:`link_content` are taken into
        account.
        """
        if not isinstance(other, self.__class__):
            return NotImplemented

        return (
            self.source_url,
            self.link_content,
        ) == (
            other.source_url,
            other.link_content,
        )
