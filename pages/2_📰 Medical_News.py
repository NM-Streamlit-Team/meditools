import streamlit as st
from langchain.chains import LLMChain
from langchain.llms import openai
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.memory.chat_message_histories import StreamlitChatMessageHistory
from langchain.prompts import PromptTemplate
from langchain.document_loaders import UnstructuredURLLoader
from langchain.chains.summarize import load_summarize_chain
from langchain.utilities import GoogleSerperAPIWrapper
from openai import OpenAI
from functions import *
from pathlib import Path
import os
import pprint


# set page icon and tab title
st.set_page_config(
        page_title="MediNews",
        page_icon="📰",
    )

# Make page content larger (zoom)
st.markdown("""<style>body {zoom: 1.5;  /* Adjust this value as needed */}</style>""", unsafe_allow_html=True)

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
    
# TRY LOADING REQUIRED KEYS
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
if not OPENAI_API_KEY:
    raise ValueError("OpenAI API key is not set. Please set the OPENAI_API_KEY environment variable.")

SERPER_KEY = st.secrets["SERPER_API_KEY"]
if not SERPER_KEY:
    raise ValueError("Serper API key is not set. Please set the SERPER_API_KEY environment variable.")
    
  
# IF AUTHENTICATION SUCCESS, CREATE PAGE: 
if st.session_state['authenticated']:
    
    with st.expander("⚠️ Important Notice on Usage"):
            st.write("""
    **Important Notice on Usage:** Please note that while our AI News Tool endeavors to provide accurate and up-to-date information, it relies on emerging technologies and retrieval methods that may be subject to errors. We make every effort to fact-check and verify news content, but accuracy cannot be guaranteed. Users are advised to conduct further research and fact-checking before making important decisions based on the information provided by this tool.
                
        Powered by OPENAI LLM Models    
                            """)
    
    # GET FILTERS / TUNING SETTINGS FROM USER
    specialization = st.multiselect("Please select your area of interest(s) (Max = 3)", spec_options, ["General Medical News"],max_selections=3,key="specialization")
    
    recency = st.sidebar.radio(
        "Please select the recency of the news: :calendar:",
        ["Less than 1 week","Less than 2 weeks","Less than 1 month","Any time"],
        index=0,
        key="recency"
    )
    
    num_generated = st.sidebar.slider(
        "How many news articles/sources would you like to generate?",
        3,10,5,
        key="num_generated"
    )
    
    if not st.session_state['specialization']:
        st.markdown("Please pick *AT LEAST ONE* area of interest from the dropdown menu.")
    else: # we have valid filters, can proceed
        
        search_queries_spec = [(f'advancements in {topic}', topic) for topic in specialization] # list of tuples containing query and that query's topic
        
        if st.button("GENERATE NEWS/UPDATES"):
            try:
                with st.spinner("Your results are being generated..."):
                    result_dict = {}
                    for query,topic in search_queries_spec:
                        search = GoogleSerperAPIWrapper(type="news",tbs="qdr:w3",serper_api_key=SERPER_KEY) # FIX DATE IN SEARCH TO MATCH BUTTON
                        topic_results = search.results(query)
                        if topic not in result_dict:
                            result_dict[topic] = topic_results
                        # ADD MESSAGE IF VERY FEW RESULTS OF ONE TOPIC WAS GENERATED
                st.write(result_dict)

            except Exception as e:
                st.exception(f"Exception: {e}")