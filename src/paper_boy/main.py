"""Main orchestration — fetch, build, deliver."""

from __future__ import annotations

import logging
from datetime import date
from pathlib import Path

from paper_boy.config import Config
from paper_boy.delivery import deliver
from paper_boy.epub import build_epub
from paper_boy.feeds import fetch_feeds

logger = logging.getLogger(__name__)


def build_newspaper(
    config: Config,
    output_path: str | Path | None = None,
    issue_date: date | None = None,
) -> Path:
    """Fetch feeds and build the newspaper EPUB.

    Returns the path to the generated EPUB file.
    """
    if issue_date is None:
        issue_date = date.today()

    logger.info("Building %s for %s", config.newspaper.title, issue_date)

    # Fetch all feeds
    logger.info("Fetching %d feed(s)...", len(config.feeds))
    sections = fetch_feeds(config)

    total_articles = sum(len(s.articles) for s in sections)
    if total_articles == 0:
        raise RuntimeError("No articles were extracted from any feed")

    logger.info(
        "Extracted %d articles across %d sections",
        total_articles,
        len(sections),
    )

    # Build EPUB
    epub_path = build_epub(sections, config, issue_date, output_path)
    logger.info("Built EPUB: %s", epub_path)

    return epub_path


def build_and_deliver(
    config: Config,
    output_path: str | Path | None = None,
    issue_date: date | None = None,
) -> Path:
    """Build the newspaper and deliver it."""
    epub_path = build_newspaper(config, output_path, issue_date)

    # Deliver
    deliver(epub_path, config)

    return epub_path
