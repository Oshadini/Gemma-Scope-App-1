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
if "show_dropdown" not in st.session_state:
    st.session_state.show_dropdown = False  # To control the visibility of the dropdown

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
                        "strength": exp.get("strength", 40),  # Default strength to 40 if not provided
                    }
                    for exp in explanations
                ]
                st.session_state.show_dropdown = True  # Show dropdown after a search
            else:
                st.sidebar.error("No explanations found.")
        except requests.exceptions.RequestException as e:
            st.sidebar.error(f"Search API request failed: {e}")
    else:
        st.sidebar.error("Query must be at least 3 characters long.")

# Handle description selection
if st.session_state.show_dropdown and st.session_state.available_descriptions:
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
            st.session_state.show_dropdown = False  # Hide dropdown after selection
            st.sidebar.success(f"Feature added: {selected_description}")

# Display selected descriptions with sliders and remove buttons
st.sidebar.markdown("### Selected Features")
if st.session_state.selected_features:
    updated_features = []
    for i, feature in enumerate(st.session_state.selected_features):
        col1, col2 = st.sidebar.columns([4, 1])  # Create two columns for slider and button
        remove_clicked = False
        with col1:
            # Show the slider only if the feature is not marked for removal
            if feature not in updated_features:
                feature["strength"] = st.slider(
                    f"Strength for '{feature['description']}'",
                    min_value=-100,
                    max_value=100,
                    value=feature["strength"],
                    key=f"strength_{feature['description']}",
                )
        with col2:
            if st.button("Remove", key=f"remove_{feature['description']}"):
                remove_clicked = True
        # Add the feature to updated_features if not removed
        if not remove_clicked:
            updated_features.append(feature)

    # Update session state with the remaining features
    st.session_state.selected_features = updated_features
else:
    st.sidebar.markdown("No features selected yet.")

# User input for other settings
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

            # Display responses
            st.markdown("### Default Model Response")
            st.write(default_chat[-1]["content"] if default_chat else "No response")

            st.markdown("### Steered Model Response")
            if features:
                for feature in features:
                    st.markdown(f"- {feature['layer']}:{feature['index']} - {feature['strength']}")
                st.write(steered_chat[-1]["content"] if steered_chat else "No response")
            else:
                st.warning("No features selected. Steered response may not be influenced.")

        except requests.exceptions.RequestException as e:
            st.error(f"API request failed: {e}")
