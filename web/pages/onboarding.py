"""Onboarding flow — 3-step setup wizard."""

import streamlit as st

from web.components.theme import inject_theme
from web.components.masthead import render_masthead
from web.services.feed_catalog import get_bundles, get_categories, get_feeds_for_bundle, validate_rss_url
from web.services.database import save_user_config, get_user_config, complete_onboarding


inject_theme()

# Initialize onboarding state
if "onboarding_step" not in st.session_state:
    st.session_state["onboarding_step"] = 1
if "onboarding_feeds" not in st.session_state:
    st.session_state["onboarding_feeds"] = []

current_step = st.session_state["onboarding_step"]


def _render_step_indicator(current: int, total: int = 3):
    """Render the step progress dots."""
    dots = ""
    for i in range(1, total + 1):
        if i < current:
            css_class = "step-dot step-dot-completed"
        elif i == current:
            css_class = "step-dot step-dot-active"
        else:
            css_class = "step-dot"
        dots += f'<span class="{css_class}"></span>'

    st.markdown(
        f"""
    <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1.5rem;">
        <span class="caption-text">Step {current} of {total}</span>
        <div class="step-indicator">{dots}</div>
    </div>
    """,
        unsafe_allow_html=True,
    )


# ============================================================
# STEP 1: Choose Your Path
# ============================================================
if current_step == 1:
    _render_step_indicator(1)

    st.markdown(
        """
    <div style="margin-bottom: 1.5rem;">
        <hr class="thick-rule">
        <h2 class="masthead-title" style="font-size: 1.4rem; padding: 0.5rem 0;">
            How do you get your news?
        </h2>
        <hr class="thin-rule">
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Free Sources card
    st.markdown(
        """
    <div class="pb-card" style="padding: 1.5rem;">
        <div class="section-label" style="font-size: 0.85rem; margin-bottom: 0.5rem;">
            FREE SOURCES
        </div>
        <hr class="thin-rule" style="margin-bottom: 0.75rem;">
        <div class="headline-text" style="font-size: 1rem; margin-bottom: 0.5rem;">
            The world's best free journalism, curated into your morning paper.
        </div>
        <div class="body-text" style="font-size: 0.9rem; margin-bottom: 0.5rem;">
            Sources like The Guardian, NPR, Ars Technica, Reuters, and 25+ others.
            Full articles, not just headlines.
        </div>
        <div class="caption-text">Ready in 2 minutes.</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    if st.button("Start with Free Sources", type="primary", use_container_width=True):
        st.session_state["onboarding_step"] = 2
        st.session_state["onboarding_path"] = "free"
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # Paid Subscriptions card (coming soon)
    st.markdown(
        """
    <div class="pb-card" style="padding: 1.5rem; opacity: 0.6;">
        <div class="section-label" style="font-size: 0.85rem; margin-bottom: 0.5rem;">
            PAID SUBSCRIPTIONS
            <span class="badge badge-building" style="margin-left: 0.5rem;">Coming soon</span>
        </div>
        <hr class="thin-rule" style="margin-bottom: 0.75rem;">
        <div class="headline-text" style="font-size: 1rem; margin-bottom: 0.5rem;">
            Forward newsletters from your existing FT, NYT, Bloomberg, or WSJ subscription.
        </div>
        <div class="body-text" style="font-size: 0.9rem; margin-bottom: 0.5rem;">
            We compile the newsletter content &mdash; editorial commentary, analysis, and curated
            summaries &mdash; into your morning paper. These are digests, not full articles.
        </div>
        <div class="caption-text">Takes about 5 minutes to set up.</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.button(
        "Set Up Newsletter Forwarding",
        use_container_width=True,
        disabled=True,
    )

    st.markdown(
        '<div class="caption-text" style="text-align: center; margin-top: 1rem;">'
        "You can always add both later."
        "</div>",
        unsafe_allow_html=True,
    )


# ============================================================
# STEP 2: Pick Your Sources
# ============================================================
elif current_step == 2:
    _render_step_indicator(2)

    st.markdown(
        """
    <div style="margin-bottom: 1rem;">
        <hr class="thick-rule">
        <h2 class="masthead-title" style="font-size: 1.4rem; padding: 0.5rem 0;">
            Pick your sources
        </h2>
        <hr class="thin-rule">
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="caption-text" style="margin-bottom: 1.5rem;">'
        "Select at least 3. You can change these anytime."
        "</div>",
        unsafe_allow_html=True,
    )

    # === STARTER BUNDLES ===
    st.markdown(
        """
    <div class="section-label" style="margin-bottom: 0.75rem;">
        STARTER BUNDLES
    </div>
    <hr class="dotted-rule" style="margin-bottom: 1rem;">
    """,
        unsafe_allow_html=True,
    )

    bundles = get_bundles()
    bundle_cols = st.columns(len(bundles))

    for i, bundle in enumerate(bundles):
        with bundle_cols[i]:
            feeds_in_bundle = get_feeds_for_bundle(bundle["name"])
            feed_names = ", ".join(f["name"] for f in feeds_in_bundle[:4])
            if len(feeds_in_bundle) > 4:
                feed_names += f" +{len(feeds_in_bundle) - 4} more"

            st.markdown(
                f"""
            <div class="pb-card" style="text-align: center; padding: 1.25rem;">
                <div class="headline-text" style="font-size: 0.95rem; margin-bottom: 0.5rem;">
                    {bundle['name']}
                </div>
                <div class="caption-text" style="font-size: 0.8rem; margin-bottom: 0.5rem;">
                    {feed_names}
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )

            if st.button(
                "Select",
                key=f"bundle_{i}",
                use_container_width=True,
            ):
                # Set the selected feeds from the bundle
                st.session_state["onboarding_feeds"] = [
                    {"name": f["name"], "url": f["url"], "category": "Bundle"}
                    for f in feeds_in_bundle
                ]
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # === BUILD YOUR OWN ===
    st.markdown(
        """
    <div class="section-label" style="margin-bottom: 0.75rem;">
        OR BUILD YOUR OWN
    </div>
    <hr class="dotted-rule" style="margin-bottom: 1rem;">
    """,
        unsafe_allow_html=True,
    )

    # Track selected feed URLs
    selected_urls = {f["url"] for f in st.session_state["onboarding_feeds"]}

    categories = get_categories()

    # Display categories in 2-column layout
    cat_col1, cat_col2 = st.columns(2)

    for i, category in enumerate(categories):
        with cat_col1 if i % 2 == 0 else cat_col2:
            st.markdown(
                f"""
            <div class="section-label" style="margin-bottom: 0.5rem; margin-top: 0.5rem;">
                {category['name']}
            </div>
            """,
                unsafe_allow_html=True,
            )

            for feed in category["feeds"]:
                is_selected = feed["url"] in selected_urls
                if st.checkbox(
                    feed["name"],
                    value=is_selected,
                    key=f"feed_{feed['id']}",
                    help=feed["description"],
                ):
                    if not is_selected:
                        st.session_state["onboarding_feeds"].append(
                            {
                                "name": feed["name"],
                                "url": feed["url"],
                                "category": category["name"],
                            }
                        )
                        selected_urls.add(feed["url"])
                else:
                    if is_selected:
                        st.session_state["onboarding_feeds"] = [
                            f
                            for f in st.session_state["onboarding_feeds"]
                            if f["url"] != feed["url"]
                        ]
                        selected_urls.discard(feed["url"])

    st.markdown("<br>", unsafe_allow_html=True)

    # === CUSTOM RSS URL ===
    st.markdown(
        """
    <div class="section-label" style="margin-bottom: 0.5rem;">
        ADD A CUSTOM RSS FEED
    </div>
    """,
        unsafe_allow_html=True,
    )

    custom_col1, custom_col2 = st.columns([3, 1])
    with custom_col1:
        custom_url = st.text_input(
            "RSS URL",
            placeholder="https://example.com/rss",
            label_visibility="collapsed",
        )
    with custom_col2:
        if st.button("Add", use_container_width=True):
            if custom_url and validate_rss_url(custom_url):
                # Extract domain for a name
                from urllib.parse import urlparse

                domain = urlparse(custom_url).netloc
                name = domain.replace("www.", "").split(".")[0].title()
                st.session_state["onboarding_feeds"].append(
                    {"name": name, "url": custom_url, "category": "Custom"}
                )
                st.rerun()
            elif custom_url:
                st.error("Please enter a valid URL starting with http:// or https://")

    st.markdown("<hr class='thin-rule'>", unsafe_allow_html=True)

    # === BOTTOM BAR ===
    feed_count = len(st.session_state["onboarding_feeds"])

    bottom_col1, bottom_col2 = st.columns([1, 1])
    with bottom_col1:
        st.markdown(
            f'<div class="mono-text" style="padding-top: 0.5rem;">'
            f"{feed_count} source{'s' if feed_count != 1 else ''} selected"
            f"</div>",
            unsafe_allow_html=True,
        )
    with bottom_col2:
        can_continue = feed_count >= 3
        if st.button(
            "Continue",
            type="primary",
            use_container_width=True,
            disabled=not can_continue,
        ):
            st.session_state["onboarding_step"] = 3
            st.rerun()

    if not can_continue and feed_count > 0:
        st.markdown(
            f'<div class="caption-text" style="text-align: right;">'
            f"Select {3 - feed_count} more to continue"
            f"</div>",
            unsafe_allow_html=True,
        )

    # Back button
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Back"):
        st.session_state["onboarding_step"] = 1
        st.rerun()


# ============================================================
# STEP 3: Delivery Setup
# ============================================================
elif current_step == 3:
    _render_step_indicator(3)

    st.markdown(
        """
    <div style="margin-bottom: 1.5rem;">
        <hr class="thick-rule">
        <h2 class="masthead-title" style="font-size: 1.4rem; padding: 0.5rem 0;">
            Where should we deliver your paper?
        </h2>
        <hr class="thin-rule">
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Delivery method
    delivery_method = st.radio(
        "Delivery method",
        options=["download", "google_drive"],
        format_func=lambda x: {
            "download": "Download Only",
            "google_drive": "Kobo (via Google Drive)",
        }[x],
        index=0,
        label_visibility="collapsed",
    )

    if delivery_method == "download":
        st.markdown(
            """
        <div class="pb-card" style="padding: 1.25rem;">
            <div class="body-text" style="font-size: 0.9rem;">
                Download each edition manually from the Past Editions page.
                No setup required &mdash; great for trying things out.
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
        <div class="pb-card" style="padding: 1.25rem;">
            <div class="body-text" style="font-size: 0.9rem; margin-bottom: 0.75rem;">
                Your newspaper appears in your Kobo library automatically
                via Google Drive sync.
            </div>
            <div class="caption-text">
                Requires a Google Drive connection and Kobo set up with Google Drive sync.
                Configure this in Delivery settings after setup.
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown("<hr class='dotted-rule' style='margin: 1rem 0;'>", unsafe_allow_html=True)

    # Delivery schedule
    st.markdown(
        """
    <div class="section-label" style="margin-bottom: 0.75rem;">
        DELIVERY SCHEDULE
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="body-text" style="font-size: 0.9rem; margin-bottom: 0.5rem;">'
        "Your paper will be ready every morning at:"
        "</div>",
        unsafe_allow_html=True,
    )

    time_col, tz_col = st.columns(2)
    with time_col:
        delivery_time = st.selectbox(
            "Time",
            options=["05:00", "05:30", "06:00", "06:30", "07:00", "07:30", "08:00"],
            index=2,  # Default 06:00
            format_func=lambda x: f"{x} AM" if x else x,
            label_visibility="collapsed",
        )
    with tz_col:
        timezone = st.selectbox(
            "Timezone",
            options=["UTC", "US/Eastern", "US/Central", "US/Pacific", "Europe/London", "Europe/Paris"],
            index=0,
            label_visibility="collapsed",
        )

    st.markdown("<hr class='dotted-rule' style='margin: 1rem 0;'>", unsafe_allow_html=True)

    # Newspaper settings
    st.markdown(
        """
    <div class="section-label" style="margin-bottom: 0.75rem;">
        NEWSPAPER SETTINGS
    </div>
    """,
        unsafe_allow_html=True,
    )

    title = st.text_input("Newspaper title", value="Morning Digest")
    max_articles = st.selectbox(
        "Max articles per source",
        options=[3, 5, 8, 10, 15],
        index=3,  # Default 10
    )
    include_images = st.checkbox("Include images", value=True)

    st.markdown("<hr class='thin-rule' style='margin: 1.5rem 0;'>", unsafe_allow_html=True)

    # === BUILD BUTTON ===
    if st.button(
        "Build My First Edition",
        type="primary",
        use_container_width=True,
    ):
        # Save the config
        config = {
            "title": title,
            "feeds": st.session_state["onboarding_feeds"],
            "delivery_method": "local" if delivery_method == "download" else "google_drive",
            "google_drive_folder": "Rakuten Kobo",
            "max_articles_per_feed": max_articles,
            "include_images": include_images,
            "delivery_time": delivery_time,
            "language": "en",
        }
        save_user_config(config)
        complete_onboarding()

        # Clear onboarding state
        for key in ["onboarding_step", "onboarding_feeds", "onboarding_path", "started_onboarding"]:
            st.session_state.pop(key, None)

        st.rerun()

    # Back button
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Back"):
        st.session_state["onboarding_step"] = 2
        st.rerun()
