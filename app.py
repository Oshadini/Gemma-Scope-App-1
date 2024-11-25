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
    st.session_state.selected_features = []
if "available_descriptions" not in st.session_state:
    st.session_state.available_descriptions = []

# API details
API_URL = "https://www.neuronpedia.org/api/steer-chat"
SEARCH_API_URL = "https://www.neuronpedia.org/api/explanation/search-model"
MODEL_ID = "gemma-2-9b-it"
HEADERS = {"Content-Type": "application/json", "X-Api-Key": "YOUR_TOKEN"}

# Set page configuration
st.set_page_config(page_title="Steer Chatbot", layout="wide")
st.title("🚀 Steer Chatbot with SAE Features")

# Sidebar: Search and Settings
st.sidebar.header("Settings")
query = st.sidebar.text_input("Enter your query:", key="query_input", placeholder="Type your query here...")

if st.sidebar.button("Search 🔎"):
    if len(query) >= 3:
        try:
            search_payload = {"modelId": MODEL_ID, "query": query}
            search_response = requests.post(SEARCH_API_URL, json=search_payload, headers=HEADERS)
            search_response.raise_for_status()
            search_data = search_response.json()

            explanations = search_data.get("results", [])
            if explanations:
                st.session_state.available_descriptions = [
                    {"description": exp["description"], "layer": exp["layer"], "index": exp["index"], "strength": exp.get("strength", 40)}
                    for exp in explanations
                ]
                st.sidebar.success("Explanations loaded successfully!")
            else:
                st.sidebar.warning("No explanations found.")
        except requests.exceptions.RequestException as e:
            st.sidebar.error(f"API request failed: {e}")
    else:
        st.sidebar.error("Query must be at least 3 characters long.")

# Feature Selection and Management
if st.session_state.available_descriptions:
    descriptions = [desc["description"] for desc in st.session_state.available_descriptions]
    selected_description = st.sidebar.selectbox("Select an explanation:", [""] + descriptions, key="description_select")

    if selected_description:
        feature = next(
            (desc for desc in st.session_state.available_descriptions if desc["description"] == selected_description),
            None,
        )
        if feature and feature not in st.session_state.selected_features:
            st.session_state.selected_features.append(feature)
            st.session_state.available_descriptions = []
            del st.session_state["description_select"]
            st.sidebar.success(f"Feature added: {selected_description}")

st.sidebar.markdown("### Selected Features")
if st.session_state.selected_features:
    for feature in st.session_state.selected_features:
        col1, col2 = st.sidebar.columns([4, 1])
        with col1:
            st.slider(
                feature["description"],
                min_value=-100,
                max_value=100,
                value=feature["strength"],
                key=f"strength_{feature['description']}",
            )
        with col2:
            if st.button("❌", key=f"remove_{feature['description']}"):
                st.session_state.selected_features.remove(feature)
else:
    st.sidebar.info("No features selected yet.")

# Chat Interface
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### Steered Chat")
    for message in st.session_state.steered_memory.chat_memory.messages:
        if isinstance(message, HumanMessage):
            st.markdown(f"**👤 User:** {message.content}")
        elif isinstance(message, AIMessage):
            st.markdown(f"**🤖 Steered Model:** {message.content}")

with col2:
    st.markdown("### Default Chat")
    for message in st.session_state.default_memory.chat_memory.messages:
        if isinstance(message, HumanMessage):
            st.markdown(f"**👤 User:** {message.content}")
        elif isinstance(message, AIMessage):
            st.markdown(f"**🤖 Default Model:** {message.content}")

# Fixed input at the bottom
st.markdown(
    """
    <style>
    .fixed-input {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        padding: 10px;
        background-color: white;
        border-top: 1px solid #ccc;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
user_input = st.text_input("Your Message:", key="user_input", placeholder="Type a message...", label_visibility="collapsed")
if st.button("Send 📨", key="send_button"):
    if user_input:
        features = [
            {"modelId": MODEL_ID, "layer": feature["layer"], "index": feature["index"], "strength": feature["strength"]}
            for feature in st.session_state.selected_features
        ]
        payload = {
            "defaultChatMessages": [{"role": "user", "content": user_input}],
            "steeredChatMessages": [{"role": "user", "content": user_input}],
            "modelId": MODEL_ID,
            "features": features,
        }
        try:
            response = requests.post(API_URL, json=payload, headers=HEADERS)
            response.raise_for_status()
            data = response.json()

            default_response = data.get("DEFAULT", {}).get("chat_template", [])[-1].get("content", "No response")
            steered_response = data.get("STEERED", {}).get("chat_template", [])[-1].get("content", "No response")

            st.session_state.default_memory.chat_memory.add_user_message(user_input)
            st.session_state.default_memory.chat_memory.add_ai_message(default_response)
            st.session_state.steered_memory.chat_memory.add_user_message(user_input)
            st.session_state.steered_memory.chat_memory.add_ai_message(steered_response)
        except requests.exceptions.RequestException as e:
            st.error(f"API request failed: {e}")
