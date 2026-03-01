"""Cover image generation for the newspaper EPUB."""

from __future__ import annotations

import textwrap
from datetime import date
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from paper_boy.feeds import Section

# Cover dimensions optimized for e-readers
COVER_WIDTH = 600
COVER_HEIGHT = 900

# Colors
BG_COLOR = "#FAFAF8"
TEXT_COLOR = "#1A1A1A"
ACCENT_COLOR = "#333333"
RULE_COLOR = "#888888"
DATE_COLOR = "#555555"
SECTION_COLOR = "#666666"

# Font sizes (will use default font if custom not available)
TITLE_SIZE = 42
DATE_SIZE = 18
HEADLINE_SIZE = 16
SECTION_LABEL_SIZE = 12


def _load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Load a font, falling back to default if custom fonts aren't available."""
    # Try common system fonts
    font_paths = [
        # macOS
        "/System/Library/Fonts/NewYork.ttf",
        "/System/Library/Fonts/Supplemental/Georgia.ttf",
        "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
        # Linux
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
        # Bundled
        str(Path(__file__).parent.parent.parent / "fonts" / "font.ttf"),
    ]
    for path in font_paths:
        try:
            return ImageFont.truetype(path, size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()


def _load_bold_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Load a bold font variant."""
    font_paths = [
        "/System/Library/Fonts/NewYorkLarge-Bold.otf",
        "/System/Library/Fonts/Supplemental/Georgia Bold.ttf",
        "/System/Library/Fonts/Supplemental/Times New Roman Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
    ]
    for path in font_paths:
        try:
            return ImageFont.truetype(path, size)
        except (OSError, IOError):
            continue
    return _load_font(size)


def generate_cover(
    title: str,
    sections: list[Section],
    issue_date: date | None = None,
) -> bytes:
    """Generate a newspaper-style cover image.

    Returns JPEG bytes.
    """
    if issue_date is None:
        issue_date = date.today()

    img = Image.new("RGB", (COVER_WIDTH, COVER_HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    title_font = _load_bold_font(TITLE_SIZE)
    date_font = _load_font(DATE_SIZE)
    headline_font = _load_bold_font(HEADLINE_SIZE)
    section_font = _load_font(SECTION_LABEL_SIZE)

    y = 40

    # Top rule
    draw.line([(30, y), (COVER_WIDTH - 30, y)], fill=RULE_COLOR, width=2)
    y += 15

    # Newspaper title
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = (COVER_WIDTH - title_width) // 2
    draw.text((title_x, y), title, fill=TEXT_COLOR, font=title_font)
    y += (title_bbox[3] - title_bbox[1]) + 10

    # Date line
    date_str = issue_date.strftime("%A, %B %d, %Y")
    date_bbox = draw.textbbox((0, 0), date_str, font=date_font)
    date_width = date_bbox[2] - date_bbox[0]
    date_x = (COVER_WIDTH - date_width) // 2
    draw.text((date_x, y), date_str, fill=DATE_COLOR, font=date_font)
    y += (date_bbox[3] - date_bbox[1]) + 15

    # Rule below date
    draw.line([(30, y), (COVER_WIDTH - 30, y)], fill=RULE_COLOR, width=2)
    y += 25

    # Headlines from each section
    max_headlines = 6
    headline_count = 0

    for section in sections:
        if headline_count >= max_headlines:
            break
        if not section.articles:
            continue

        # Section label
        section_label = section.name.upper()
        draw.text((40, y), section_label, fill=SECTION_COLOR, font=section_font)
        y += 18

        # Top headline from this section
        article = section.articles[0]
        headline = article.title
        wrapped = textwrap.fill(headline, width=45)
        lines = wrapped.split("\n")[:2]  # Max 2 lines per headline
        for line in lines:
            draw.text((40, y), line, fill=TEXT_COLOR, font=headline_font)
            y += 22

        y += 12

        # Thin separator
        if headline_count < max_headlines - 1:
            draw.line([(40, y), (COVER_WIDTH - 40, y)], fill="#CCCCCC", width=1)
            y += 12

        headline_count += 1

        if y > COVER_HEIGHT - 80:
            break

    # Bottom rule
    draw.line(
        [(30, COVER_HEIGHT - 40), (COVER_WIDTH - 30, COVER_HEIGHT - 40)],
        fill=RULE_COLOR,
        width=2,
    )

    # Output as JPEG
    output = BytesIO()
    img.save(output, format="JPEG", quality=90)
    return output.getvalue()
