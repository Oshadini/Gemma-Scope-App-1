# Display selected descriptions with sliders for strength adjustment and remove buttons
st.sidebar.markdown("### Selected Features")
if st.session_state.selected_features:
    # Create containers for each feature
    for i, feature in enumerate(st.session_state.selected_features[:]):  # Use a copy to iterate safely
        # Create a collapsible container for each feature
        with st.sidebar.container():
            # Display the slider for strength
            feature["strength"] = st.slider(
                f"Strength for '{feature['description']}'",
                min_value=-100,
                max_value=100,
                value=feature["strength"],
                key=f"strength_{feature['description']}",
            )
            # Add the remove button
            if st.button(f"Remove '{feature['description']}'", key=f"remove_{feature['description']}"):
                st.session_state.selected_features.pop(i)  # Remove the selected feature
                break  # Exit the loop to avoid index shifting issues
else:
    st.sidebar.markdown("No features selected yet.")

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
            "features": features,  # Pass the combined descriptions
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
