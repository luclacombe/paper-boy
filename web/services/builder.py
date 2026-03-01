"""Bridge between the Streamlit web UI and the paper_boy build pipeline."""

import logging
import os
import sys
import tempfile
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Ensure the src directory is on the path so we can import paper_boy
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from paper_boy.config import (
    Config,
    DeliveryConfig,
    EmailConfig,
    FeedConfig,
    GoogleDriveConfig,
    NewspaperConfig,
)
from paper_boy.delivery import deliver
from paper_boy.feeds import Section, fetch_feeds
from paper_boy.main import BuildResult, build_newspaper

logger = logging.getLogger(__name__)


def config_from_user_data(user_config: dict) -> Config:
    """Construct a paper_boy Config from web UI user data.

    Args:
        user_config: Dict from the database service with keys like
                     title, feeds, delivery_method, etc.

    Returns:
        A paper_boy Config object ready for build_newspaper().
    """
    feeds = [
        FeedConfig(name=f["name"], url=f["url"]) for f in user_config.get("feeds", [])
    ]

    newspaper = NewspaperConfig(
        title=user_config.get("title", "Morning Digest"),
        language=user_config.get("language", "en"),
        max_articles_per_feed=user_config.get("max_articles_per_feed", 10),
        include_images=user_config.get("include_images", True),
    )

    google_drive = GoogleDriveConfig(
        folder_name=user_config.get("google_drive_folder", "Rakuten Kobo"),
    )

    email_config = EmailConfig(
        smtp_host=user_config.get("email_smtp_host", "smtp.gmail.com"),
        smtp_port=user_config.get("email_smtp_port", 465),
        sender=user_config.get("email_sender", ""),
        password=user_config.get("email_password", ""),
        recipient=user_config.get("kindle_email", ""),
    )

    delivery = DeliveryConfig(
        method=user_config.get("delivery_method", "local"),
        device=user_config.get("device", "kobo"),
        google_drive=google_drive,
        email=email_config,
    )

    return Config(newspaper=newspaper, feeds=feeds, delivery=delivery)


def build_edition(
    user_config: dict,
    output_dir: Optional[str] = None,
    issue_date: Optional[date] = None,
) -> BuildResult:
    """Build a newspaper from the user's config.

    Args:
        user_config: Dict from the database service.
        output_dir: Directory to write the EPUB. Uses temp dir if None.
        issue_date: Date for the edition. Uses today if None.

    Returns:
        BuildResult with epub_path, sections, and total_articles.

    Raises:
        RuntimeError: If no articles were fetched.
        ValueError: If no feeds are configured.
    """
    if not user_config.get("feeds"):
        raise ValueError("No feeds configured. Add some sources first.")

    config = config_from_user_data(user_config)

    if output_dir is None:
        output_dir = tempfile.mkdtemp(prefix="paperboy_")

    if issue_date is None:
        issue_date = date.today()

    output_path = os.path.join(
        output_dir, f"paper-boy-{issue_date.isoformat()}.epub"
    )

    return build_newspaper(config, output_path=output_path, issue_date=issue_date)


def deliver_edition(epub_path, user_config: dict) -> Tuple[bool, str]:
    """Deliver a built EPUB using the configured delivery method.

    Args:
        epub_path: Path to the EPUB file.
        user_config: Dict from the database service.

    Returns:
        Tuple of (success: bool, message: str).
    """
    config = config_from_user_data(user_config)

    if config.delivery.method == "local":
        return True, "Download ready"

    try:
        deliver(Path(epub_path), config)
        method = config.delivery.method
        if method == "google_drive":
            return True, f"Uploaded to Google Drive ({config.delivery.google_drive.folder_name})"
        elif method == "email":
            return True, f"Emailed to {config.delivery.email.recipient}"
        return True, "Delivered"
    except Exception as e:
        logger.error("Delivery failed: %s", e)
        return False, str(e)


def preview_feeds(user_config: dict) -> List[Section]:
    """Fetch feeds without building EPUB — for dashboard headline preview.

    Args:
        user_config: Dict from the database service.

    Returns:
        List of Section objects with articles.
    """
    if not user_config.get("feeds"):
        return []

    config = config_from_user_data(user_config)
    return fetch_feeds(config)
