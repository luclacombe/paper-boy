"""Feed catalog service — loads and queries the curated RSS feed list."""

import os
from functools import lru_cache

import yaml


CATALOG_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "feed_catalog.yaml")


@lru_cache(maxsize=1)
def _load_catalog() -> dict:
    """Load the feed catalog from YAML."""
    with open(CATALOG_PATH) as f:
        return yaml.safe_load(f)


def get_bundles() -> list[dict]:
    """Get all starter bundles.

    Returns a list of dicts with keys: name, description, feeds (list of feed IDs).
    """
    return _load_catalog()["bundles"]


def get_categories() -> list[dict]:
    """Get all feed categories with their feeds.

    Returns a list of dicts with keys: name, feeds (list of feed dicts).
    Each feed dict has: id, name, url, description.
    """
    return _load_catalog()["categories"]


def get_all_feeds() -> dict[str, dict]:
    """Get a flat dict of all feeds, keyed by feed ID.

    Returns: {"guardian-world": {"id": "guardian-world", "name": "The Guardian", ...}, ...}
    """
    feeds = {}
    for category in get_categories():
        for feed in category["feeds"]:
            feeds[feed["id"]] = feed
    return feeds


def get_feeds_for_bundle(bundle_name: str) -> list[dict]:
    """Get the full feed details for a given bundle name.

    Returns a list of feed dicts (id, name, url, description).
    """
    all_feeds = get_all_feeds()
    for bundle in get_bundles():
        if bundle["name"] == bundle_name:
            return [all_feeds[fid] for fid in bundle["feeds"] if fid in all_feeds]
    return []


def validate_rss_url(url: str) -> bool:
    """Basic validation of an RSS feed URL."""
    if not url:
        return False
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        return False
    if "." not in url:
        return False
    return True
