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

# Main interface
st.title("Steer Models")

# CSS to apply separate background colors to each section
st.markdown("""
    <style>
        .left-column {
            background-color: #f9f9f9; /* Light gray for Normal section */
            padding: 20px;
            border-radius: 10px;
        }
        .right-column {
            background-color: #eaf7ff; /* Light blue for Steered section */
            padding: 20px;
            border-radius: 10px;
        }
        .full-width {
            margin: 0 auto;
            width: 100%;
        }
    </style>
""", unsafe_allow_html=True)

if st.session_state.features_mode == "default":
    # Default UI with Normal and Steered Headers
    col1, col2 = st.columns([1, 1], gap="medium")

    with col1:
        st.markdown('<div class="left-column">', unsafe_allow_html=True)
        st.subheader("NORMAL")
        st.markdown(f"### Model: Normal {model}")
        st.markdown("""I'm the default, non-steered model.""")

        # Normal Chat History
        with st.container():
            st.markdown("#### Chat - NORMAL")
            for chat in st.session_state.chat_history:
                st.markdown(f"👤: {chat['user_input']}", unsafe_allow_html=True)
                st.markdown(f"""
                    <div style="background-color: lightblue; border-radius: 10px; padding: 10px; margin: 5px 0;">
                        {chat['normal_response']}
                    </div>
                """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="right-column">', unsafe_allow_html=True)
        st.subheader("STEERED")
        st.markdown(f"### Model: Steered {model}")
        st.markdown("""Choose a demo, select a preset, or manually search and add features.""")

        # Steered Chat History
        with st.container():
            st.markdown("#### Chat - STEERED")
            for chat in st.session_state.chat_history:
                st.markdown(f"👤: {chat['user_input']}", unsafe_allow_html=True)
                st.markdown(f"""
                    <div style="background-color: lightgreen; border-radius: 10px; padding: 10px; margin: 5px 0;">
                        {chat['steered_response']}
                    </div>
                """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

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

# The "search" and "selected" modes remain unchanged
elif st.session_state.features_mode == "search":
    st.subheader("Search for Features")
    # Remaining implementation for 'search' mode...

elif st.session_state.features_mode == "selected":
    st.subheader("Selected Features")
    # Remaining implementation for 'selected' mode...


