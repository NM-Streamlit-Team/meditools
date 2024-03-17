import streamlit as st
from openai import OpenAI
from streamlit.logger import get_logger
### Add Password Prompting ###



st.set_page_config(page_title='MediTools', layout = 'centered', page_icon = ':stethoscope:', initial_sidebar_state = 'auto')
st.title("MediTools")

st.markdown("""<style>body {zoom: 1.5;  /* Adjust this value as needed */}</style>""", unsafe_allow_html=True)

#home_tab, tool1_tab, tool2_tab, chatGPT_tab = st.tabs(["Home", "Tool 1", "Tool 2", "ChatGPT Demo"])

# with home_tab:
st.header("MediTools: Medical Education in the 21st Century")
with st.expander("Please read before using"):
    st.write("This app contains a collection of prototype medical education tools, powered by LLMs and AI. All information provided by the tools herein is for training purposes only and should not be taken as pure fact.")
    st.write("Authors: Remi Sampaleanu, Amr Alshatnawi, Dr. David Liebovitz")
# with tool1_tab:
#     st.header("First tool header")
# with tool2_tab:
#     st.header("Second tool header")
    


