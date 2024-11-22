# File: steer_chatbot.py

import streamlit as st
import requests

# API details
MODEL_ID = "gemma-2-9b-it"
SEARCH_API_URL = "https://www.neuronpedia.org/api/explanation/search-model"
CHAT_API_URL = "https://www.neuronpedia.org/api/steer-chat"
HEADERS = {
    "Content-Type": "application/json",
    "X-Api-Key": "sk-np-h0ZsR5M1gY0w8al332rJUYa0C8hQL2yUogd5n4Pgvvg0"
}

# Streamlit UI
st.title("Steer With SAE Features (Chat)")
st.sidebar.title("Settings")

# State initialization
if "selected_features" not in st.session_state:
    st.session_state.selected_features = []

# Step 1: User enters query
query = st.text_input("Enter a query to search explanations (min 3 characters):")

if st.button("Search Explanations"):
    if len(query) < 3:
        st.warning("Query must be at least 3 characters long.")
    else:
        # Make the API request
        search_payload = {"modelId": MODEL_ID, "query": query}
        try:
            response = requests.post(SEARCH_API_URL, json=search_payload, headers=HEADERS)
            response.raise_for_status()
            explanations = response.json().get("results", [])
            
            if not explanations:
                st.info("No explanations found for the given query.")
            else:
                # Display explanation descriptions
                descriptions = [
                    {"description": e["description"], "layer": e["layer"], "index": e["index"]}
                    for e in explanations
                ]
                st.session_state.descriptions = descriptions
                for i, desc in enumerate(descriptions):
                    st.write(f"**{i + 1}. {desc['description']}** (Layer: {desc['layer']}, Index: {desc['index']})")
        except requests.exceptions.RequestException as e:
            st.error(f"API request failed: {e}")

# Step 2: User selects description(s)
if "descriptions" in st.session_state and st.session_state.descriptions:
    selected_description = st.selectbox(
        "Select an explanation by description (based on the search above):",
        options=[desc["description"] for desc in st.session_state.descriptions]
    )
    if st.button("Add Selected Explanation"):
        # Get the full explanation details
        selected_feature = next(
            (desc for desc in st.session_state.descriptions if desc["description"] == selected_description),
            None
        )
        if selected_feature:
            st.session_state.selected_features.append(selected_feature)
            st.success(f"Added: {selected_description}")

# Display selected features
if st.session_state.selected_features:
    st.subheader("Selected Features:")
    for feature in st.session_state.selected_features:
        st.write(f"- **{feature['description']}** (Layer: {feature['layer']}, Index: {feature['index']})")

# Step 3: Chat interface with steered features
st.markdown("### Chat Interface")
user_input = st.text_input("Your Message:", key="user_input")
if st.button("Send"):
    if user_input:
        # Prepare the features payload
        features_payload = [
            {
                "modelId": MODEL_ID,
                "layer": feature["layer"],
                "index": feature["index"]
            }
            for feature in st.session_state.selected_features
        ]

        # Prepare the API payload
        chat_payload = {
            "defaultChatMessages": [{"role": "user", "content": user_input}],
            "steeredChatMessages": [{"role": "user", "content": user_input}],
            "modelId": MODEL_ID,
            "features": features_payload,
            "temperature": 0.5,
            "n_tokens": 48,
            "freq_penalty": 2,
            "seed": 16,
            "strength_multiplier": 4,
            "steer_special_tokens": True
        }

        # Send the API request
        try:
            response = requests.post(CHAT_API_URL, json=chat_payload, headers=HEADERS)
            response.raise_for_status()
            data = response.json()

            # Parse responses
            default_response = data.get("DEFAULT", {}).get("chat_template", [])
            steered_response = data.get("STEERED", {}).get("chat_template", [])

            st.subheader("Chat Responses")
            st.write("**Default Model Response:**")
            st.write(default_response[-1]["content"] if default_response else "No response")
            st.write("**Steered Model Response:**")
            st.write(steered_response[-1]["content"] if steered_response else "No response")

        except requests.exceptions.RequestException as e:
            st.error(f"API request failed: {e}")
