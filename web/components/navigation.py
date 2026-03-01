"""Horizontal navigation bar component for Paper Boy."""

import streamlit as st


# Navigation items with their page file paths
NAV_ITEMS = [
    {"label": "Today's Edition", "page": "pages/dashboard.py", "key": "dashboard"},
    {"label": "My Sources", "page": "pages/sources.py", "key": "sources"},
    {"label": "Delivery", "page": "pages/delivery.py", "key": "delivery"},
    {"label": "Past Editions", "page": "pages/history.py", "key": "history"},
]


def render_navigation(current_page: str):
    """Render newspaper-style horizontal tab navigation.

    Uses Streamlit columns with styled buttons that trigger page switches.
    The active page button is styled differently via CSS.

    Args:
        current_page: The key of the currently active page
                     (e.g., "dashboard", "sources").
    """
    # Custom CSS for navigation styling
    st.markdown(
        """
    <style>
    /* Navigation container spacing */
    .nav-container {
        border-bottom: 1px solid #C4BFB8;
        padding-bottom: 0;
        margin-bottom: 1.5rem;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="nav-container">', unsafe_allow_html=True)

    cols = st.columns(len(NAV_ITEMS))
    for i, item in enumerate(NAV_ITEMS):
        is_active = item["key"] == current_page
        with cols[i]:
            if is_active:
                # Active tab — styled label (not clickable)
                st.markdown(
                    f"""
                <div style="
                    text-align: center;
                    padding: 0.5rem 0;
                    font-family: 'Source Sans 3', sans-serif;
                    font-size: 0.8rem;
                    font-weight: 700;
                    letter-spacing: 0.04em;
                    text-transform: uppercase;
                    color: #1B1B1B;
                    border-bottom: 3px solid #C23B22;
                ">{item['label']}</div>
                """,
                    unsafe_allow_html=True,
                )
            else:
                # Inactive tab — clickable button
                if st.button(
                    item["label"],
                    key=f"nav_{item['key']}",
                    use_container_width=True,
                ):
                    st.switch_page(item["page"])

    st.markdown("</div>", unsafe_allow_html=True)
