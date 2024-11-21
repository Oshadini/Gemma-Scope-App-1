# streamlit_app.py

import streamlit as st

# Initial session state for UI toggle
if "features_mode" not in st.session_state:
    st.session_state.features_mode = False

# Function to toggle features view
def toggle_features():
    st.session_state.features_mode = True

# Sidebar
st.sidebar.title("Steer Models")
model = st.sidebar.selectbox(
    "Select Model to Steer",
    ["GEMMA-2-98-IT", "Other Models"]
)
preset = st.sidebar.radio(
    "Select a Preset",
    ["San Francisco Mode", "Positivity Mode", "Negativity Mode", "Music Mode", "British English Mode"]
)
st.sidebar.button("Demo", key="demo_button")  # Placeholder for the demo buttons

# Main interface
st.title("Steer Models")

# Normal and Steered Model Display
if not st.session_state.features_mode:
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
    if st.button("Add features"):
        toggle_features()
else:
    # Features Mode UI
    st.subheader("Search for Features")
    feature_query = st.text_input("Search query (e.g., 'cats', 'blue', 'royal')")

    st.markdown("### Advanced Settings")
    col1, col2, col3 = st.columns(3)

    with col1:
        tokens = st.slider("Tokens", 0, 100, 32)
        temp = st.slider("Temperature", 0.0, 1.0, 0.5)
    with col2:
        freq_penalty = st.slider("Frequency Penalty", 0, 10, 2)
        manual_seed = st.slider("Manual Seed", 0, 50, 16)
    with col3:
        strength = st.slider("Strength Multiple", 1, 10, 4)
        random_seed = st.checkbox("Random Seed")

    st.button("Reset Settings")
