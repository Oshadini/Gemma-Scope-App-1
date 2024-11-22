# File: steer_chatbot.py

import streamlit as st
import requests
from langchain.memory import ConversationBufferMemory

# Initialize Session State
if "default_memory" not in st.session_state:
    st.session_state.default_memory = ConversationBufferMemory()
if "steered_memory" not in st.session_state:
    st.session_state.steered_memory = ConversationBufferMemory()
if "selected_descriptions" not in st.session_state:
    st.session_state.selected_descriptions = {}
if "feature_details" not in st.session_state:
    st.session_state.feature_details = {}

# API details
SEARCH_API_URL = "https://www.neuronpedia.org/api/explanation/search-model"
STEER_API_URL = "https://www.neuronpedia.org/api/steer-chat"
MODEL_ID = "gemma-2-9b-it"
HEADERS = {
    "Content-Type": "application/json",
    "X-Api-Key": "sk-np-h0ZsR5M1gY0w8al332rJUYa0C8hQL2yUogd5n4Pgvvg0"
}

# Streamlit UI
st.title("Steer With SAE Features (Chat)")
st.sidebar.title("Settings")

# Sidebar to display selected descriptions
st.sidebar.markdown("### Selected Features")
for query, descriptions in st.session_state.selected_descriptions.items():
    st.sidebar.markdown(f"**Query: {query}**")
    for desc in descriptions:
        st.sidebar.markdown(f"- {desc}")

# User input for querying
st.markdown("### Query Explanations")
query_input = st.text_input("Enter your query (min 3 characters):")
if st.button("Search"):
    if len(query_input) >= 3:
        # Search API Call
        payload = {
            "modelId": MODEL_ID,
            "query": query_input
        }
        try:
            response = requests.post(SEARCH_API_URL, json=payload, headers=HEADERS)
            response.raise_for_status()
            data = response.json()

            # Extract "description", "layer", and "index"
            explanations = data.get("results", [])
            if explanations:
                options = [
                    (exp["description"], exp["layer"], exp["index"]) for exp in explanations
                ]
                st.session_state.feature_details[query_input] = options

                # Display descriptions
                st.markdown(f"#### Results for '{query_input}'")
                for i, (desc, _, _) in enumerate(options, 1):
                    st.write(f"{i}. {desc}")
            else:
                st.warning(f"No results found for '{query_input}'.")

        except requests.exceptions.RequestException as e:
            st.error(f"API request failed: {e}")
    else:
        st.error("Query must be at least 3 characters long.")

# User selection of descriptions
if query_input in st.session_state.feature_details:
    options = st.session_state.feature_details[query_input]
    descriptions = [opt[0] for opt in options]
    selected_desc = st.selectbox(
        "Select a description to add to features:",
        [""] + descriptions
    )
    if st.button("Add Feature"):
        if selected_desc:
            selected_option = next(
                (opt for opt in options if opt[0] == selected_desc), None
            )
            if selected_option:
                desc, layer, index = selected_option
                if query_input not in st.session_state.selected_descriptions:
                    st.session_state.selected_descriptions[query_input] = []
                if desc not in st.session_state.selected_descriptions[query_input]:
                    st.session_state.selected_descriptions[query_input].append(desc)

# Prepare features for the steer API
features = []
for query, descriptions in st.session_state.selected_descriptions.items():
    for desc in descriptions:
        for option in st.session_state.feature_details.get(query, []):
            if option[0] == desc:
                features.append({
                    "modelId": MODEL_ID,
                    "layer": option[1],
                    "index": option[2],
                    "strength": 48  # Default strength value
                })

# Chat interface
st.markdown("### Chat Interface")
user_input = st.text_input("Your Message:", key="user_input")
if st.button("Send"):
    if user_input:
        # Prepare payload for steer API
        payload = {
            "defaultChatMessages": [{"role": "user", "content": user_input}],
            "steeredChatMessages": [{"role": "user", "content": user_input}],
            "modelId": MODEL_ID,
            "features": features,
            "temperature": 0.5,  # Default temperature
            "n_tokens": 48,  # Default token count
            "freq_penalty": 2,  # Default frequency penalty
            "seed": 16,  # Default seed
            "strength_multiplier": 4,  # Default multiplier
            "steer_special_tokens": True  # Default special tokens
        }

        # Steer API Call
        try:
            response = requests.post(STEER_API_URL, json=payload, headers=HEADERS)
            response.raise_for_status()
            data = response.json()

            # Parse responses
            default_chat = data.get("DEFAULT", {}).get("chat_template", [])
            steered_chat = data.get("STEERED", {}).get("chat_template", [])

            default_response = (
                default_chat[-1]["content"] if default_chat and default_chat[-1]["role"] == "model" else "No response"
            )
            steered_response = (
                steered_chat[-1]["content"] if steered_chat and steered_chat[-1]["role"] == "model" else "No response"
            )

            # Add responses to memory
            st.session_state.default_memory.chat_memory.add_user_message(user_input)
            st.session_state.default_memory.chat_memory.add_ai_message(default_response)

            st.session_state.steered_memory.chat_memory.add_user_message(user_input)
            st.session_state.steered_memory.chat_memory.add_ai_message(steered_response)

        except requests.exceptions.RequestException as e:
            st.error(f"API request failed: {e}")
        except (IndexError, TypeError, KeyError) as e:
            st.error(f"Error parsing API response: {e}")

# Display Chat History
col1, col2 = st.columns(2)

from langchain.schema import HumanMessage, AIMessage

# Default Model Chat
with col1:
    st.subheader("Default Model Chat")
    for message in st.session_state.default_memory.chat_memory.messages:
        if isinstance(message, HumanMessage):
            st.markdown(f"**👤 User:** {message.content}")
        elif isinstance(message, AIMessage):
            st.markdown(f"**🤖 Default Model:** {message.content}")

# Steered Model Chat
with col2:
    st.subheader("Steered Model Chat")
    for message in st.session_state.steered_memory.chat_memory.messages:
        if isinstance(message, HumanMessage):
            st.markdown(f"**👤 User:** {message.content}")
        elif isinstance(message, AIMessage):
            st.markdown(f"**🤖 Steered Model:** {message.content}")
