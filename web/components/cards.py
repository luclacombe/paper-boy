"""Reusable card components for Paper Boy."""

from typing import List, Optional

import streamlit as st

from web.components.theme import (
    CAPTION_GRAY,
    DELIVERED_GREEN,
    BUILDING_AMBER,
    FAILED_CHARCOAL,
    EDITION_RED,
)


def status_banner(
    status: str,
    message: str,
    detail: str = "",
):
    """Render a status banner (delivered, building, failed, empty).

    Args:
        status: One of "delivered", "building", "failed", "empty".
        message: Primary status message.
        detail: Secondary detail line (e.g., "37 articles - 8 sources - 2.4 MB").
    """
    status_styles = {
        "delivered": {
            "border_color": DELIVERED_GREEN,
            "icon": "&#10003;",
            "icon_color": DELIVERED_GREEN,
        },
        "building": {
            "border_color": BUILDING_AMBER,
            "icon": "&#9676;",
            "icon_color": BUILDING_AMBER,
        },
        "failed": {
            "border_color": FAILED_CHARCOAL,
            "icon": "&#10007;",
            "icon_color": FAILED_CHARCOAL,
        },
        "empty": {
            "border_color": CAPTION_GRAY,
            "icon": "&#9671;",
            "icon_color": CAPTION_GRAY,
        },
    }
    style = status_styles.get(status, status_styles["empty"])

    detail_html = ""
    if detail:
        detail_html = f'<div class="mono-text" style="margin-top: 0.25rem;">{detail}</div>'

    st.markdown(
        f"""
    <div class="status-banner" style="border-left: 4px solid {style['border_color']};">
        <div style="font-size: 1.1rem; font-weight: 600; color: {style['icon_color']};">
            <span style="margin-right: 0.5rem;">{style['icon']}</span>
            {message}
        </div>
        {detail_html}
    </div>
    """,
        unsafe_allow_html=True,
    )


def headline_card(source_name: str, headlines: List[str], source_type: str = "RSS"):
    """Render a headline card for a single source.

    Args:
        source_name: Name of the source (e.g., "The Guardian").
        headlines: List of article titles (shows first 2-3).
        source_type: "RSS" or "Newsletter".
    """
    headlines_html = ""
    for title in headlines[:3]:
        headlines_html += f"""
        <div class="headline-text" style="font-size: 0.95rem; margin-bottom: 0.4rem;">
            {title}
        </div>
        """

    remaining = len(headlines) - 3
    if remaining > 0:
        headlines_html += f"""
        <div class="caption-text" style="margin-top: 0.3rem;">
            &middot;&middot;&middot; {remaining} more article{"s" if remaining != 1 else ""}
        </div>
        """

    type_badge = ""
    if source_type == "Newsletter":
        type_badge = '<span class="section-label" style="float: right; font-size: 0.7rem;">newsletter</span>'

    st.markdown(
        f"""
    <div class="pb-card">
        <div class="section-label" style="margin-bottom: 0.5rem;">
            {source_name}
            {type_badge}
        </div>
        <hr class="thin-rule" style="margin-bottom: 0.6rem;">
        {headlines_html}
    </div>
    """,
        unsafe_allow_html=True,
    )


def source_card(
    name: str,
    url: str,
    article_count: Optional[int] = None,
    last_fetched: str = "",
    status: str = "active",
):
    """Render a source card for the My Sources page.

    Args:
        name: Source name.
        url: Feed URL.
        article_count: Number of articles fetched.
        last_fetched: When the feed was last fetched.
        status: "active" or "warning".
    """
    badge_class = "badge-active" if status == "active" else "badge-failed"
    badge_text = "Active" if status == "active" else "Warning"
    badge_icon = "&#10003;" if status == "active" else "&#9888;"

    stats_html = ""
    if article_count is not None:
        stats_html = f'<span class="mono-text">{article_count} articles</span>'
    if last_fetched:
        stats_html += f' <span class="caption-text">&middot; Last fetched: {last_fetched}</span>'

    st.markdown(
        f"""
    <div class="pb-card">
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div>
                <div class="headline-text" style="font-size: 1rem;">{name}</div>
                <div class="caption-text" style="font-size: 0.8rem; margin-top: 0.15rem;">{url}</div>
            </div>
            <span class="badge {badge_class}">{badge_icon} {badge_text}</span>
        </div>
        <div style="margin-top: 0.5rem;">
            {stats_html}
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )


def edition_card(
    date_str: str,
    edition_number: int,
    article_count: int,
    source_count: int,
    file_size: str,
    status: str,
    error_message: str = "",
):
    """Render an edition card for the Past Editions page.

    Args:
        date_str: Formatted date string.
        edition_number: Edition number.
        article_count: Number of articles.
        source_count: Number of sources.
        file_size: File size string (e.g., "2.4 MB").
        status: "delivered", "failed", or "building".
        error_message: Error message if failed.
    """
    badge_class = {
        "delivered": "badge-delivered",
        "failed": "badge-failed",
        "building": "badge-building",
    }.get(status, "badge-failed")

    badge_text = {
        "delivered": "&#10003; Delivered",
        "failed": "&#10007; Failed",
        "building": "&#9676; Building",
    }.get(status, status)

    error_html = ""
    if error_message:
        error_html = f'<div class="caption-text" style="margin-top: 0.3rem;">{error_message}</div>'

    st.markdown(
        f"""
    <div class="pb-card">
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div>
                <div class="headline-text" style="font-size: 1rem;">{date_str}</div>
                <div class="mono-text" style="margin-top: 0.2rem;">
                    {article_count} articles &middot; {source_count} sources &middot; {file_size}
                </div>
                {error_html}
            </div>
            <div style="text-align: right;">
                <span class="badge {badge_class}">{badge_text}</span>
                <div class="caption-text" style="margin-top: 0.2rem;">Edition #{edition_number}</div>
            </div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )


def onboarding_choice_card(
    title: str,
    subtitle: str,
    description: str,
    button_text: str,
    time_estimate: str,
    enabled: bool = True,
):
    """Render a choice card for the onboarding step 1.

    Returns True if the button was clicked.
    """
    opacity = "1" if enabled else "0.6"
    coming_soon = "" if enabled else '<span class="badge badge-building" style="margin-left: 0.5rem;">Coming soon</span>'

    st.markdown(
        f"""
    <div class="pb-card" style="opacity: {opacity}; padding: 1.5rem;">
        <div class="section-label" style="font-size: 0.85rem; margin-bottom: 0.5rem;">
            {title}{coming_soon}
        </div>
        <hr class="thin-rule" style="margin-bottom: 0.75rem;">
        <div class="headline-text" style="font-size: 1rem; margin-bottom: 0.5rem;">
            {subtitle}
        </div>
        <div class="body-text" style="font-size: 0.9rem; margin-bottom: 0.75rem;">
            {description}
        </div>
        <div class="caption-text" style="margin-bottom: 0.75rem;">{time_estimate}</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    if enabled:
        return st.button(button_text, use_container_width=True, type="primary")
    else:
        st.button(button_text, use_container_width=True, disabled=True)
        return False
