# -*- coding: utf-8 -*-

import io
import re
from typing import Tuple

import requests
from praw import Reddit
from requests.exceptions import HTTPError
from structlog import get_logger

from slow_start_rewatch.config import Config
from slow_start_rewatch.exceptions import ImageNotFound, PostConversionError
from slow_start_rewatch.reddit.post_image import PostImage
from slow_start_rewatch.reddit.reddit_helper import RedditHelper, RichTextJson

log = get_logger()


class TextPostConverter(object):
    """Provides methods for parsing and converting Reddit Text Posts."""

    def __init__(self, config: Config, reddit: Reddit) -> None:
        """Initialize TextPostConverter."""
        self.reddit_helper = RedditHelper(config, reddit)
        self.mime_types = config["post_image_mime_types"]

    def convert_to_rtjson(self, markdown) -> RichTextJson:
        """
        Convert the post body from Markdown to Reddit Rich Text JSON.

        The first image in the post is replaced by the image hosted on Reddit
        so that Reddit creates a thumbnail for the post.

        1. Parse the Markdown post body and extract the first image and
           normalize the Markdown content by ensuring the image is surrounded
           by empty rows.

        2. Convert the Markdown content to Reddit Rich Text JSON.

        3. Download the source image.

        4. Store the image to the Reddit hosting.

        5. Replace the source image with the image hosted by Reddit.
        """
        normalized_markdown, post_image = self.parse_markdown(markdown)

        rtjson = self.reddit_helper.convert_to_rtjson(normalized_markdown)

        self.download_image(post_image)

        post_image.reddit_asset_id = self.reddit_helper.upload_image(
            filename=post_image.filename,
            mime_type=post_image.mime_type,
            image_content=post_image.image_content,
        )

        return self.replace_image(rtjson, post_image)

    def parse_markdown(self, markdown_text: str) -> Tuple[str, PostImage]:
        """
        Parse the Markdown post body and extract the first image.

        Normalize the Markdown content by recreating the image link surrounded
        by empty rows.
        """
        pattern = re.compile(
            r"\s*\[\s*(?P<content>[^\]]+?)\s*\]" +
            r"\([^\)]*?(?P<url>http[^\)]+\.(" +
            "|".join(self.mime_types.keys()) +
            r"))[^\)]*?\)\s*",
        )

        match = pattern.search(markdown_text)

        if not match:
            raise ImageNotFound("Image not found in the Markdown content.")

        post_image = PostImage(
            source_url=match.group("url"),
            link_content=match.group("content"),
        )

        normalized_markdown = pattern.sub(
            repl=r"\n\n[\g<content>](\g<url>)\n\n",
            string=markdown_text,
            count=1,
        )

        return normalized_markdown, post_image

    def download_image(self, post_image: PostImage) -> None:
        """Download the source image."""
        log.info("post_image_download", url=post_image.source_url)
        response = requests.get(post_image.source_url)
        try:
            response.raise_for_status()
        except HTTPError as exception:
            log.exception("post_image_download_error")
            raise PostConversionError(
                "Failed to download the image in the post.",
            ) from exception

        post_image.image_content = io.BytesIO(response.content)
        post_image.mime_type = self.mime_types[post_image.extension]
        log.debug(
            "post_image_download_result",
            file_size=len(response.content),
        )

    def replace_image(
        self,
        rtjson: RichTextJson,
        post_image: PostImage,
    ) -> RichTextJson:
        """Replace the source image with the image hosted by Reddit."""
        reddit_image = {
            "c": post_image.link_content,
            "e": "img",
            "id": post_image.reddit_asset_id,
        }

        for index, element in enumerate(rtjson):
            try:
                if element["c"][0]["u"] == post_image.source_url:
                    rtjson[index] = reddit_image  # type: ignore
                    break
            except (KeyError, TypeError):
                continue
        else:
            raise PostConversionError(
                "The source image wasn't found in the Rich Text JSON.",
            )

        return rtjson
