"""Delivery settings page."""

import streamlit as st

from web.components.theme import inject_theme
from web.components.masthead import render_page_header
from web.components.navigation import render_navigation
from web.services.database import get_user_config, save_user_config


inject_theme()
render_page_header("Delivery")
render_navigation("delivery")

config = get_user_config()

# === DESTINATION ===
st.markdown(
    """
<div class="section-label" style="margin-bottom: 0.75rem;">
    DESTINATION
</div>
<hr class="dotted-rule" style="margin-bottom: 1rem;">
""",
    unsafe_allow_html=True,
)

current_method = config.get("delivery_method", "local")
delivery_index = 1 if current_method == "google_drive" else 0

delivery_method = st.radio(
    "Delivery method",
    options=["local", "google_drive"],
    format_func=lambda x: {
        "local": "Download Only",
        "google_drive": "Kobo (via Google Drive)",
    }[x],
    index=delivery_index,
    label_visibility="collapsed",
)

if delivery_method == "local":
    st.markdown(
        """
    <div class="pb-card" style="padding: 1rem;">
        <div class="body-text" style="font-size: 0.9rem;">
            Download each edition manually from the Past Editions page.
            No setup required.
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        """
    <div class="pb-card" style="padding: 1rem;">
        <div class="body-text" style="font-size: 0.9rem; margin-bottom: 0.5rem;">
            Your newspaper appears in your Kobo library automatically via Google Drive sync.
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    folder_name = st.text_input(
        "Google Drive folder name",
        value=config.get("google_drive_folder", "Rakuten Kobo"),
    )

    st.markdown(
        """
    <div class="caption-text" style="margin-top: 0.25rem;">
        This is the folder in your Google Drive that syncs with your Kobo.
        The default is "Rakuten Kobo".
    </div>
    """,
        unsafe_allow_html=True,
    )

# Kindle coming soon
st.markdown(
    """
<div class="pb-card" style="padding: 1rem; opacity: 0.5; margin-top: 0.75rem;">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div class="body-text" style="font-size: 0.9rem;">
            Kindle (via email)
        </div>
        <span class="badge badge-building">Coming soon</span>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown(
    "<hr class='thin-rule' style='margin: 1.5rem 0;'>",
    unsafe_allow_html=True,
)

# === SCHEDULE ===
st.markdown(
    """
<div class="section-label" style="margin-bottom: 0.75rem;">
    SCHEDULE
</div>
<hr class="dotted-rule" style="margin-bottom: 1rem;">
""",
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="body-text" style="font-size: 0.9rem; margin-bottom: 0.5rem;">'
    "Build and deliver every day at:"
    "</div>",
    unsafe_allow_html=True,
)

time_options = ["05:00", "05:30", "06:00", "06:30", "07:00", "07:30", "08:00"]
current_time = config.get("delivery_time", "06:00")
time_index = time_options.index(current_time) if current_time in time_options else 2

time_col, tz_col = st.columns(2)
with time_col:
    delivery_time = st.selectbox(
        "Delivery time",
        options=time_options,
        index=time_index,
        format_func=lambda x: f"{x} AM",
        label_visibility="collapsed",
    )
with tz_col:
    timezone = st.selectbox(
        "Timezone",
        options=["UTC", "US/Eastern", "US/Central", "US/Pacific", "Europe/London", "Europe/Paris"],
        index=0,
        label_visibility="collapsed",
    )

st.markdown(
    "<hr class='thin-rule' style='margin: 1.5rem 0;'>",
    unsafe_allow_html=True,
)

# === NEWSPAPER SETTINGS ===
st.markdown(
    """
<div class="section-label" style="margin-bottom: 0.75rem;">
    NEWSPAPER SETTINGS
</div>
<hr class="dotted-rule" style="margin-bottom: 1rem;">
""",
    unsafe_allow_html=True,
)

title = st.text_input(
    "Newspaper title",
    value=config.get("title", "Morning Digest"),
)

max_options = [3, 5, 8, 10, 15, 20]
current_max = config.get("max_articles_per_feed", 10)
max_index = max_options.index(current_max) if current_max in max_options else 3

max_articles = st.selectbox(
    "Max articles per source",
    options=max_options,
    index=max_index,
)

include_images = st.checkbox(
    "Include images",
    value=config.get("include_images", True),
)

st.markdown(
    "<hr class='thin-rule' style='margin: 1.5rem 0;'>",
    unsafe_allow_html=True,
)

# === SAVE BUTTON ===
if st.button("Save Changes", type="primary", use_container_width=True):
    updated_config = config.copy()
    updated_config["delivery_method"] = delivery_method
    if delivery_method == "google_drive":
        updated_config["google_drive_folder"] = folder_name
    updated_config["delivery_time"] = delivery_time
    updated_config["title"] = title
    updated_config["max_articles_per_feed"] = max_articles
    updated_config["include_images"] = include_images

    save_user_config(updated_config)

    st.markdown(
        """
    <div style="text-align: center; padding: 0.5rem; margin-top: 0.5rem;">
        <span class="badge badge-delivered">&#10003; Settings saved</span>
    </div>
    """,
        unsafe_allow_html=True,
    )
