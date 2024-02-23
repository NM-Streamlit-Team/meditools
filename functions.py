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