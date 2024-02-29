import streamlit as st
from langchain.chains import LLMChain
from langchain.llms import openai
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.memory.chat_message_histories import StreamlitChatMessageHistory
from langchain.prompts import PromptTemplate 
from openai import OpenAI
from functions import *
from pathlib import Path

# set page icon and tab title
st.set_page_config(
        page_title="MediNews",
        page_icon="📰",
    )


# DEFINITIONS
spec_options = ["General Medical News", "Anesthesiology", "Cardiology", "Immunology", "Dermatology",
                "Emergency Medicine", "Colon and Rectal Surgery", "Family Medicine", "Forensic Pathology", "General Surgery", "Genetics", "Hospice/Paliative Care", 
                "Internal Medicine", "Neurology", "Obstetrics/Gynecology", "Ophthalmic Surgery", "Orthopaedic Surgery", "Otolaryngology", "Pathology",
                "Pediatrics", "Physical Medicine & Rehabilitation", "Preventative Medicine", "Psychiatry", "Radiology", "Rheumatology", "Sleep Medicine",
                "Thoracic Surgery", "Urology", "Vascular Surgery"]

# AUTHENTICATION CHECK
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
    
if not st.session_state['authenticated']:
    authenticate()
   
# IF AUTHENTICATION SUCCESS, CREATE PAGE: 
if st.session_state['authenticated']:
    
    with st.expander("⚠️ Important Notice on Usage"):
            st.write("""
    **Important Notice on Usage:** Please note that while our AI News Tool endeavors to provide accurate and up-to-date information, it relies on emerging technologies and retrieval methods that may be subject to errors. We make every effort to fact-check and verify news content, but accuracy cannot be guaranteed. Users are advised to conduct further research and fact-checking before making important decisions based on the information provided by this tool.
                
        Powered by OPENAI LLM Models    
                            """)
    specialization = st.multiselect("Please select your area of interest(s) (Max = 3)", spec_options, ["General Medical News"],max_selections=3)
    
    if not specialization:
        st.markdown("Please pick *AT LEAST ONE* area of interest from the dropdown menu.")
    else:
        st.write("Worked.")