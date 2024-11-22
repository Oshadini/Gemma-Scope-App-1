# File: steer_chatbot.py

import streamlit as st
import requests
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage

# Initialize Conversation Memory
if "default_memory" not in st.session_state:
    st.session_state.default_memory = ConversationBufferMemory()
if "steered_memory" not in st.session_state:
    st.session_state.steered_memory = ConversationBufferMemory()

# API details
SEARCH_API_URL = "https://www.neuronpedia.org/api/explanation/search-model"
CHAT_API_URL = "https://www.neuronpedia.org/api/steer-chat"
MODEL_ID = "gemma-2-9b-it"
HEADERS = {
    "Content-Type": "application/json",
    "X-Api-Key": "YOUR_TOKEN"
}

# Streamlit UI
st.title("Steer With SAE Features (Chat)")
st.sidebar.title("Settings")

# Step 1: User Input for Query
st.markdown("### Search for Explanations")
query = st.text_input("Enter your query (minimum 3 characters):")
search_results = []

if st.button("Search Explanations"):
    if len(query) >= 3:
        # Prepare API payload
        search_payload = {
            "modelId": MODEL_ID,
            "query": query
        }

        # API Call
        try:
            response = requests.post(SEARCH_API_URL, json=search_payload, headers=HEADERS)
            response.raise_for_status()
            search_results = response.json().get("results", [])

            # Display Results
            if search_results:
                st.markdown("### Search Results")
                for i, result in enumerate(search_results):
                    st.markdown(f"**{i + 1}. {result['explanation']}**")
            else:
                st.warning("No results found.")
        except requests.exceptions.RequestException as e:
            st.error(f"Search API request failed: {e}")
    else:
        st.warning("Query must be at least 3 characters long.")

# Step 2: User Selects Explanation
if search_results:
    selected_index = st.selectbox("Select an explanation:", range(len(search_results)))
    selected_result = search_results[selected_index]
    selected_layer = selected_result["layer"]
    selected_index_value = selected_result["index"]
    st.markdown(f"**Selected Layer:** {selected_layer}")
    st.markdown(f"**Selected Index:** {selected_index_value}")

# Sidebar Settings
layer = st.sidebar.text_input("Layer", value=selected_layer if search_results else "9-gemmascope-res-131k")
index = st.sidebar.number_input("Index", value=selected_index_value if search_results else 62610, step=1)
strength = st.sidebar.number_input("Strength", value=48, step=1)
temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.5)
n_tokens = st.sidebar.number_input("Tokens", value=48, step=1)
freq_penalty = st.sidebar.number_input("Frequency Penalty", value=2, step=1)
seed = st.sidebar.number_input("Seed", value=16, step=1)
strength_multiplier = st.sidebar.number_input("Strength Multiplier", value=4, step=1)
steer_special_tokens = st.sidebar.checkbox("Steer Special Tokens", value=True)

# Chat Interface
st.markdown("### Chat Interface")
user_input = st.text_input("Your Message:", key="user_input")
if st.button("Send"):
    if user_input:
        # Prepare API payload
        payload = {
            "defaultChatMessages": [
                {"role": "user", "content": user_input}
            ],
            "steeredChatMessages": [
                {"role": "user", "content": user_input}
            ],
            "modelId": MODEL_ID,
            "features": [
                {
                    "modelId": MODEL_ID,
                    "layer": layer,
                    "index": index,
                    "strength": strength
                }
            ],
            "temperature": temperature,
            "n_tokens": n_tokens,
            "freq_penalty": freq_penalty,
            "seed": seed,
            "strength_multiplier": strength_multiplier,
            "steer_special_tokens": steer_special_tokens
        }

        # API Call and Response Handling
        try:
            response = requests.post(CHAT_API_URL, json=payload, headers=HEADERS)
            response.raise_for_status()
            data = response.json()

            # Debugging: Print the entire API response
            st.write("API Response Data:", data)

            # Parse Default and Steered Chat Templates
            default_chat = data.get("DEFAULT", {}).get("chat_template", [])
            steered_chat = data.get("STEERED", {}).get("chat_template", [])

            # Extract the Latest Model Response for Default and Steered
            default_response = (
                default_chat[-1]["content"] if default_chat and default_chat[-1]["role"] == "model" else "No response"
            )
            steered_response = (
                steered_chat[-1]["content"] if steered_chat and steered_chat[-1]["role"] == "model" else "No response"
            )

            # Add User Input and Responses to Memory
            st.session_state.default_memory.chat_memory.add_user_message(user_input)
            st.session_state.default_memory.chat_memory.add_ai_message(default_response)

            st.session_state.steered_memory.chat_memory.add_user_message(user_input)
            st.session_state.steered_memory.chat_memory.add_ai_message(steered_response)

        except requests.exceptions.RequestException as e:
            st.error(f"Chat API request failed: {e}")
        except (IndexError, TypeError, KeyError) as e:
            st.error(f"Error parsing API response: {e}")

# Display Chat History
col1, col2 = st.columns(2)

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
