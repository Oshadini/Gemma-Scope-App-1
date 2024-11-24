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
if "explanation_selected" not in st.session_state:
    st.session_state.explanation_selected = False  # Tracks if an explanation is selected

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
            # Reset explanation selection state
            st.session_state.explanation_selected = False
            
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
            else:
                st.sidebar.error("No explanations found.")
        except requests.exceptions.RequestException as e:
            st.sidebar.error(f"Search API request failed: {e}")
    else:
        st.sidebar.error("Query must be at least 3 characters long.")

# Handle description selection
if st.session_state.available_descriptions and not st.session_state.explanation_selected:
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
            st.session_state.explanation_selected = True  # Explanation is selected
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
