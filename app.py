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

# Display selected features with sliders
st.sidebar.markdown("### 🎛 Selected Features")
if st.session_state.selected_features:
    for feature in st.session_state.selected_features:
        col1, col2 = st.sidebar.columns([4, 1])
        with col1:
            st.sidebar.slider(
                f"{feature['description']}",
                min_value=-100,
                max_value=100,
                value=feature["strength"],
                key=f"strength_{feature['description']}",
            )
        with col2:
            if st.sidebar.button("❌", key=f"remove_{feature['description']}"):
                st.session_state.selected_features.remove(feature)
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
messages = st.container()
user_input = st.text_input("Your Message:", key="user_input", placeholder="Type a message...")

if st.button("Send 📨", key="send_button"):
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

            # Display responses
            default_response = data.get("DEFAULT", {}).get("chat_template", [])[-1].get("content", "No response")
            steered_response = data.get("STEERED", {}).get("chat_template", [])[-1].get("content", "No response")

            st.session_state.default_memory.chat_memory.add_user_message(user_input)
            st.session_state.default_memory.chat_memory.add_ai_message(default_response)
            st.session_state.steered_memory.chat_memory.add_user_message(user_input)
            st.session_state.steered_memory.chat_memory.add_ai_message(steered_response)

        except requests.exceptions.RequestException as e:
            st.error(f"API request failed: {e}")

# Display Chat History
with messages:
    st.markdown("#### Chat History")
    for message in st.session_state.default_memory.chat_memory.messages:
        if isinstance(message, HumanMessage):
            st.chat_message("user").write(message.content)
        elif isinstance(message, AIMessage):
            st.chat_message("assistant").write(message.content)

    for message in st.session_state.steered_memory.chat_memory.messages:
        if isinstance(message, AIMessage):
            st.chat_message("assistant").write(f"Steered: {message.content}")
