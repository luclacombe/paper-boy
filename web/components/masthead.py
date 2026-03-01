"""Newspaper masthead component for Paper Boy."""

from datetime import date
from typing import Optional

import streamlit as st


def render_masthead(
    show_date: bool = True,
    edition_number: Optional[int] = None,
    size: str = "large",
):
    """Render the newspaper-style masthead.

    Args:
        show_date: Whether to show today's date below the title.
        edition_number: Optional edition number to display.
        size: "large" for landing/dashboard, "small" for inner pages.
    """
    today = date.today()
    date_str = today.strftime("%A, %B %-d, %Y")

    if size == "large":
        title_size = "2.2rem"
        subtitle_size = "1.1rem"
    else:
        title_size = "1.6rem"
        subtitle_size = "0.95rem"

    edition_html = ""
    if edition_number is not None:
        edition_html = (
            f'<span style="float: right;">Edition #{edition_number}</span>'
        )

    date_html = ""
    if show_date:
        date_html = f"""
        <div class="masthead-date" style="font-size: {subtitle_size}; margin-top: 0.25rem;">
            <span>{date_str}</span>
            {edition_html}
        </div>
        """

    st.markdown(
        f"""
    <div style="margin-bottom: 1.5rem;">
        <hr class="thick-rule">
        <div style="padding: 0.75rem 0 0.5rem 0;">
            <h1 class="masthead-title" style="font-size: {title_size};">
                P A P E R &nbsp; B O Y
            </h1>
        </div>
        <hr class="thin-rule">
        {date_html}
        <hr class="thick-rule" style="margin-top: 0.5rem;">
    </div>
    """,
        unsafe_allow_html=True,
    )


def render_page_header(title: str):
    """Render a section/page header in newspaper style."""
    st.markdown(
        f"""
    <div style="margin-bottom: 1.5rem;">
        <hr class="thick-rule">
        <h2 class="masthead-title" style="font-size: 1.4rem; padding: 0.5rem 0;">
            {title}
        </h2>
        <hr class="thin-rule">
    </div>
    """,
        unsafe_allow_html=True,
    )
