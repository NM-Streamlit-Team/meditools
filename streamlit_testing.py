import streamlit as st
from openai import OpenAI
from streamlit.logger import get_logger
### Add Password Prompting ###

st.set_page_config(page_title='MediTools', layout = 'centered', page_icon = ':stethoscope:', initial_sidebar_state = 'auto')
st.title("MediTools")

home_tab, tool1_tab, tool2_tab, chatGPT_tab = st.tabs(["Home", "Tool 1", "Tool 2", "ChatGPT Demo"])

with home_tab:
    st.header("MediTools: Medical Education in the 21st Century")
    with st.expander("Please read before using"):
        st.write("This app contains a collection of prototype medical education tools, powered by LLMs and AI. All information provided by the tools herein is for training purposes only and should not be taken as pure fact.")
        st.write("Authors: Remi Sampaleanu, Amr Alshatnawi, Dr. David Liebovitz")
with tool1_tab:
    st.header("First tool header")
with tool2_tab:
    st.header("Second tool header")    
with chatGPT_tab:
    st.header("OPENAI ChatGPT DEMO")

    # Read OpenAI API key
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

    # Check if key was retrieved 
    if not OPENAI_API_KEY:
        raise ValueError("OpenAI API key is not set. Please set the OPENAI_API_KEY environment variable.")
    # Initialize OpenAI client
    openai_client = OpenAI(api_key=OPENAI_API_KEY)

    #################################### Function to send a prompt to the GPT  ####################################
    def chat_with_gpt(prompt, model):
        # Create a streaming responsede
        stream = openai_client.chat.completions.create(
            model= model,
            messages=[{"role": "user", "content": prompt}],
            stream=True,
        )
        # Initialize the response variable
        response = ""  

        # Iterate over the streaming response
        for chunk in stream:
            response += chunk.choices[0].delta.content or ""
        return response.strip()
    
    #################################### End chat_with_gpt function ####################################

     # ChatGPT Warning
    with st.expander("⚠️ Important Notice on Usage"):
        st.write("""
    **Important Notice on Usage:** This AI-powered chat interface is designed to simulate natural human conversations and provide informative responses across a wide range of topics. However, please be advised that the responses generated by the AI are based on patterns in data and may not always be accurate or reflect the most current information. Users are encouraged to use critical judgment and verify facts independently, especially for important decisions. Remember, the AI does not possess consciousness or understanding; its responses are generated based on training data and algorithms. Enjoy your interaction responsibly.
    """)
    # Dropdown menu for model selection
    model_version = st.selectbox("Choose GPT Model", ["Please choose a Model First", "gpt-3.5-turbo", "gpt-4"])

    # Collect User input for ChatGPT
    user_input = st.text_input("You:", "")

    if st.button("Chat") or user_input:
        if user_input:
            with st.spinner(text="ChatGPT is writing...."):
                st.write("ChatGPT:", chat_with_gpt(user_input, model_version))
        else:
            st.write("Please enter something.")
################################################ END OF CHATGPT DEMO TAB CODE  #################################################

