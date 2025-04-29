import streamlit as st
import os
from screenshot import list_open_apps, screenshot_active_window

st.set_page_config(page_title="Digital Accessibility", layout="centered")

st.title("Digital Accessibility")

# Fetch open apps
apps = list_open_apps()

if not apps:
    st.error("Could not fetch open applications. Please ensure permissions are granted.")
else:
    # User selects an app
    selected_app = st.selectbox("Select an app to capture:", apps)

    if st.button("Capture Screenshot"):
        with st.spinner("Capturing screenshot..."):
            screenshot_path = screenshot_active_window(selected_app)
        
        if screenshot_path and os.path.exists(screenshot_path):
            st.success(f"Screenshot captured successfully!")
            st.image(screenshot_path, caption=f"Screenshot of {selected_app}", use_container_width=True)
            
            # Import speech_to_text only when the button is pressed
            from utils import speech_to_text, call_llm, text_to_speech
            
            # Add functionality to capture voice input
            st.write("Listening:")
            voice_input = speech_to_text()

            if voice_input:
                st.write(f"You said: {voice_input}")
                
                # Set the system and user prompt for LLM
                SYSTEM_PROMPT = "You are a helpful visual accessibility agent. Describe images clearly, concisely, and objectively in a sentence."
                USER_PROMPT = voice_input 
                
                # Call LLM with the image and user prompt
                result = call_llm(USER_PROMPT, screenshot_path, SYSTEM_PROMPT)
                
                if result:
                    st.write("LLM Response:")
                    st.success(f"{result}")
                    # Optionally, speak the LLM response
                    text_to_speech(result)
                else:
                    st.error("LLM did not provide a valid response.")
            else:
                st.error("Could not capture your voice input.")
        else:
            st.error("Failed to capture screenshot. Please try again.")
