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
from streamlit_tags import st_tags, st_tags_sidebar
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
spec_options = ["General Medicine", "Anesthesiology", "Cardiology", "Immunology", "Dermatology",
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
    **Important Notice on Usage:** Please note that while our AI News Tool endeavors to provide accurate and up-to-date information, 
    it relies on emerging technologies and retrieval methods that may be subject to errors. We make every effort to fact-check and verify news content, 
    but accuracy cannot be guaranteed. Users are advised to conduct further research and 
    fact-checking before making important decisions based on the information provided by this tool.   
                            """)
    
    # GET FILTERS / TUNING SETTINGS FROM USER
    specialization = st.multiselect("Please select your area of interest(s) (Max = 3)", spec_options, ["General Medicine"],max_selections=3,key="specialization")
    # Write instructions for the tool
    st.markdown("""
                ## Instructions:  
                  
                  
                1. Select your specializations or areas of interest from the dropdown menu above.
                2. Select your results timeframe (how recent do you want these articles and updates to be?) from the sidebar.
                3. Add any keywords you are interested in. These may boost the relevance of your results (e.g. "Treatment", "Diagnostic", etc.)
                4. Choose how many results you want to display. *Please note that this is the total number of results, and will be divided evenly amongst your chosen topics.*
                5. **Hit *GENERATE RESULTS*, and watch your personalized news get retrieved and summarized!**
                """)
    
    recency = st.sidebar.radio(
        "Please select the recency of the news: :calendar:",
        ["Less than 1 week","Less than 2 weeks","Less than 1 month","Any time"],
        index=0,
        key="recency"
    )
    
    keywords = st_tags_sidebar(
        label="Please select any keywords you wish to add to your query (*Optional*, Max = 5):",
        text="Press enter to add keyword",
        maxtags=5,
        key="keywords"
    )
    
    num_generated = st.sidebar.slider(
        "How many news articles/sources would you like to generate?",
        3,10,5,
        key="num_generated"
    )
    
    if not st.session_state['specialization']:
        st.markdown("Please pick *AT LEAST ONE* area of interest from the dropdown menu.")
    else: # we have valid filters, can proceed
        
        formatted_keywords = ""
        if keywords:
            # create the formatted keyword string to inject into query
            for idx, word in enumerate(keywords):
                if idx != len(keywords) - 1:
                    formatted_keywords += f'"{word}" | '
                else:
                    formatted_keywords += f'"{word}"'
            
            search_queries_spec = [(f'{topic} + {formatted_keywords} + advancements | updates | new developments | research', topic) for topic in specialization] # list of tuples containing query and that query's topic
        else:
            search_queries_spec = [(f'{topic} + advancements | updates | new developments | research', topic) for topic in specialization] # list of tuples containing query and that query's topic
        # st.write(f"CURRENT SEARCH QUERY: {search_queries_spec[0][0]}")    
        
        if st.button("GENERATE RESULTS"):
            try:
                with st.spinner("Your results are being generated..."):
                    result_dict = {} # Empty set to store results in
                    
                    # Get recency in proper format for argument
                    if recency == 'Less than 1 week':
                        recency_arg = 'qdr:w'
                    elif recency == 'Less than 2 weeks':
                        recency_arg = 'qdr:w2'
                    elif recency == 'Less than 1 month':
                        recency_arg = 'qdr:m'
                    elif recency == 'Any time': # actually last 5 years
                        recency_arg = 'qdr:y5'
                    
                    for query,topic in search_queries_spec:
                        search = GoogleSerperAPIWrapper(type="news",tbs=recency_arg,serper_api_key=SERPER_KEY)
                        topic_results = search.results(query)
                        
                        if topic not in result_dict:
                            result_dict[topic] = topic_results
                            
                    # OUTPUT MESSAGE IF VERY FEW RESULTS OF ONE TOPIC WAS GENERATED
                    lacking_topics = ""
                    for key,dict in result_dict.items():
                        if len(dict["news"]) < 3:
                            lacking_topics += (key + " ")
                            # st.write(len(dict["news"]))
                
                    # OUTPUT RESULTS           
                    if lacking_topics != "":
                        st.warning(f'PLEASE NOTE: Very few results were found for the following topics: {lacking_topics}',icon="⚠️")
                    result_list_dict = divide_news_topics(result_dict, num_generated)
                    # st.write(result_list_dict)
                    
                    for topic, contents_list in result_list_dict.items():
                        
                        # PUT DIVIDING TOPIC HEADERS
                        st.write(f"### {topic} Results:\n")
                        
                        for item in contents_list:
                            url_loader = UnstructuredURLLoader(urls=[item['link']])
                            data = url_loader.load() # load the webpage data

                            # Run the summarize chain (ON GPT-3.5-turbo)
                            llm = ChatOpenAI(temperature=0, model='gpt-3.5-turbo', openai_api_key=OPENAI_API_KEY)
                            chain = load_summarize_chain(llm, chain_type="map_reduce")
                            summary = chain.run(data)
                            
                            st.success(f"TITLE:  {item['title']}\n\nLINK:  {item['link']}\n\nSUMMARY:  {summary}")

            except Exception as e:
                st.exception(f"Exception: {e}")