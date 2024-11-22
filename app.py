# File: steer_chatbot.py

import streamlit as st
import requests
from langchain.memory import ConversationBufferMemory

# Initialize Conversation Memory
if "default_memory" not in st.session_state:
    st.session_state.default_memory = ConversationBufferMemory()
if "steered_memory" not in st.session_state:
    st.session_state.steered_memory = ConversationBufferMemory()

# API details
API_URL = "https://www.neuronpedia.org/api/steer-chat"
MODEL_ID = "gemma-2-9b-it"
HEADERS = {"Content-Type": "application/json"}

# Streamlit UI
st.title("Steer With SAE Features (Chat)")
st.sidebar.title("Settings")

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

        # API Call
        try:
            response = requests.post(API_URL, json=payload, headers=HEADERS)
            response.raise_for_status()
            data = response.json()

            # Debugging: Check the API response structure
            st.write("API Response:", data)

            # Extract responses safely
            default_response = data.get("defaultChatMessages", [{}])[0].get("content", "No response")
            steered_response = data.get("steeredChatMessages", [{}])[0].get("content", "No response")
            
            # Add user input to default memory
            st.session_state.default_memory.chat_memory.add_user_message(user_input)
            
            # Add default model response to default memory
            st.session_state.default_memory.chat_memory.add_ai_message(default_response)
            
            # Add user input to steered memory
            st.session_state.steered_memory.chat_memory.add_user_message(user_input)
            
            # Add steered model response to steered memory
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
        role = message.role  # 'user' or 'assistant'
        content = message.content
        if role == "user":
            st.markdown(f"**👤 User:** {content}")
        else:
            st.markdown(f"**🤖 Default Model:** {content}")

# Display Steered Model Chat
with col2:
    st.subheader("Steered Model Chat")
    for message in st.session_state.steered_memory.chat_memory.messages:
        role = message.role  # 'user' or 'assistant'
        content = message.content
        if role == "user":
            st.markdown(f"**👤 User:** {content}")
        else:
            st.markdown(f"**🤖 Steered Model:** {content}")

