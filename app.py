# File: steer_chatbot.py

import streamlit as st
import requests
from langchain.memory import ConversationBufferMemory

# Initialize Conversation Memory
if "default_memory" not in st.session_state:
    st.session_state.default_memory = ConversationBufferMemory()
if "steered_memory" not in st.session_state:
    st.session_state.steered_memory = ConversationBufferMemory()

# Persistent state for selected features
if "selected_features" not in st.session_state:
    st.session_state.selected_features = []

# API details
SEARCH_API_URL = "https://www.neuronpedia.org/api/explanation/search-model"
STEER_CHAT_API_URL = "https://www.neuronpedia.org/api/steer-chat"
MODEL_ID = "gemma-2-9b-it"
HEADERS = {
    "Content-Type": "application/json",
    "X-Api-Key": "sk-np-h0ZsR5M1gY0w8al332rJUYa0C8hQL2yUogd5n4Pgvvg0"
}

# Streamlit UI
st.title("Steer With SAE Features (Chat)")
st.sidebar.title("Settings")

# Chat interface
st.markdown("### Chat Interface")
user_query = st.text_input("Enter your query (min 3 characters):")

if st.button("Search"):
    if len(user_query) < 3:
        st.error("Query must be at least 3 characters long.")
    else:
        # Prepare payload for search API
        search_payload = {
            "modelId": MODEL_ID,
            "query": user_query
        }

        try:
            search_response = requests.post(SEARCH_API_URL, json=search_payload, headers=HEADERS)
            search_response.raise_for_status()
            search_data = search_response.json()

            # Extract explanations
            explanations = search_data.get("explanations", [])
            if not explanations:
                st.info("No explanations found for the query.")
            else:
                st.session_state.current_explanations = explanations

                # Display all descriptions
                for idx, explanation in enumerate(explanations):
                    description = explanation.get("description", "No description")
                    layer = explanation.get("layer")
                    index = explanation.get("index")
                    if st.button(f"Select: {description}"):
                        # Add selected feature to session state
                        st.session_state.selected_features.append({
                            "modelId": MODEL_ID,
                            "layer": layer,
                            "index": index
                        })
                        st.success(f"Selected: {description}")

        except requests.exceptions.RequestException as e:
            st.error(f"Search API request failed: {e}")

# Display selected features
st.markdown("### Selected Features")
if st.session_state.selected_features:
    for feature in st.session_state.selected_features:
        st.markdown(f"- **Layer**: {feature['layer']}, **Index**: {feature['index']}")
else:
    st.info("No features selected yet.")

# Chat input
user_input = st.text_input("Your Message for the Steered Chat:")
if st.button("Send"):
    if user_input:
        # Prepare steered chat API payload
        payload = {
            "defaultChatMessages": [{"role": "user", "content": user_input}],
            "steeredChatMessages": [{"role": "user", "content": user_input}],
            "modelId": MODEL_ID,
            "features": st.session_state.selected_features,
            "temperature": 0.5,
            "n_tokens": 48,
            "freq_penalty": 2,
            "seed": 16,
            "strength_multiplier": 4,
            "steer_special_tokens": True
        }

        try:
            response = requests.post(STEER_CHAT_API_URL, json=payload, headers=HEADERS)
            response.raise_for_status()
            data = response.json()

            # Parse and display API responses
            default_chat = data.get("DEFAULT", {}).get("chat_template", [])
            steered_chat = data.get("STEERED", {}).get("chat_template", [])

            default_response = (
                default_chat[-1]["content"] if default_chat and default_chat[-1]["role"] == "model" else "No response"
            )
            steered_response = (
                steered_chat[-1]["content"] if steered_chat and steered_chat[-1]["role"] == "model" else "No response"
            )

            st.session_state.default_memory.chat_memory.add_user_message(user_input)
            st.session_state.default_memory.chat_memory.add_ai_message(default_response)

            st.session_state.steered_memory.chat_memory.add_user_message(user_input)
            st.session_state.steered_memory.chat_memory.add_ai_message(steered_response)

            st.write("### Default Model Response")
            st.write(default_response)
            st.write("### Steered Model Response")
            st.write(steered_response)

        except requests.exceptions.RequestException as e:
            st.error(f"API request failed: {e}")
        except (IndexError, TypeError, KeyError) as e:
            st.error(f"Error parsing API response: {e}")

# Display Chat History
col1, col2 = st.columns(2)

from langchain.schema import HumanMessage, AIMessage

# Display Default Model Chat
with col1:
    st.subheader("Default Model Chat")
    for message in st.session_state.default_memory.chat_memory.messages:
        if isinstance(message, HumanMessage):
            st.markdown(f"**👤 User:** {message.content}")
        elif isinstance(message, AIMessage):
            st.markdown(f"**🤖 Default Model:** {message.content}")

# Display Steered Model Chat
with col2:
    st.subheader("Steered Model Chat")
    for message in st.session_state.steered_memory.chat_memory.messages:
        if isinstance(message, HumanMessage):
            st.markdown(f"**👤 User:** {message.content}")
        elif isinstance(message, AIMessage):
            st.markdown(f"**🤖 Steered Model:** {message.content}")
