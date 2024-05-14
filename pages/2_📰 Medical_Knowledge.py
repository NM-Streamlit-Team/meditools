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
import requests
import xml.etree.ElementTree as ET
import datetime
from streamlit_pdf_viewer import pdf_viewer
import tempfile


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

    # define tabs
    tabs = ["AI-Enhanced PubMed 🤖", "Google News 📃"]
    tab = st.sidebar.selectbox("👆 Select tool", tabs)
    st.sidebar.divider()

    if tab == "Google News 📃":
        st.title('Google News Retrieval Tool')
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
                                llm = ChatOpenAI(temperature=0, model='gpt-4o', openai_api_key=OPENAI_API_KEY)
                                chain = load_summarize_chain(llm, chain_type="map_reduce")
                                summary = chain.run(data)
                                
                                st.success(f"TITLE:  {item['title']}\n\nLINK:  {item['link']}\n\nSUMMARY:  {summary}")

                except Exception as e:
                    st.exception(f"Exception: {e}")
    


    ############################################################################################# Research Paper Tab #############################################################################################

    elif tab == "AI-Enhanced PubMed 🤖":

        #################################### AI-Enhanced PubMed Functions ####################################

        # Get pubmed articles ids based on query
        def search_pubmed(query, max_results=5, mindate = '', maxdate = ''):
            base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
            params = {
                'db': 'pubmed',
                'term': query,
                'retmode': 'json',
                'retmax': max_results, 
                'mindate': mindate,
                'maxdate': maxdate,
                'usehistory': 'y'
            }
            response = requests.get(base_url, params=params)
            if response.status_code == 200:
                return response.json()['esearchresult']['idlist']
            else:
                return []
            

        # Fetch details about pubmed artciles using the IDs, including the abstracts
        def fetch_article_details_with_abstracts(pmids):
            base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
            params = {
                'db': 'pubmed',
                'id': ','.join(pmids),
                'retmode': 'xml'
            }
            response = requests.get(base_url, params=params)
            if response.status_code == 200:
                return response.text
            else:
                return None
            

        # Parse the fetched data to extract abstract and metadata
        def parse_article_details(xml_data):
            """Parse XML data from efetch to extract details including abstracts and other metadata."""
            root = ET.fromstring(xml_data)
            articles = {}
            for article in root.findall('.//PubmedArticle'):
                pmid = article.find('.//PMID').text
                title = article.find('.//ArticleTitle').text
                abstract = article.find('.//Abstract/AbstractText')
                abstract_text = abstract.text if abstract is not None else "No abstract available"
                authors = [author.find('LastName').text + " " + author.find('ForeName').text 
                        for author in article.findall('.//Author') if author.find('LastName') is not None and author.find('ForeName') is not None]
                pubdate = article.find('.//PubDate/Year').text if article.find('.//PubDate/Year') is not None else "Not available"
                journal = article.find('.//Journal/Title').text if article.find('.//Journal/Title') is not None else "Not available"

                # Look for PMCID
                article_id_list = article.find('.//ArticleIdList')
                pmcid = None
                if article_id_list is not None:
                    for article_id in article_id_list.findall('.//ArticleId'):
                        if article_id.get('IdType') == 'pmc':
                            pmcid = article_id.text

                full_text_link = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmcid}/" if pmcid else None

                articles[pmid] = {
                    'title': title,
                    'abstract': abstract_text,
                    'authors': authors,
                    'pubdate': pubdate,
                    'journal': journal,
                    'pmcid': pmcid,
                    'full_text_link': full_text_link
                }
            return articles
        

        # Extract article text using diffbot
        def extract_text_article(pmcid):
            api_endpoint = "https://api.diffbot.com/v3/article"
            params = {
                'token': st.secrets['DiffBot_API_Key'],
                'url': f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmcid}/"
            }
            response = requests.get(api_endpoint, params=params)
            data = response.json()
            
            if response.status_code == 200:
                return data['objects'][0]  
            else:
                return f"Error: {data['error']}"
            
        
        # Display the artcile details and setup for LLM
        def display_articles(articles):

            # Dictionary to hold placeholders for each article
            placeholders = {}  

            for pmid, article in articles.items():
                # Create a dictionary for each article's placeholders
                placeholders[pmid] = {
                    'title': st.empty(),
                    'pmid': st.empty(),
                    'authors': st.empty(),
                    'date': st.empty(),
                    'journal': st.empty(),
                    'pubmed_url': st.empty(),
                    'abstract': st.empty(),
                    'text_link': st.empty(),
                    'PMCID': st.empty(),
                    'button': st.empty(),
                    'line': st.empty()
                }

                # Display article metadata
                placeholders[pmid]['title'].subheader(article['title'])
                placeholders[pmid]['pmid'].write(f"**PMID:** {pmid}")
                placeholders[pmid]['authors'].write(f"**Authors:** {', '.join(article['authors'])}")
                placeholders[pmid]['date'].write(f"**Published Date:** {article['pubdate']}")
                placeholders[pmid]['journal'].write(f"**Journal:** {article['journal']}")
                pubmed_url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
                placeholders[pmid]['pubmed_url'].markdown(f"**PubMed:** [View on PubMed]({pubmed_url})")
                placeholders[pmid]['abstract'].write(f"**Abstract:** {article['abstract']}")

                # Check if the article is on pubmed central
                if article['pmcid']:
                    placeholders[pmid]['text_link'].markdown(f"**Full Text:** [Access on PMC]({article['full_text_link']})")
                    # Button to setup for LLM
                    if placeholders[pmid]['button'].button("select this paper to query with LLM", key=pmid):
                        with st.spinner("🤖 Getting the LLM ready for you"):
                            # Extract selected paper text 
                            full_text = extract_text_article(article['pmcid'])
                            st.session_state['full_article_text'] = full_text['text']
                            pubmed_query.empty()
                            pubmed_title.empty()
                            search_button.empty()
                            pubmed_expander.empty()
                            st.session_state['selected_pmid'] = pmid
                            st.session_state['selected_article'] = article
                            st.session_state['LLM_Invoked'] = True
                            st.subheader(f"Selected Article for LLM Query: {st.session_state['selected_article']['title']}")
                            st.rerun()

                # Line (UI) 
                placeholders[pmid]['line'].markdown("---")

                # Remove the articles if the user selects one 
                if 'selected_pmid' in st.session_state:
                    for article_pmid in placeholders:
                        for key in placeholders[article_pmid]:
                            placeholders[article_pmid][key].empty()    


        # Setup LLM for user Interaction
        def LLM_interaction():

            # Rest tool button 
            if st.sidebar.button("Reset Tool"):
                clear_session_state_except_password()
                st.rerun()

            else:
                
                # Get selected paper metadata 
                pmcid = st.session_state['selected_article']['pmcid']
                title = st.session_state['selected_article']['title']
                authors = st.session_state['selected_article']['authors']
                journal = st.session_state['selected_article']['journal']

                st.subheader(f"Selected Article for LLM Query: {title}")
                # Select LLM
                st.session_state['model_version_knowledge'] = st.selectbox("Choose GPT Model", ["Please choose a model", "meta-llama/llama-3-8b-instruct", "meta-llama/llama-3-70b-instruct", "anthropic/claude-3-haiku"])
                
                # more sidebar options to provide pdf and article links
                st.sidebar.divider()
                st.sidebar.markdown(f"**PDF** - [Link](https://www.ncbi.nlm.nih.gov/pmc/articles/{pmcid}/pdf/)")
                st.sidebar.markdown(f"**Full Text on PMC** - [Link](https://www.ncbi.nlm.nih.gov/pmc/articles/{pmcid}/)")

                
                # Template for prompt
                pubmed_template = """ 
                Task: Act as a research literature mentor, guiding users through the complexities of medical research papers. The assistant should provide insightful analyses, summarize key findings, and answer specific questions to help users grasp the intricate details and broader implications of the studies.
                Topic: Engage in a detailed discussion of research methodologies, results, implications, and relevance to current medical practices or further research, based on the user's queries. The assistant should adeptly translate scientific jargon into easily understandable language.
                Style: Detailed, analytical, and educational, ensuring the explanations are comprehensive yet accessible.
                Tone: Professional, friendly, and encouraging, fostering an environment conducive to learning and inquiry.
                Audience: Users ranging from medical professionals to students and others interested in medical research.
                Length: 1-3 paragraphs per response
                Format: markdown; **include ```AI Response``` headings**

                Here is the content of the paper you need to answer questions about:
                Title: {title}
                Authors: {authors}
                Jorunal: {journal}
                Full text: {full_article_text}


                Example interaction:

                User: Could you summarize the methodology and key findings of the study on new migraine treatments I found in the article?
                AI:
                ```AI Response:```
                The study utilized a double-blind, placebo-controlled trial to evaluate the efficacy of the new migraine treatment over a period of six months. Participants were randomly assigned to receive either the new medication or a placebo, with neither the participants nor the researchers knowing who received the actual medication. This method helps eliminate bias and increases the reliability of the results.

                Key findings indicate that the treatment group experienced a significant reduction in the frequency and severity of migraine attacks compared to the placebo group. The researchers concluded that the medication could be an effective option for reducing migraine symptoms in adults. These results are promising, suggesting potential changes in therapeutic approaches for migraine sufferers.

                {{history}}
                User: {{human_input}}
                AI: 
                """
                # format prompt to include input variables
                formatted_pubmed_template = pubmed_template.format(title = title, authors = authors, journal = journal, full_article_text = st.session_state['full_article_text'])
                
                # set up memory
                msgs = StreamlitChatMessageHistory(key = "langchain_messages_pubmed")
                memory = ConversationBufferMemory(chat_memory=msgs)
                
                initial_msg = f"Hi! Ask me anything about {st.session_state['selected_article']['title']}. I'm ready to help!"
                if len(msgs.messages) == 0:
                    msgs.add_ai_message(initial_msg)

                prompt = PromptTemplate(input_variables=["history", "human_input"], template= formatted_pubmed_template)

                # LLM chain with an OpenRouter base for the models
                llm_chain =LLMChain(llm= ChatOpenAI(base_url="https://openrouter.ai/api/v1", api_key=st.secrets["OpenRouter_API_Key"], model=st.session_state['model_version_knowledge']), prompt=prompt, memory=memory)
                
                
                if st.session_state['model_version_knowledge'] == "Please choose a model":
                    st.info("Please choose a model to proceed")
                else:
                    for msg in msgs.messages:
                        st.chat_message(msg.type).write(msg.content)
                    if prompt := st.chat_input():
                        st.chat_message("User").write(prompt)
                        with st.spinner("Generating response..."):
                            response = llm_chain.run(prompt)
                        st.session_state.last_response = response
                        st.chat_message("AI").write(response)
            
        #################################### AI-Enhanced PubMed tab Streamlit interface ####################################

        if 'LLM_Invoked' not in st.session_state:
    
            # Empty placeholders
            pubmed_title = st.empty()
            pubmed_expander = st.empty()
            pubmed_query = st.empty()
            search_button = st.empty() 


            pubmed_title.title('AI-Enhanced PubMed: Query and Understand with LLMs')

            with pubmed_expander.expander("⚠️ Important Notice on Usage"):
                    st.write("""
            **Important Notice on Usage:** Please be aware that while our PubMed Retrieval Tool strives to provide accurate and
            comprehensive information, it depends on emerging technologies and data extraction methods that
            may be subject to inaccuracies. We diligently work to confirm and validate the content retrieved,
            but complete accuracy of the information cannot be guaranteed. Users are encouraged to conduct additional research
            and verification before making critical decisions based on the information provided by this tool.
                            """)

            # Tool parameters 
            date_today = datetime.date.today()
            default_min_date = datetime.date(year=2015, month=1, day=1)
            query = pubmed_query.text_input("Enter your search term:", "")
            max_results = st.sidebar.number_input("Number of results:", min_value=1, max_value=100, value=10)
            min_date = st.sidebar.date_input("Select minimum date:", default_min_date)
            max_date = st.sidebar.date_input("Select maximum date:", date_today)

            # Rest tool button 
            if st.sidebar.button("Reset Tool"):
                clear_session_state_except_password()
                st.rerun()

            if search_button.button("Search"):
                st.session_state['pubmed_search_button'] = True

            if 'pubmed_search_button' in st.session_state:
                if query == "":
                    st.warning("Please enter a query in the search bar")
                else:
                    with st.spinner("Generating results🔎"):
                        pmids = search_pubmed(query, max_results, min_date, max_date)
                        if pmids:
                            xml_data = fetch_article_details_with_abstracts(pmids)
                            if xml_data:
                                articles = parse_article_details(xml_data)
                                display_articles(articles)
                            else:
                                st.write("Failed to fetch article details.")
                        else:
                            st.write("No articles found.")

        else:
            LLM_interaction()