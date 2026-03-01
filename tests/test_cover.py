"""Tests for cover image generation."""

from datetime import date
from io import BytesIO

from PIL import Image

from paper_boy.cover import generate_cover
from paper_boy.feeds import Article, Section


def _make_sections():
    return [
        Section(
            name="World News",
            articles=[
                Article(title="Climate Summit Reaches Historic Agreement", url="https://example.com/1"),
                Article(title="Markets Rally on Economic Data", url="https://example.com/2"),
            ],
        ),
        Section(
            name="Technology",
            articles=[
                Article(title="New AI Breakthrough in Language Models", url="https://example.com/3"),
            ],
        ),
        Section(
            name="Science",
            articles=[
                Article(title="Mars Rover Discovers Ancient Water Signs", url="https://example.com/4"),
            ],
        ),
    ]


def test_generate_cover_returns_jpeg():
    sections = _make_sections()
    cover_bytes = generate_cover("Morning Digest", sections, date(2026, 2, 28))

    assert len(cover_bytes) > 0
    img = Image.open(BytesIO(cover_bytes))
    assert img.format == "JPEG"


def test_generate_cover_dimensions():
    sections = _make_sections()
    cover_bytes = generate_cover("Test Paper", sections, date(2026, 1, 1))

    img = Image.open(BytesIO(cover_bytes))
    assert img.size == (600, 900)


def test_generate_cover_empty_sections():
    cover_bytes = generate_cover("Test Paper", [], date(2026, 1, 1))
    assert len(cover_bytes) > 0

    img = Image.open(BytesIO(cover_bytes))
    assert img.size == (600, 900)


def test_generate_cover_default_date():
    sections = _make_sections()
    cover_bytes = generate_cover("Test", sections)
    assert len(cover_bytes) > 0
