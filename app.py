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
    st.session_state.selected_features = []  # To store selected descriptions, layer, and index
if "available_descriptions" not in st.session_state:
    st.session_state.available_descriptions = []  # To temporarily store descriptions for a query

# API details
API_URL = "https://www.neuronpedia.org/api/steer-chat"
SEARCH_API_URL = "https://www.neuronpedia.org/api/explanation/search-model"
MODEL_ID = "gemma-2-9b-it"
HEADERS = {"Content-Type": "application/json", "X-Api-Key": "YOUR_TOKEN"}

# Streamlit UI
st.title("Steer With SAE Features (Chat)")
st.sidebar.title("Settings")

# User input for search query
st.sidebar.markdown("### Search for Explanations")
query = st.sidebar.text_input("Enter Query:", key="query_input", placeholder="Search for explanations...")

# Search and display results
if st.sidebar.button("Search"):
    if len(query) >= 3:
        try:
            # Call the Search API
            search_payload = {"modelId": MODEL_ID, "query": query}
            search_response = requests.post(SEARCH_API_URL, json=search_payload, headers=HEADERS)
            search_response.raise_for_status()
            search_data = search_response.json()

            explanations = search_data.get("results", [])
            if explanations:
                # Extract and display explanation descriptions for user selection
                st.session_state.available_descriptions = [
                    {
                        "description": exp["description"],
                        "layer": exp["layer"],
                        "index": exp["index"],
                    }
                    for exp in explanations
                ]
            else:
                st.sidebar.error("No explanations found.")
        except requests.exceptions.RequestException as e:
            st.sidebar.error(f"Search API request failed: {e}")
    else:
        st.sidebar.error("Query must be at least 3 characters long.")

# Handle description selection
if st.session_state.available_descriptions:
    descriptions = [desc["description"] for desc in st.session_state.available_descriptions]
    selected_description = st.sidebar.selectbox("Select an explanation", [""] + descriptions)
    if selected_description:
        # Find the corresponding feature and add it to the selected features
        feature = next(
            (desc for desc in st.session_state.available_descriptions if desc["description"] == selected_description),
            None,
        )
        if feature and feature not in st.session_state.selected_features:
            st.session_state.selected_features.append(feature)
            st.session_state.available_descriptions = []  # Clear temporary storage after selection
            st.sidebar.success(f"Feature added: {selected_description}")

# Display selected descriptions with sliders for strength adjustment
st.sidebar.markdown("### Selected Features")
if st.session_state.selected_features:
    for feature in st.session_state.selected_features:
        feature["strength"] = st.sidebar.slider(
            f"Strength for '{feature['description']}'",
            min_value=-100,
            max_value=100,
            value=feature.get("strength", 0),  # Default to 0 if not already set
            key=f"strength_{feature['description']}",
        )
        st.sidebar.markdown(
            f"- **Description**: {feature['description']}<br>"
            f"  **Layer**: {feature['layer']}<br>"
            f"  **Index**: {feature['index']}",
            unsafe_allow_html=True,
        )
else:
    st.sidebar.markdown("No features selected yet.")

# User input for features
layer = st.sidebar.text_input("Layer", value="9-gemmascope-res-131k")
index = st.sidebar.number_input("Index", value=62610, step=1)
strength = st.sidebar.number_input("Strength", value=48, step=1)
temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.5)
n_tokens = st.sidebar.number_input("Tokens", value=48, step=1)
freq_penalty = st.sidebar.number_input("Frequency Penalty", value=2, step=1)
seed = st.sidebar.number_input("Seed", value=16, step=1)
strength_multiplier = st.sidebar.number_input("Strength Multiplier", value=4, step=1)
steer_special_tokens = st.sidebar.checkbox("Steer Special Tokens", value=True)

# Chat interface
st.markdown("### Chat Interface")
user_input = st.text_input("Your Message:", key="user_input")
if st.button("Send"):
    if user_input:
        # Prepare features for the API payload
        features = [
            {
                "modelId": MODEL_ID,
                "layer": feature["layer"],
                "index": feature["index"],
                "strength": feature["strength"],  # Use slider-adjusted strength
            }
            for feature in st.session_state.selected_features
        ]

        # Prepare API payload
        payload = {
            "defaultChatMessages": [
                {"role": "user", "content": user_input}
            ],
            "steeredChatMessages": [
                {"role": "user", "content": user_input}
            ],
            "modelId": MODEL_ID,
            "features": features,
            "temperature": temperature,
            "n_tokens": n_tokens,
            "freq_penalty": freq_penalty,
            "seed": seed,
            "strength_multiplier": strength_multiplier,
            "steer_special_tokens": steer_special_tokens,
        }

        # API Call and response handling
        try:
            response = requests.post(API_URL, json=payload, headers=HEADERS)
            response.raise_for_status()
            data = response.json()

            # Parse Default and Steered chat templates
            default_chat = data.get("DEFAULT", {}).get("chat_template", [])
            steered_chat = data.get("STEERED", {}).get("chat_template", [])

            # Extract the latest model response for default and steered
            default_response = (
                default_chat[-1]["content"] if default_chat and default_chat[-1]["role"] == "model" else "No response"
            )
            steered_response = (
                steered_chat[-1]["content"] if steered_chat and steered_chat[-1]["role"] == "model" else "No response"
            )

            # Add user input and responses to memory
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
