# streamlit_app.py

import streamlit as st

# Initial session state for UI toggle
if "features_mode" not in st.session_state:
    st.session_state.features_mode = "default"  # 'default', 'search', 'selected'

# Functions to toggle modes
def set_mode(mode):
    st.session_state.features_mode = mode

# Sidebar
st.sidebar.title("Steer Models")
model = st.sidebar.selectbox(
    "Select Model to Steer",
    ["GEMMA-2-98-IT", "Other Models"]
)

st.sidebar.button("Back", on_click=lambda: set_mode("default"))  # Back Button
st.sidebar.button("Demo", key="demo_button")  # Placeholder for the demo buttons

# Main interface
st.title("Steer Models")

if st.session_state.features_mode == "default":
    # Default UI
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("NORMAL")
        st.markdown("""
        ### Hey, I'm normal gemma-2-9b-it!
        I'm the default, non-steered model.
        """)

    with col2:
        st.subheader("STEERED")
        st.markdown("""
        ### Hey, I'm steered gemma-2-9b-it!
        Choose a demo, select a preset, or manually search and add features.
        """)

    # Button to Add Features
    if st.button("Search for Features"):
        set_mode("search")
elif st.session_state.features_mode == "search":
    # Features Mode UI - Search for Features
    st.subheader("Search for Features")
    feature_query = st.text_input("Search query (e.g., 'cats', 'blue', 'royal')", key="feature_query")

    if feature_query:
        st.markdown("### Results")
        st.button("code snippets related to API data retrieval and error handling", key="feature_1", on_click=lambda: set_mode("selected"))
        st.button("paths or connections related to a specific API or software library", key="feature_2", on_click=lambda: set_mode("selected"))
        st.button("technical terms and references related to software", key="feature_3", on_click=lambda: set_mode("selected"))

    st.markdown("### Advanced Settings")
    col1, col2, col3 = st.columns(3)

    with col1:
        tokens = st.slider("Tokens", 0, 100, 32, key="tokens")
        temp = st.slider("Temperature", 0.0, 1.0, 0.5, key="temp")
    with col2:
        freq_penalty = st.slider("Frequency Penalty", 0, 10, 2, key="freq_penalty")
        manual_seed = st.slider("Manual Seed", 0, 50, 16, key="manual_seed")
    with col3:
        strength = st.slider("Strength Multiple", 1, 10, 4, key="strength")
        random_seed = st.checkbox("Random Seed", key="random_seed")

    st.button("Reset Settings", on_click=lambda: st.session_state.update({
        "tokens": 32,
        "temp": 0.5,
        "freq_penalty": 2,
        "manual_seed": 16,
        "strength": 4,
        "random_seed": False,
    }))
elif st.session_state.features_mode == "selected":
    # Features Mode UI - Selected Features
    st.subheader("Selected Features")
    st.markdown("""
    - **Feature**: Code snippets related to API data retrieval and error handling
    - **Feature**: Paths or connections related to a specific API or software library
    """)

    st.markdown("### Adjustments for Selected Features")
    col1, col2, col3 = st.columns(3)

    with col1:
        tokens = st.slider("Tokens", 0, 100, 32, key="tokens_selected")
        temp = st.slider("Temperature", 0.0, 1.0, 0.5, key="temp_selected")
    with col2:
        freq_penalty = st.slider("Frequency Penalty", 0, 10, 2, key="freq_penalty_selected")
        manual_seed = st.slider("Manual Seed", 0, 50, 16, key="manual_seed_selected")
    with col3:
        strength = st.slider("Strength Multiple", 1, 10, 4, key="strength_selected")
        random_seed = st.checkbox("Random Seed", key="random_seed_selected")

    st.button("Reset Settings", on_click=lambda: st.session_state.update({
        "tokens_selected": 32,
        "temp_selected": 0.5,
        "freq_penalty_selected": 2,
        "manual_seed_selected": 16,
        "strength_selected": 4,
        "random_seed_selected": False,
    }))
