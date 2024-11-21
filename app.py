# streamlit_app.py

import streamlit as st

# Initialize session state for UI toggle and chat histories
if "features_mode" not in st.session_state:
    st.session_state.features_mode = "default"  # Modes: 'default', 'search', 'selected'
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # Unified chat history for single input, split by Normal and Steered responses

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

# Define CSS styles for the sections
normal_section_style = """
    <div style="
        background-color: #f0f8ff;  /* Very light blue */
        border-radius: 10px;
        padding: 20px;
        margin: 10px;
    ">
"""
steered_section_style = """
    <div style="
        background-color: #f5fff0;  /* Very light green */
        border-radius: 10px;
        padding: 20px;
        margin: 10px;
    ">
"""
chat_bubble_style_normal = """
    <div style="
        background-color: lightblue;
        border-radius: 10px;
        padding: 10px;
        margin: 5px 0;
    ">
"""
chat_bubble_style_steered = """
    <div style="
        background-color: lightgreen;
        border-radius: 10px;
        padding: 10px;
        margin: 5px 0;
    ">
"""

# Main interface
st.title("Steer Models")

if st.session_state.features_mode == "default":
    # Render Normal section
    st.markdown(normal_section_style, unsafe_allow_html=True)
    st.subheader("NORMAL")
    st.markdown(f"### Model: Normal {model}")
    st.markdown("""I'm the default, non-steered model.""")

    # Chat history for NORMAL
    st.markdown("#### Chat - NORMAL")
    for chat in st.session_state.chat_history:
        st.markdown(f"👤: {chat['user_input']}", unsafe_allow_html=True)
        st.markdown(chat_bubble_style_normal + chat["normal_response"] + "</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)  # Close Normal section container

    # Render Steered section
    st.markdown(steered_section_style, unsafe_allow_html=True)
    st.subheader("STEERED")
    st.markdown(f"### Model: Steered {model}")
    st.markdown("""Choose a demo, select a preset, or manually search and add features.""")

    # Chat history for STEERED
    st.markdown("#### Chat - STEERED")
    for chat in st.session_state.chat_history:
        st.markdown(f"👤: {chat['user_input']}", unsafe_allow_html=True)
        st.markdown(chat_bubble_style_steered + chat["steered_response"] + "</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)  # Close Steered section container

    # Unified Chat Input
    st.markdown("### Send a Message")
    user_input = st.text_input("Send a message to both models:", key="user_input")
    if st.button("Send", key="send"):
        if user_input:
            # Generate mock responses for Normal and Steered models
            normal_response = f"[NORMAL] Echo: {user_input}"  # Replace with actual Normal model response
            steered_response = f"[STEERED] Echo: {user_input}"  # Replace with actual Steered model response

            # Append to chat history
            st.session_state.chat_history.append({
                "user_input": user_input,
                "normal_response": normal_response,
                "steered_response": steered_response,
            })

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



