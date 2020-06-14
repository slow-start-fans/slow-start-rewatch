# -*- coding: utf-8 -*-

import io
import json
from pathlib import Path
from unittest.mock import call, patch

import pytest
from requests.exceptions import HTTPError

from slow_start_rewatch.exceptions import ImageNotFound, PostConversionError
from slow_start_rewatch.reddit.post_image import PostImage
from slow_start_rewatch.reddit.text_post_converter import TextPostConverter
from tests.conftest import TEST_IMAGE_URL, TEST_ROOT_DIR, MockConfig

TEST_TEXT_POST_CONVERTER_PATH = Path(TEST_ROOT_DIR).joinpath(
    "test_text_post_converter",
)


@patch.object(TextPostConverter, "replace_image")
@patch.object(TextPostConverter, "download_image")
@patch.object(TextPostConverter, "parse_markdown")
@patch("slow_start_rewatch.reddit.text_post_converter.RedditHelper")
def test_convert_to_rtjson(
    mock_reddit_helper,
    mock_parse_markdown,
    mock_download_image,
    mock_replace_image,
    text_post_converter_config,
    reddit,
    downloaded_image: PostImage,
):
    """
    Test the procedure of converting Markdown to Reddit Rich Text JSON.

    Ensure that all the methods involved in the process are called correctly.
    """
    mock_parse_markdown.return_value = ("Fluffy Markdown", downloaded_image)
    helper = mock_reddit_helper.return_value
    helper.convert_to_rtjson.return_value = [{"c": [{"t": "Fluffy Markdown"}]}]

    converter = TextPostConverter(text_post_converter_config, reddit)
    converter.convert_to_rtjson("**Fluffy Markdown**")

    assert mock_parse_markdown.call_args == call("**Fluffy Markdown**")
    assert helper.convert_to_rtjson.call_args == call("Fluffy Markdown")
    assert mock_download_image.call_args == call(downloaded_image)
    assert helper.upload_image.call_args == call(
        filename=downloaded_image.filename,
        mime_type=downloaded_image.mime_type,
        image_content=downloaded_image.image_content,
    )
    assert mock_replace_image.call_args == call(
        [{"c": [{"t": "Fluffy Markdown"}]}],
        downloaded_image,
    )


def test_parse_markdown(
    text_post_converter_config,
    reddit,
    text_post_markdown,
    text_post_normalized_markdown,
):
    """Test that the post body Markdown is parsed correctly."""
    converter = TextPostConverter(text_post_converter_config, reddit)

    normalized_markdown, parsed_post_image = converter.parse_markdown(
        text_post_markdown,
    )

    expected_post_image = PostImage(
        source_url=TEST_IMAGE_URL,
        link_content="wonderful animation",
    )

    assert normalized_markdown == text_post_normalized_markdown
    assert parsed_post_image == expected_post_image

    with pytest.raises(ImageNotFound):
        converter.parse_markdown("The cute image **is missing!**")


@patch("requests.get")
def test_download_image(
    mock_get,
    text_post_converter_config,
    reddit,
    post_image: PostImage,
):
    """
    Test downloading an image content.

    1. Test handling an exception and ensure that the `post_image` is empty.

    2. Test successful download.
    """
    mock_get.return_value.content = b"GIF89a"  # noqa: WPS110
    mock_get.return_value.raise_for_status.side_effect = [HTTPError, None]

    converter = TextPostConverter(text_post_converter_config, reddit)

    with pytest.raises(PostConversionError):
        converter.download_image(post_image)

    with pytest.raises(AttributeError):
        assert not post_image.image_content

    with pytest.raises(AttributeError):
        assert not post_image.mime_type

    converter.download_image(post_image)

    assert post_image.image_content.getvalue() == b"GIF89a"
    assert post_image.mime_type == "image/gif"


def test_replace_image(
    text_post_converter_config,
    reddit,
    text_post_rtjson,
    text_post_adapted_rtjson,
    post_image: PostImage,
):
    """Test replacing the image in the Reddit Rich Text JSON."""
    converter = TextPostConverter(text_post_converter_config, reddit)

    post_image.reddit_asset_id = "adorable_id"

    rtjson = converter.replace_image(text_post_rtjson, post_image)

    assert rtjson == text_post_adapted_rtjson

    with pytest.raises(PostConversionError):
        assert not converter.replace_image(
            text_post_adapted_rtjson,
            post_image,
        )


@pytest.fixture()
def text_post_converter_config():
    """Return mock Config for testing the `TextPostConverter`."""
    return MockConfig({
        "reddit": {"user_agent": "Slow Start Rewatch Client"},
        "post_image_mime_types": {"gif": "image/gif"},
    })


@pytest.fixture()
def downloaded_image(post_image):
    """Return mock `PostImage` class with downloaded image content."""
    post_image.mime_type = "image/gif"
    post_image.image_content = io.BytesIO(b"GIF89a")

    return post_image


@pytest.fixture()
def post_image():
    """Return mock `PostImage` class."""
    return PostImage(
        source_url=TEST_IMAGE_URL,
        link_content="Slow Start is awesome!",
    )


@pytest.fixture()
def text_post_markdown():
    """
    Return a sample Markdown post body.

    The first image placed inline to check that the normalization works
    correctly.
    """
    markdown_file_path = TEST_TEXT_POST_CONVERTER_PATH.joinpath(
        "text_post_markdown.md",
    )
    with open(markdown_file_path, "r") as markdown_file:
        markdown = markdown_file.read()

    return markdown


@pytest.fixture()
def text_post_normalized_markdown():
    """
    Return a sample "normalized" Markdown post body.

    The first image is surrounded by empty rows.
    """
    normalized_markdown_file_path = TEST_TEXT_POST_CONVERTER_PATH.joinpath(
        "text_post_normalized_markdown.md",
    )
    with open(normalized_markdown_file_path, "r") as normalized_markdown_file:
        normalized_markdown = normalized_markdown_file.read()

    return normalized_markdown


@pytest.fixture()
def text_post_rtjson():
    """Return a sample Reddit Rich Text JSON post body."""
    rtjson_file_path = TEST_TEXT_POST_CONVERTER_PATH.joinpath(
        "text_post_rtjson.json",
    )
    with open(rtjson_file_path, "r") as rtjson_file:
        rtjson = json.load(rtjson_file)

    return rtjson


@pytest.fixture()
def text_post_adapted_rtjson():
    """
    Return an adapted Reddit Rich Text JSON post body.

    The original link to the first image is replaced by the image uploaded to
    the Reddit Hosting.
    """
    adapted_rtjson_file_path = TEST_TEXT_POST_CONVERTER_PATH.joinpath(
        "text_post_adapted_rtjson.json",
    )
    with open(adapted_rtjson_file_path, "r") as adapted_rtjson_file:
        adapted_rtjson = json.load(adapted_rtjson_file)

    return adapted_rtjson
