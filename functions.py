import streamlit as st
import base64
import time

# function to remove first two words from a string
def remove_first_two_words(text: str) -> str:
    # Split the text into a list of words
    words = text.split()
    # Remove the first two words
    remaining_words = words[2:]
    # Rejoin the remaining words back into a string
    new_text = " ".join(remaining_words)

    return new_text

# function to autoplay audio 
def autoplay_audio(binary_content: bytes):
    # Encode the binary audio data to base64
    b64 = base64.b64encode(binary_content).decode()
    md = f"""
        <audio controls autoplay>
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        Your browser does not support the audio element.
        </audio>
        """
    st.markdown(md, unsafe_allow_html=True)


# function to authenticate user
def authenticate():
    # placeholders variables for UI 
    title_placeholder = st.empty()
    help_placeholder = st.empty()
    password_input_placeholder = st.empty()
    button_placeholder = st.empty()
    success_placeholder = st.empty()
    
    # check if not authenticated 
    if not st.session_state['authenticated']:
        # UI for authentication
        with title_placeholder:
            st.title("👋 Welcome to MediTools")
        with help_placeholder:
            with st.expander("**⚠️ Read if You Need Help With Password**"):
                st.write("To request or get an updated password contact developers.")
            
                st.write("""**Amr Alshatnawi**
             
                                    amralshatnawi@gmail.com
**Remi Sampaleanu**
             
             rsampale@outlook.com""")
            # UI and get get user password
            with password_input_placeholder:
                user_password = st.text_input("Enter the application password:", type="password", key="pwd_input")
            check_password = True if user_password == st.secrets["PASSWORD"] else False
            # Check user password and correct password
            with button_placeholder:
                if st.button("Authenticate") or user_password:
                    # If password is correct
                    if check_password:
                        st.session_state['authenticated'] = True
                        password_input_placeholder.empty()
                        button_placeholder.empty()
                        success_placeholder.success("Authentication Successful!")
                        st.balloons()
                        time.sleep(1)
                        success_placeholder.empty()
                        title_placeholder.empty()
                        help_placeholder.empty()
                    else:
                        st.error("❌ Incorrect Password. Please Try Agian.")

def clear_session_state_except_password():
    # Make a copy of the session_state keys
    keys = list(st.session_state.keys())
            
    # Iterate over the keys
    for key in keys:
        # If the key is not 'authenticated', delete it from the session_state
        if key != 'authenticated':
            del st.session_state[key]

def clear_session_state_except_password_doctor_name():
    # Make a copy of the session_state keys
    keys = list(st.session_state.keys())
            
    # Iterate over the keys
    for key in keys:
        # If the key is not 'authenticated & doctor_name & name', delete it from the session_state
        if key != 'authenticated' and key != 'Doctor_name' and key != 'first_name' and key != 'last_name':
            del st.session_state[key]
            
def divide_news_topics(parent_dict, limit):
    # Gather all news results from topics which actually have results
    # st.write(f"parent_dict: {parent_dict}")
    all_contents = {topic: details['news'] for topic, details in parent_dict.items() if 'news' in details}
    topics_with_content = {topic: contents for topic, contents in all_contents.items() if contents}
    num_topics = len(topics_with_content)
    # st.write(f"topics_with_content: {topics_with_content}")
    
    # If there are no topics, return an empty list
    if num_topics == 0:
        st.warning("NO RESULTS WERE FOUND FOR ANY OF THE SELECTED TOPICS")
        return []
    
    # Try to divide the content evenly, save remainder for later
    base_content_per_topic, extra_content = divmod(limit, num_topics)
    
    # Prepare the result list
    result_content = []
    
    # Distribute content
    for index, (topic, contents) in enumerate(topics_with_content.items()):
        # Determine how many contents to take for this topic
        num_contents_to_take = base_content_per_topic + (1 if index < extra_content else 0)
        
        # Add the content to the result list, respecting the topic's available content
        result_content.extend(contents[:num_contents_to_take])
    
    return result_content