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

# CSS to create full-height background colors for both sections
st.markdown("""
    <style>
        .container {
            display: flex;
            width: 100%;
            height: 100vh; /* Full screen height */
            margin: 0;
            padding: 0;
        }
        .left-pane {
            flex: 1;
            background-color: #f9f9f9; /* Light gray for NORMAL */
            padding: 20px;
            box-sizing: border-box;
        }
        .right-pane {
            flex: 1;
            background-color: #eaf7ff; /* Light blue for STEERED */
            padding: 20px;
            box-sizing: border-box;
        }
        .response-box {
            background-color: rgba(173, 216, 230, 0.5); /* Light blue for NORMAL chat */
            border-radius: 10px;
            padding: 10px;
            margin: 10px 0;
        }
        .response-box-steered {
            background-color: rgba(144, 238, 144, 0.5); /* Light green for STEERED chat */
            border-radius: 10px;
            padding: 10px;
            margin: 10px 0;
        }
    </style>
""", unsafe_allow_html=True)

if st.session_state.features_mode == "default":
    # Full-width layout using CSS
    st.markdown('<div class="container">', unsafe_allow_html=True)
    
    # Left column for NORMAL
    st.markdown('<div class="left-pane">', unsafe_allow_html=True)
    st.subheader("NORMAL")
    st.markdown(f"### Model: Normal {model}")
    st.markdown("""I'm the default, non-steered model.""")

    # Normal Chat History
    st.markdown("#### Chat - NORMAL")
    for chat in st.session_state.chat_history:
        st.markdown(f"👤: {chat['user_input']}", unsafe_allow_html=True)
        st.markdown(f"""
            <div class="response-box">
                {chat['normal_response']}
            </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Right column for STEERED
    st.markdown('<div class="right-pane">', unsafe_allow_html=True)
    st.subheader("STEERED")
    st.markdown(f"### Model: Steered {model}")
    st.markdown("""Choose a demo, select a preset, or manually search and add features.""")

    # Steered Chat History
    st.markdown("#### Chat - STEERED")
    for chat in st.session_state.chat_history:
        st.markdown(f"👤: {chat['user_input']}", unsafe_allow_html=True)
        st.markdown(f"""
            <div class="response-box-steered">
                {chat['steered_response']}
            </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)  # Close container

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

# "search" and "selected" modes remain unchanged
elif st.session_state.features_mode == "search":
    st.subheader("Search for Features")
    # Remaining implementation for 'search' mode...

elif st.session_state.features_mode == "selected":
    st.subheader("Selected Features")
    # Remaining implementation for 'selected' mode...


