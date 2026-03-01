"""Today's Edition — the main dashboard page."""

import os
import time
from datetime import date, datetime

import streamlit as st

from web.components.theme import inject_theme
from web.components.masthead import render_masthead
from web.components.navigation import render_navigation
from web.components.cards import status_banner, headline_card
from web.components.loading import show_empty_state, BUILD_MESSAGES
from web.services.database import get_user_config, get_delivery_history, add_delivery_record
from web.services.builder import build_edition, preview_feeds


inject_theme()

# Masthead
render_masthead(show_date=True, edition_number=st.session_state.get("edition_number"))

# Navigation
render_navigation("dashboard")

# Get user config
config = get_user_config()
feeds = config.get("feeds", [])

if not feeds:
    show_empty_state("no_sources")
    if st.button("Add Sources", type="primary"):
        st.switch_page("pages/sources.py")
    st.stop()


# === STATUS BANNER ===
last_build = st.session_state.get("last_build")

if last_build:
    if last_build["status"] == "delivered":
        status_banner(
            "delivered",
            f"Today's edition delivered at {last_build.get('time', '')}",
            f"{last_build.get('article_count', 0)} articles · "
            f"{last_build.get('source_count', 0)} sources · "
            f"{last_build.get('file_size', '')}",
        )
    elif last_build["status"] == "failed":
        status_banner(
            "failed",
            "Something went wrong while building your edition.",
            last_build.get("error", "We'll try again automatically."),
        )
    elif last_build["status"] == "building":
        status_banner(
            "building",
            "Building your edition...",
            "This usually takes 1-3 minutes.",
        )
else:
    status_banner(
        "empty",
        "No edition built yet",
        "Click 'Build New Edition' to create your first newspaper.",
    )

st.markdown("<br>", unsafe_allow_html=True)

# === ACTION BUTTONS ===
btn_col1, btn_col2 = st.columns(2)

with btn_col1:
    # Download button (only if we have a built EPUB)
    epub_path = st.session_state.get("last_epub_path")
    if epub_path and os.path.exists(epub_path):
        with open(epub_path, "rb") as f:
            epub_bytes = f.read()
        today = date.today().isoformat()
        st.download_button(
            "Download EPUB",
            data=epub_bytes,
            file_name=f"paper-boy-{today}.epub",
            mime="application/epub+zip",
            use_container_width=True,
        )
    else:
        st.button("Download EPUB", disabled=True, use_container_width=True)

with btn_col2:
    build_clicked = st.button(
        "Build New Edition",
        type="primary",
        use_container_width=True,
    )

# === BUILD PROCESS ===
if build_clicked:
    progress_bar = st.progress(0)
    status_text = st.empty()

    try:
        # Step 1: Setting the type
        status_text.markdown(
            f'<div class="caption-text" style="text-align: center; font-style: italic;">'
            f"{BUILD_MESSAGES[0]}</div>",
            unsafe_allow_html=True,
        )
        progress_bar.progress(0.1)

        # Step 2: Pulling from the wire
        status_text.markdown(
            f'<div class="caption-text" style="text-align: center; font-style: italic;">'
            f"{BUILD_MESSAGES[1]}</div>",
            unsafe_allow_html=True,
        )
        progress_bar.progress(0.3)

        # Step 3: Running the press (actual build)
        status_text.markdown(
            f'<div class="caption-text" style="text-align: center; font-style: italic;">'
            f"{BUILD_MESSAGES[2]}</div>",
            unsafe_allow_html=True,
        )
        progress_bar.progress(0.5)

        epub_path = build_edition(config)

        # Step 4: Folding and bundling
        status_text.markdown(
            f'<div class="caption-text" style="text-align: center; font-style: italic;">'
            f"{BUILD_MESSAGES[3]}</div>",
            unsafe_allow_html=True,
        )
        progress_bar.progress(0.8)

        # Get file size
        file_size_bytes = os.path.getsize(epub_path)
        if file_size_bytes > 1024 * 1024:
            file_size = f"{file_size_bytes / (1024 * 1024):.1f} MB"
        else:
            file_size = f"{file_size_bytes / 1024:.0f} KB"

        # Step 5: Done!
        status_text.markdown(
            f'<div class="caption-text" style="text-align: center; font-style: italic;">'
            f"{BUILD_MESSAGES[4]}</div>",
            unsafe_allow_html=True,
        )
        progress_bar.progress(1.0)

        now = datetime.now()
        build_record = {
            "status": "delivered",
            "time": now.strftime("%-I:%M %p"),
            "date": now.strftime("%A, %B %-d, %Y"),
            "article_count": len(feeds) * config.get("max_articles_per_feed", 10),
            "source_count": len(feeds),
            "file_size": file_size,
            "file_size_bytes": file_size_bytes,
            "epub_path": str(epub_path),
            "edition_date": date.today().isoformat(),
        }

        st.session_state["last_build"] = build_record
        st.session_state["last_epub_path"] = str(epub_path)

        # Track edition number
        edition_num = st.session_state.get("edition_number", 0) + 1
        st.session_state["edition_number"] = edition_num
        build_record["edition_number"] = edition_num

        add_delivery_record(build_record)

        time.sleep(1)
        st.rerun()

    except Exception as e:
        progress_bar.empty()
        status_text.empty()

        error_msg = str(e)
        # Translate technical errors to human-friendly messages
        if "No articles" in error_msg:
            friendly_msg = "None of your sources had new articles. This can happen on slow news days."
        elif "ConnectionError" in error_msg or "timeout" in error_msg.lower():
            friendly_msg = "We couldn't reach some of your sources. Please try again in a few minutes."
        else:
            friendly_msg = "Something went wrong while building your edition. Please try again."

        st.session_state["last_build"] = {
            "status": "failed",
            "error": friendly_msg,
            "time": datetime.now().strftime("%-I:%M %p"),
        }
        st.rerun()


# === HEADLINES SECTION ===
st.markdown(
    """
<div style="margin: 1.5rem 0 1rem 0; text-align: center;">
    <hr class="thin-rule">
    <div class="section-label" style="padding: 0.5rem 0; font-size: 0.8rem;">
        TODAY'S SOURCES
    </div>
    <hr class="thin-rule">
</div>
""",
    unsafe_allow_html=True,
)

# Display feeds in 2-column layout
col1, col2 = st.columns(2)

for i, feed in enumerate(feeds):
    with col1 if i % 2 == 0 else col2:
        headline_card(
            source_name=feed["name"],
            headlines=[],  # Headlines populated after build
            source_type=feed.get("type", "RSS"),
        )


# === SOURCE STATUS TABLE ===
st.markdown(
    """
<div style="margin: 1.5rem 0 1rem 0; text-align: center;">
    <hr class="thin-rule">
    <div class="section-label" style="padding: 0.5rem 0; font-size: 0.8rem;">
        SOURCE STATUS
    </div>
    <hr class="thin-rule">
</div>
""",
    unsafe_allow_html=True,
)

for feed in feeds:
    st.markdown(
        f"""
    <div class="source-row">
        <span>{feed['name']}</span>
        <span class="caption-text">RSS</span>
    </div>
    """,
        unsafe_allow_html=True,
    )
