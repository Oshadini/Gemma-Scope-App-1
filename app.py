# File: steer_chatbot.py

import streamlit as st
import requests
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage

# Initialize Session State
if "default_memory" not in st.session_state:
    st.session_state.default_memory = ConversationBufferMemory()
if "steered_memory" not in st.session_state:
    st.session_state.steered_memory = ConversationBufferMemory()
if "selected_features" not in st.session_state:
    st.session_state.selected_features = []  # To store selected descriptions, layer, index, and strength
if "available_descriptions" not in st.session_state:
    st.session_state.available_descriptions = []  # To temporarily store descriptions for a query

# API details
API_URL = "https://www.neuronpedia.org/api/steer-chat"
SEARCH_API_URL = "https://www.neuronpedia.org/api/explanation/search-model"
MODEL_ID = "gemma-2-9b-it"
HEADERS = {"Content-Type": "application/json", "X-Api-Key": "YOUR_TOKEN"}

# Main Application UI
st.set_page_config(page_title="Steer With SAE Features (Chat)", layout="wide")
st.title("🚀 Steer Chatbot with SAE Features")

# Sidebar: Settings and Search
st.sidebar.header("Settings")
st.sidebar.markdown("Adjust the parameters below to customize the behavior of the chatbot.")

# Search Query
st.sidebar.markdown("### 🔍 Search for Explanations")
query = st.sidebar.text_input("Enter your query:", key="query_input", placeholder="Type your query here...")

if st.sidebar.button("Search 🔎"):
    if len(query) >= 3:
        try:
            # Call the Search API
            search_payload = {"modelId": MODEL_ID, "query": query}
            search_response = requests.post(SEARCH_API_URL, json=search_payload, headers=HEADERS)
            search_response.raise_for_status()
            search_data = search_response.json()

            explanations = search_data.get("results", [])
            if explanations:
                st.session_state.available_descriptions = [
                    {
                        "description": exp["description"],
                        "layer": exp["layer"],
                        "index": exp["index"],
                        "strength": exp.get("strength", 40),  # Default strength to 40 if not provided
                    }
                    for exp in explanations
                ]
                st.sidebar.success("Explanations loaded successfully!")
            else:
                st.sidebar.warning("No explanations found for the query.")
        except requests.exceptions.RequestException as e:
            st.sidebar.error(f"Search API request failed: {e}")
    else:
        st.sidebar.error("Query must be at least 3 characters long.")

# Feature Selection
if st.session_state.available_descriptions:
    descriptions = [desc["description"] for desc in st.session_state.available_descriptions]
    selected_description = st.sidebar.selectbox("Select an explanation:", [""] + descriptions, key="description_select")

    if selected_description:
        # Add selected feature
        feature = next(
            (desc for desc in st.session_state.available_descriptions if desc["description"] == selected_description),
            None,
        )
        if feature and feature not in st.session_state.selected_features:
            st.session_state.selected_features.append(feature)
            st.session_state.available_descriptions = []  # Clear temporary storage after selection
            del st.session_state["description_select"]  # Remove dropdown from UI
            st.sidebar.success(f"Feature added: {selected_description}")

# Display selected features with sliders and remove buttons
# Display selected features with sliders and remove buttons
# Display selected features with sliders and remove buttons
# Display selected features with sliders and remove buttons
# Display selected features with sliders and remove buttons
import streamlit as st

# Display selected features with sliders and remove buttons
st.sidebar.markdown("### 🎛 Selected Features")

if st.session_state.selected_features:
    for feature in st.session_state.selected_features:
        # Use a container to group the slider and the remove button
        with st.sidebar.container():
            col1, col2 = st.sidebar.columns([4, 1])  # Create two columns: one for the slider, one for the button

            # Display the slider
            with col1:
                st.slider(
                    feature["description"],
                    min_value=-100,
                    max_value=100,
                    value=feature["strength"],
                    key=f"strength_{feature['description']}",
                )

            # Display the remove button
            with col2:
                #button_key = f"remove_{feature['description']}"
                button_key = f"strength_{feature['description']}"
                
                # Show the button and check if clicked
                if st.button("❌", key=button_key):
                    # Remove the feature from the session state
                    st.session_state.selected_features = [
                        f for f in st.session_state.selected_features if f != feature
                    ]
                    # Clear the specific slider key
                    slider_key = f"strength_{feature['description']}"
                    if slider_key in st.session_state:
                        del st.session_state[slider_key]

                    # No need to rerun, the UI will naturally update after state change

else:
    st.sidebar.info("No features selected yet.")





# Chat Settings
st.sidebar.markdown("### ⚙️ Chat Settings")
temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.5, help="Adjust the creativity of the responses.")
n_tokens = st.sidebar.number_input("Max Tokens", value=48, step=1, help="Set the maximum token limit for responses.")
freq_penalty = st.sidebar.number_input("Frequency Penalty", value=2, step=1, help="Discourage repetitive responses.")
seed = st.sidebar.number_input("Seed", value=16, step=1, help="Set the random seed for reproducible results.")
strength_multiplier = st.sidebar.number_input("Strength Multiplier", value=4, step=1, help="Boost selected feature strength.")
steer_special_tokens = st.sidebar.checkbox("Steer Special Tokens", value=True)

# Main Chat Interface
st.markdown("### 💬 Chat Interface")
chat_col1, chat_col2 = st.columns([1, 1])

with chat_col2:  # Default chat on the right
    st.markdown("#### Default Chat")
    for message in st.session_state.default_memory.chat_memory.messages:
        if isinstance(message, HumanMessage):
            st.markdown(f"**👤 User:** {message.content}")
        elif isinstance(message, AIMessage):
            st.markdown(f"**🤖 Default Model:** {message.content}")

with chat_col1:  # Steered chat on the left
    st.markdown("#### Steered Chat")
    for message in st.session_state.steered_memory.chat_memory.messages:
        if isinstance(message, HumanMessage):
            st.markdown(f"**👤 User:** {message.content}")
        elif isinstance(message, AIMessage):
            st.markdown(f"**🤖 Steered Model:** {message.content}")

# Fixed user input at the bottom
user_input = st.text_input(
    "Your Message:",
    key="user_input",
    placeholder="Type your message here...",
    label_visibility="hidden",
)
send_button = st.button("Send 📨", use_container_width=True)

if send_button and user_input:
    if user_input:
        features = [
            {
                "modelId": MODEL_ID,
                "layer": feature["layer"],
                "index": feature["index"],
                "strength": feature["strength"],
            }
            for feature in st.session_state.selected_features
        ]

        # Debugging: Log features being sent
        st.write("**Features Sent to API:**", features)

        payload = {
            "defaultChatMessages": [{"role": "user", "content": user_input}],
            "steeredChatMessages": [{"role": "user", "content": user_input}],
            "modelId": MODEL_ID,
            "features": features,
            "temperature": temperature,
            "n_tokens": n_tokens,
            "freq_penalty": freq_penalty,
            "seed": seed,
            "strength_multiplier": strength_multiplier,
            "steer_special_tokens": steer_special_tokens,
        }

        try:
            response = requests.post(API_URL, json=payload, headers=HEADERS)
            response.raise_for_status()
            data = response.json()

            # Debugging: Log API response
            st.write("**API Response:**", data)

            # Display responses
            default_response = data.get("DEFAULT", {}).get("chat_template", [])[-1].get("content", "No response")
            steered_response = data.get("STEERED", {}).get("chat_template", [])[-1].get("content", "No response")

            if not steered_response or steered_response == "No response":
                st.warning("Steered response not generated or not influenced by selected features.")
            else:
                st.success("Steered response generated successfully!")

            # Save responses in memory
            st.session_state.default_memory.chat_memory.add_user_message(user_input)
            st.session_state.default_memory.chat_memory.add_ai_message(default_response)
            st.session_state.steered_memory.chat_memory.add_user_message(user_input)
            st.session_state.steered_memory.chat_memory.add_ai_message(steered_response)

        except requests.exceptions.RequestException as e:
            st.error(f"API request failed: {e}")
