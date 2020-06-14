# -*- coding: utf-8 -*-

import io

import pytest

from slow_start_rewatch.reddit.post_image import PostImage
from tests.conftest import TEST_IMAGE_URL

TEST_IMAGE_CONTENT = "Slow Start is awesome!"


def test_create():
    """Test creating a `PostImage` instance."""
    post_image = PostImage(
        source_url=TEST_IMAGE_URL,
        link_content=TEST_IMAGE_CONTENT,
    )

    assert post_image.source_url == TEST_IMAGE_URL
    assert post_image.link_content == TEST_IMAGE_CONTENT
    assert post_image.filename == "happy_shion.gif"
    assert post_image.extension == "gif"
    assert post_image.reddit_asset_id is None


def test_create_with_empty_field():
    """Test creating a `PostImage` instance with an empty attribute."""
    with pytest.raises(AttributeError):
        PostImage(
            source_url=TEST_IMAGE_URL,
            link_content=None,  # type: ignore
        )


def test_properties():
    """Test getters and setters of `PostImage`."""
    post_image = PostImage(
        source_url=TEST_IMAGE_URL,
        link_content=TEST_IMAGE_CONTENT,
    )

    with pytest.raises(AttributeError):
        assert post_image.mime_type

    post_image.mime_type = "image/gif"

    assert post_image.mime_type == "image/gif"

    with pytest.raises(AttributeError):
        assert post_image.image_content

    post_image.image_content = io.BytesIO(b"GIF89a")

    assert post_image.image_content.getvalue() == b"GIF89a"


def test_comparison():
    """Test the comparison of `PostImage` objects."""
    post_image = PostImage(
        source_url=TEST_IMAGE_URL,
        link_content=TEST_IMAGE_CONTENT,
    )

    identical_post_image = PostImage(
        source_url=TEST_IMAGE_URL,
        link_content=TEST_IMAGE_CONTENT,
    )

    different_post_image = PostImage(
        source_url=TEST_IMAGE_URL,
        link_content="Slow Start really is awesome!",
    )

    assert post_image == identical_post_image
    assert post_image != different_post_image
    assert post_image.__eq__("post_image") is NotImplemented  # noqa: WPS609
