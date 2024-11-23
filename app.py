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
            feature["strength"] = 48  # Default strength
            st.session_state.selected_features.append(feature)
            st.session
