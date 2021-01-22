# -*- coding: utf-8 -*-

import io
import json
from functools import partial
from typing import Dict, List, Optional, Tuple

import requests
from praw import Reddit, endpoints
from praw.exceptions import PRAWException
from praw.reddit import Submission
from requests.exceptions import HTTPError
from structlog import get_logger

from slow_start_rewatch.config import Config
from slow_start_rewatch.exceptions import RedditError

API_PATH_CONVERT = "api/convert_rte_body_format"

log = get_logger()

# Simplified Type Alias accommodated for the specific usage of this class.
RichTextJson = List[
    Dict[str, List[
        Dict[str, str]
    ]]
]


class RedditHelper(object):
    """Provides access to Reddit's API methods unsupported by `PRAW`."""

    def __init__(self, config: Config, reddit: Reddit) -> None:
        """Initialize RedditHelper."""
        self.reddit = reddit
        self._http_post = partial(requests.post, headers={
            "User-Agent": config["reddit.user_agent"],
        })

    def convert_to_rtjson(self, markdown_text: str) -> RichTextJson:
        """Convert Markdown to Reddit Rich Text."""
        log.info("post_convert", output_mode="rtjson")
        try:
            response = self.reddit.post(API_PATH_CONVERT, data={
                "output_mode": "rtjson",
                "markdown_text": markdown_text,
            })
        except (PRAWException, KeyError) as exception:
            log.exception("post_convert_error")
            raise RedditError(
                "Error when converting the post to Rich Text.",
            ) from exception

        if "output" not in response or "output_mode" not in response:
            log.error(
                "post_convert_output_missing",
                response=str(response),
            )
            raise RedditError(
                "Missing output data when converting the post to Rich Text.",
            )

        output = response["output"]

        if "document" not in output or response["output_mode"] != "rtjson":
            log.error(
                "post_convert_output_invalid",
                output=str(output),
            )
            raise RedditError(
                "Invalid output data when converting a post to Rich Text.",
            )

        return output["document"]

    def upload_image(
        self,
        filename: str,
        mime_type: str,
        image_content: io.BytesIO,
    ) -> str:
        """
        Upload image to the Reddit hosting.

        Inspired by :meth:`Subreddit._upload_media` from `PRAW`.
        """
        log.info("image_upload", filename=filename)
        try:
            upload_url, upload_data, asset_id = self._request_upload_lease(
                filename=filename,
                mime_type=mime_type,
            )
        except (PRAWException, KeyError) as upload_lease_error:
            log.exception("image_upload_lease_error")
            raise RedditError(
                "Error when preparing the image upload to the Reddit hosting.",
            ) from upload_lease_error

        upload_response = self._http_post(
            "https:{0}".format(upload_url),
            data=upload_data,
            files={
                "file": (filename, image_content),
            },
        )
        try:
            upload_response.raise_for_status()
        except HTTPError as http_error:
            log.exception("image_upload_error")
            raise RedditError(
                "Error when uploading the image to the Reddit hosting.",
            ) from http_error

        return asset_id

    def submit_post_rtjson(
        self,
        subreddit: str,
        title: str,
        body_rtjson: RichTextJson,
        flair_id: Optional[str],
    ) -> Submission:
        """
        Submit the Rich Text post to Reddit.

        Similar to :meth:`Subreddit.submit` from `PRAW`, but the body of the
        post is submitted as Rich Text JSON instead of Markdown (imitating the
        submission via New Reddit).
        """
        return self.reddit.post(
            endpoints.API_PATH["submit"],
            data={
                "sr": subreddit,
                "kind": "self",
                "richtext_json": json.dumps({"document": body_rtjson}),
                "sendreplies": True,
                "title": title,
                "flair_id": flair_id,
                "nsfw": False,
                "spoiler": False,
                "validate_on_submit": True,
            },
        )

    def _request_upload_lease(
        self,
        filename,
        mime_type,
    ) -> Tuple[str, Dict[str, str], str]:
        """
        Request the Image Upload Lease and parse the Upload Lease data.

        Inspired by :meth:`Subreddit._upload_media` from `PRAW`.
        """
        lease_data = self.reddit.post(
            endpoints.API_PATH["media_asset"],
            data={
                "filepath": filename,
                "mimetype": mime_type,
            },
        )

        upload_data = {
            str(field["name"]): str(field["value"])
            for field in lease_data["args"]["fields"]
        }
        upload_url = str(lease_data["args"]["action"])
        asset_id = str(lease_data["asset"]["asset_id"])

        return upload_url, upload_data, asset_id
