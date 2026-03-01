"""Past Editions page — archive of built newspapers."""

import os
from datetime import date

import streamlit as st

from web.components.theme import inject_theme
from web.components.masthead import render_page_header
from web.components.navigation import render_navigation
from web.components.cards import edition_card
from web.components.loading import show_empty_state
from web.services.database import get_delivery_history
from web.services import github_actions


inject_theme()
render_page_header("Past Editions")
render_navigation("history")

history = get_delivery_history()

# GitHub Actions builds
github_editions = []
if github_actions.is_configured():
    github_editions = github_actions.get_recent_builds(limit=10)

if not history and not github_editions:
    show_empty_state("no_history")
    st.stop()

# Display local editions
if history:
    for i, record in enumerate(history):
        edition_card(
            date_str=record.get("date", "Unknown date"),
            edition_number=record.get("edition_number", i + 1),
            article_count=record.get("article_count", 0),
            source_count=record.get("source_count", 0),
            file_size=record.get("file_size", "0 KB"),
            status=record.get("status", "unknown"),
            error_message=record.get("error", ""),
        )

        # Action button for each edition
        epub_path = record.get("epub_path", "")
        col1, col2 = st.columns([3, 1])

        with col2:
            if record.get("status") == "delivered" and epub_path and os.path.exists(epub_path):
                with open(epub_path, "rb") as f:
                    epub_bytes = f.read()
                edition_date = record.get("edition_date", date.today().isoformat())
                st.download_button(
                    "Download",
                    data=epub_bytes,
                    file_name=f"paper-boy-{edition_date}.epub",
                    mime="application/epub+zip",
                    key=f"download_{i}",
                    use_container_width=True,
                )
            elif record.get("status") == "failed":
                if st.button("Retry", key=f"retry_{i}", use_container_width=True):
                    st.switch_page("pages/dashboard.py")

# Display GitHub Actions builds
if github_editions:
    st.markdown(
        """
    <div style="margin: 1.5rem 0 1rem 0; text-align: center;">
        <hr class="thin-rule">
        <div class="section-label" style="padding: 0.5rem 0; font-size: 0.8rem;">
            GITHUB ACTIONS BUILDS
        </div>
        <hr class="thin-rule">
    </div>
    """,
        unsafe_allow_html=True,
    )

    for i, edition in enumerate(github_editions):
        status = edition.get("status", "unknown")
        badge_map = {
            "delivered": "delivered",
            "failed": "failed",
            "building": "building",
            "queued": "building",
        }

        edition_card(
            date_str=edition.get("date", "Unknown date"),
            edition_number=0,
            article_count=0,
            source_count=0,
            file_size="",
            status=badge_map.get(status, "unknown"),
        )

st.markdown(
    """
<div class="caption-text" style="text-align: center; margin-top: 1.5rem;">
    Showing the last 30 days of editions.
</div>
""",
    unsafe_allow_html=True,
)
