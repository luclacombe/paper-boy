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

# === DEVICE ===
st.markdown(
    """
<div class="section-label" style="margin-bottom: 0.75rem;">
    E-READER
</div>
<hr class="dotted-rule" style="margin-bottom: 1rem;">
""",
    unsafe_allow_html=True,
)

device_options = ["kobo", "kindle", "remarkable", "other"]
current_device = config.get("device", "kobo")
device_index = device_options.index(current_device) if current_device in device_options else 0

device = st.radio(
    "E-reader device",
    options=device_options,
    format_func=lambda x: {
        "kobo": "Kobo",
        "kindle": "Kindle",
        "remarkable": "reMarkable",
        "other": "Other",
    }[x],
    index=device_index,
    label_visibility="collapsed",
    horizontal=True,
)

st.markdown(
    "<hr class='thin-rule' style='margin: 1.5rem 0;'>",
    unsafe_allow_html=True,
)

# === DESTINATION (device-specific) ===
st.markdown(
    """
<div class="section-label" style="margin-bottom: 0.75rem;">
    DESTINATION
</div>
<hr class="dotted-rule" style="margin-bottom: 1rem;">
""",
    unsafe_allow_html=True,
)

# Initialize variables for save
folder_name = config.get("google_drive_folder", "Rakuten Kobo")
kindle_email = config.get("kindle_email", "")
email_smtp_host = config.get("email_smtp_host", "smtp.gmail.com")
email_smtp_port = config.get("email_smtp_port", 465)
email_sender = config.get("email_sender", "")
email_password = config.get("email_password", "")

current_method = config.get("delivery_method", "local")

if device == "kobo":
    method_options = ["google_drive", "local"]
    method_labels = {
        "local": "Download Only",
        "google_drive": "Kobo (via Google Drive)",
    }
    method_index = method_options.index(current_method) if current_method in method_options else 0

    delivery_method = st.radio(
        "Delivery method",
        options=method_options,
        format_func=lambda x: method_labels[x],
        index=method_index,
        label_visibility="collapsed",
    )

    if delivery_method == "google_drive":
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
    else:
        st.markdown(
            """
        <div class="pb-card" style="padding: 1rem;">
            <div class="body-text" style="font-size: 0.9rem;">
                Download each edition manually from the Past Editions page.
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

elif device == "kindle":
    method_options = ["email", "local"]
    method_labels = {
        "email": "Send to Kindle (via email)",
        "local": "Download Only",
    }
    method_index = method_options.index(current_method) if current_method in method_options else 0

    delivery_method = st.radio(
        "Delivery method",
        options=method_options,
        format_func=lambda x: method_labels[x],
        index=method_index,
        label_visibility="collapsed",
    )

    if delivery_method == "email":
        st.markdown(
            """
        <div class="pb-card" style="padding: 1rem;">
            <div class="body-text" style="font-size: 0.9rem; margin-bottom: 0.5rem;">
                Each edition is emailed directly to your Kindle.
                Amazon accepts EPUB files natively.
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

        kindle_email = st.text_input(
            "Kindle email address",
            value=config.get("kindle_email", ""),
            placeholder="your-name@kindle.com",
            help="Find this in Amazon → Manage Your Content and Devices → Preferences → Personal Document Settings.",
        )

        st.markdown(
            """
        <div class="section-label" style="margin-top: 1rem; margin-bottom: 0.5rem; font-size: 0.75rem;">
            SENDING EMAIL (SMTP)
        </div>
        """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
        <div class="caption-text" style="margin-bottom: 0.5rem;">
            The email account that sends to your Kindle.
            For Gmail, use an App Password (not your regular password).
        </div>
        """,
            unsafe_allow_html=True,
        )

        email_sender = st.text_input(
            "Sender email",
            value=config.get("email_sender", ""),
            placeholder="your-email@gmail.com",
        )

        email_password = st.text_input(
            "App password",
            value=config.get("email_password", ""),
            type="password",
            help="For Gmail: Google Account → Security → 2-Step Verification → App Passwords.",
        )

        smtp_col1, smtp_col2 = st.columns(2)
        with smtp_col1:
            email_smtp_host = st.text_input(
                "SMTP host",
                value=config.get("email_smtp_host", "smtp.gmail.com"),
            )
        with smtp_col2:
            email_smtp_port = st.number_input(
                "SMTP port",
                value=config.get("email_smtp_port", 465),
                min_value=1,
                max_value=65535,
            )

        st.markdown(
            """
        <div class="caption-text" style="margin-top: 0.5rem;">
            Make sure to add your sender email to Amazon's Approved Personal Document
            E-mail List in your Kindle settings.
        </div>
        """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
        <div class="pb-card" style="padding: 1rem;">
            <div class="body-text" style="font-size: 0.9rem;">
                Download and sideload via USB or email manually.
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

elif device == "remarkable":
    delivery_method = "local"
    st.markdown(
        """
    <div class="pb-card" style="padding: 1rem;">
        <div class="body-text" style="font-size: 0.9rem;">
            Download each edition and transfer to your reMarkable via USB
            or the reMarkable desktop app.
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

else:  # other
    delivery_method = "local"
    st.markdown(
        """
    <div class="pb-card" style="padding: 1rem;">
        <div class="body-text" style="font-size: 0.9rem;">
            Download each edition as an EPUB file.
            Works with any e-reader or reading app that supports EPUB.
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
    updated_config["device"] = device
    updated_config["delivery_method"] = delivery_method
    updated_config["google_drive_folder"] = folder_name
    updated_config["kindle_email"] = kindle_email
    updated_config["email_smtp_host"] = email_smtp_host
    updated_config["email_smtp_port"] = email_smtp_port
    updated_config["email_sender"] = email_sender
    updated_config["email_password"] = email_password
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
