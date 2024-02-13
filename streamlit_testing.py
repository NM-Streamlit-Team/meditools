import streamlit as st

### Add Password Prompting ###

st.set_page_config(page_title='MediTools', layout = 'centered', page_icon = ':stethoscope:', initial_sidebar_state = 'auto')
st.title("My AI Team")

home_tab, tool1_tab, tool2_tab = st.tabs(["Home", "Tool 1", "Tool 2"])

with home_tab:
    st.header("MediTools: Medical Education in the 21st Century")
    with st.expander("Please read before using"):
        st.write("This app contains a collection of prototype medical education tools, powered by LLMs and AI.")
        st.write("Authors: Remi Sampaleanu, Amr Alshatnawi, Dr. David Liebovitz")
with tool1_tab:
    st.header("First tool header")
with tool2_tab:
    st.header("Second tool header")

