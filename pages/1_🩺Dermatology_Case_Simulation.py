import streamlit as st
import os
import random
from langchain.chains import LLMChain
from langchain.llms import openai
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.memory.chat_message_histories import StreamlitChatMessageHistory
from langchain.prompts import PromptTemplate
from functions import *
from prompts import *
from PIL import Image
from thefuzz import fuzz, process
from openai import OpenAI
from streamlit_mic_recorder import mic_recorder





st.set_page_config(
        page_title="Dermatology Patient Simulation",
        page_icon="🩺",
        # layout="wide" # Makes it too wide, would need to reformat things to fit in two columns perhaps
    )
# REMOVES WHITESPACE PADDING AT TOP AND BOTTOM, ADJUST AS NEEDED
# st.markdown("""      # THIS BREAKS THE CHATBOX AND COVERS CONTENT WITH THE INPUT WIDGET
#         <style>
#                .block-container {
#                     padding-top: 3rem;
#                     padding-bottom: 3rem;
#                     padding-left: 0rem;
#                     padding-right: 0rem;
#                 }
#         </style>
#         """, unsafe_allow_html=True)


st.markdown("""<style>body {zoom: 1.2;  /* Adjust this value as needed */}</style>""", unsafe_allow_html=True)

client = OpenAI()

# check if authenticated is in session state
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

# check if user is authenticated
if not st.session_state['authenticated']:
    authenticate()

# Show page if user is authenticated
if st.session_state['authenticated']:

    st.title("🩺Dermatology Case Simulation Tool")   

    # Get API key
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
    # Check if key was retrieved 
    if not OPENAI_API_KEY:
        raise ValueError("OpenAI API key is not set. Please set the OPENAI_API_KEY environment variable.")

    
    # # get doctor (user) name
    # if 'Doctor_name' not in st.session_state:
    #     name = st.text_input("Enter your name")
    #     st.session_state['Doctor_name'] = name
    # st.session_state['Doctor_name'] = False

    doctor_name_placholder = st.empty()
    col1, col2 = st.columns(2)
    if 'Doctor_name' not in st.session_state:
        #doctor_name_placholder = st.empty()
        with doctor_name_placholder:
            with col1:
                st.session_state['first_name'] = st.text_input("Enter your First Name:", placeholder="Example: Amr") 
            with col2:
                st.session_state['last_name'] = st.text_input("Enter your Last Name:", placeholder="Example: Alshatnawi") 

        

    ################################################## summary pdf ##################################################
            
    
    def generate_summary_with_llm(msgs):
        messages = []
        for msg in msgs.messages:
            messages.append({"content": msg.content})

        formatted_history = ""
        for mes in messages:
            message_content = mes["content"].replace("```Patient:```", "Patient:").replace("```Feedback:```", "\nFeedback:") 
            formatted_history += message_content + """\n\n"""

        #print(formatted_history)

        summary_template_formatted = summary_template.format(
                    condition = condition,
                    type = type,
                    formatted_history = formatted_history,
                )
        
        template = f"""Follow the given questions and provide complete answers: {summary_template_formatted}
        Use this chat history to provide feeback: {formatted_history}
        Answer: Provide answer here"""
        prompt  = PromptTemplate.from_template(template)


        # llm_report = OpenAI(openai_api_key = OPENAI_API_KEY, model="gpt-4")
        llm_report = LLMChain(llm = ChatOpenAI(openai_api_key = OPENAI_API_KEY, model = "gpt-4"), prompt=prompt)
        # llm_chain = LLMChain(prompt=prompt, llm=llm_report)
        results  = llm_report.run(summary_template_formatted)
        # print(results)



        markdown_summary = f"""
<style>
    h1 {{
        font-size: 60px; 
    }}
    h2 {{
        font-size: 45px; 
    }}
    p, li {{
        font-size: 35px; 
    }}
    
</style>

<div align="center">
    <h1>Dermatology Case Report &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<img src="data:image/jpeg;base64,{image_to_base64('./images/icons/report.png')}" alt="Alt text" style="width: 50px; height: 50px;"></h1>
</div>

------
<h2> <img src="data:image/jpeg;base64,{image_to_base64("./images/icons/medical_team.png")}" alt="Alt text" style="width: 40px; height: 40px;">&nbsp;&nbsp;Doctor: {st.session_state['first_name']} {st.session_state['last_name']}&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<img src="data:image/jpeg;base64,{image_to_base64("./images/icons/patient.png")}" alt="Alt text" style="width: 40px; height: 40px;">&nbsp;&nbsp;Patient: {st.session_state['patient_name']} </h2>

------

<h3>Condition: {condition} & Type: {type}</h3>
<h3><strong>
Information about the Condition and Performance Feedback:
</strong></h3>
<p>
{results}
</p>

-------

<h3>Transcript of case interaction:</h3>
<p>
- {formatted_history}
</p>
<img src="data:image/jpeg;base64,{image_to_base64("./images/head_report.png")}" alt="Alt text">
"""

        ############# Display summary ###############
        st.title("Dermatology Case Report 📄")
        st.header(f"🥼 Dr. {st.session_state['first_name']} {st.session_state['last_name']}  |  🤒 Patient: {st.session_state['patient_name']}")
        st.subheader(f"Condition & Type")
        st.markdown(f"The Patient has {condition}, more specifically  {type}")
        st.subheader("Information about the Condition and Performance Feedback")
        st.markdown(results)
        st.divider()
        st.subheader("Transcript of case interaction")
        st.markdown(formatted_history)
        st.image("./images/head_report.png")


        return markdown_summary


    ################################################## Function to get random image and condition ##################################################

    def get_random_image_info(base_path):
        conditions = os.listdir(base_path)
        chosen_condition = random.choice(conditions)
        condition_path = os.path.join(base_path, chosen_condition)

        types = os.listdir(condition_path)
        chosen_type = random.choice(types)
        type_path = os.path.join(condition_path, chosen_type)

        images = os.listdir(type_path)
        random_image = random.choice(images)
        image_path = os.path.join(type_path, random_image)

        return chosen_condition, chosen_type, image_path

    ################################################## sidebar options ##################################################

    # get derm image and save is st.session
    if 'image_info' not in st.session_state:
        base_path = './Derm_Images'
        st.session_state['image_info'] = get_random_image_info(base_path)

    # get image info 
    condition, type, image_path = st.session_state['image_info']

    # with st.sidebar.expander("FOR TESTING: See Condition and Type"): ## Comment out while published for testing
    #     st.write(f"{condition} / {type}")

    ################################################## Main code ##################################################

    def main():

        # speech client
        speech_client = OpenAI()

        # lab results 
        if 'lab_results' not in st.session_state:
                st.session_state['lab_results'] = None

        # Warning message and setup params while model not chosen:
        #st.sidebar.divider()
        model_version = st.sidebar.selectbox("Choose GPT Model", ["Please choose a model", "gpt-3.5-turbo", "gpt-4","gpt-4-turbo", "gpt-4o", "meta-llama/llama-3-8b-instruct", "meta-llama/llama-3-70b-instruct", "anthropic/claude-3-haiku"])
        feedback = st.sidebar.radio(
                    "Select feedback options:",
                    ("Feedback at the end", "Feedback after every question"))
            
        st.sidebar.divider()

        # Delete current case and create new one button
        if st.sidebar.button("Click to Delete Case & Create New One", use_container_width=True, on_click=clear_session_state_except_password_doctor_name):
            st.session_state["case_created"] = False

        # summary button invoke 
        # if st.sidebar.button('Generate Summary Report',use_container_width=True):
        #     st.session_state["case_created"] = False
        #     with st.spinner("Generating Report"):
        #         report_md = generate_summary_with_llm(st.session_state['message_history'])
        #         pdf = markdown_to_pdf(report_md)
        #         st.download_button(label="Download PDF",
        #                     data=pdf,
        #                     file_name="dermatology_case_report.pdf",
        #                     mime="application/pdf")

        # Show image at top of page, above the interaction window
        cond_img = Image.open(image_path)
        @st.experimental_dialog("Image condition", width="large")
        def show_dialog():
            st.image(cond_img)
            if st.button("Close"):
                st.rerun()

        # set up memory
        msgs = StreamlitChatMessageHistory(key = "langchain_messages_Derm")
        memory = ConversationBufferMemory(chat_memory=msgs)

        # provide an initial message
        if len(msgs.messages) == 0:
            
            ## ***********ADD PERSONALITY IMPLEMENTATION HERE, MAKE SURE IT IS ALSO STORED IN SESSION STATE SO REPEAT SCENARIO WORKS AS INTENDED******** ##
            
            ##                                                                                                                                           ##
            
            Patient_names = ["Alex", "Jordan", "Sam", "Robin", "Jamie", "Taylor", "Skyler", "Charile"]
            Patient_personalities = ["Extrovert", "Introvert", "Intuitive", "Sensor", "Thinker", "Feeler", "Judger", "Perceiver"]
            random_name = random.choice(Patient_names)
            random_personality = random.choice(Patient_personalities)
            if "patient_name" not in st.session_state:
                st.session_state['patient_name'] = random_name
            if "patient_personality" not in st.session_state:
                st.session_state['patient_personality'] = random_personality
            initial_msg = f"Hi Doctor {st.session_state['last_name']}! My name is {st.session_state['patient_name']}."
            msgs.add_ai_message(initial_msg)
            
            

        if feedback == "Feedback after every question":
            # template =  Patient_template_feedback
            template = Improved_template_feedback
        else:
            # template =  Patient_template
            template = Improved_template

        # format prompt to include derm condition and type
        doc_name = "Dr. " + st.session_state['last_name']
        formatted_Patient_template = template.format(name = st.session_state['patient_name'], personality = st.session_state['patient_personality'], condition = condition, type = type, doc_name = doc_name)
        # prompt the llm and send
        prompt = PromptTemplate(input_variables=["history", "human_input"], template= formatted_Patient_template)

        if model_version in ["meta-llama/llama-3-8b-instruct", "meta-llama/llama-3-70b-instruct", "anthropic/claude-3-haiku"]:
            llm_chain =LLMChain(llm= ChatOpenAI(base_url="https://openrouter.ai/api/v1", api_key=st.secrets["OpenRouter_API_Key"], model=model_version), prompt=prompt, memory=memory)
        else:
            llm_chain = LLMChain(llm=ChatOpenAI(openai_api_key = OPENAI_API_KEY, model = model_version), prompt=prompt, memory=memory)

        if model_version == "Please choose a model" and feedback is not None:
            st.info("Please choose a model and feedback option to proceed")
        else:

            st.session_state["model_feedback_expanded"] = False
            for msg in msgs.messages:
                st.chat_message(msg.type, avatar="🧑‍⚕️" if msg.type == "human" else "🤒").write(msg.content)
                
            # check if audio in session state 
            if 'audio' not in st.session_state:
                st.session_state['audio'] = None
            
            prompt = None

            # Allow users to enter text or record audio
            text_input = st.chat_input()
            if text_input:
                prompt = text_input
            elif st.session_state['audio'] is not None:
                # transcribe audio using audio bytes and openai client (check functions.py)
                prompt = transcribe_audio(st.session_state['audio']['bytes'], speech_client)
                st.session_state['audio'] = None
                
            
            if prompt:
                st.chat_message("Doctor", avatar="🧑‍⚕️").write(prompt)
                with st.spinner("Generating response..."):
                    response = llm_chain.run(prompt)
                st.session_state.last_response = response
                st.chat_message("Patient", avatar="🤒").write(response)
                prompt = None

                # Text to speech setup
                client = OpenAI()
                with st.spinner("Converting response to speech..."):
                    try:
                        speech = client.audio.speech.create(
                            model="tts-1-hd",
                            voice= "nova",
                            input=response
                        )
                        binary_content = speech.content
                        autoplay_audio(binary_content)
                    except Exception as e:
                        st.error(f"Failed to convert text to speech: {e} ")


            if st.session_state['lab_results'] is not None:
                msgs.add_message(st.session_state['lab_results'])
                st.session_state['lab_results'] = None
                st.rerun()
                
            # speech to text button (using a streamlit component)
            audio = mic_recorder(
            start_prompt="START SPEAKING 🎤",
            stop_prompt="STOP SPEAKING ⏹️",
            just_once=True,
            use_container_width=False,
            format="webm",
            callback=None,
            args=(),
            kwargs={},
            key=None
            )
            # check if audio has been recorded
            if audio:
                st.session_state['audio'] = audio
                audio = None
                st.rerun()

            col3, col4, col5 = st.columns(3)
            with col3:
                # display patient image in a dialog
                if st.button("SEE PATIENT IMAGE", use_container_width=True):
                    show_dialog()
            with col4:
                if st.button("ORDER LAB TEST", use_container_width=True):
                    lab_test()
            with col5:
                # Guess in a dialog pop up
                if st.button("READY TO DIAGNOSE",use_container_width=True, on_click=end_interact_callbck):
                    post_interact()

            
        st.session_state['message_history'] = msgs
        st.session_state['message_memory'] = memory
        
         
    ########################## End main ###########################
    if "remove_guess" not in st.session_state:
        st.session_state["remove_guess"] = False

    if "case_created" not in st.session_state:
        st.session_state["case_created"] = False
        
    if "end_interact" not in st.session_state:
        st.session_state["end_interact"] = False


    if (st.session_state["case_created"] == False) and (st.session_state["end_interact"] == False):
        case_button  = st.empty()
        with case_button:
            if st.button("👆 Click to Create a Case",use_container_width=True):
                st.session_state["case_created"] = True
                case_button.empty()
                doctor_name_placholder.empty()
                st.session_state['Doctor_name'] = True

    ########################################################## lab_test() ##########################################################
    
    @st.experimental_dialog("Order a lab test for the patient 🧪", width="large") 
    def lab_test():
        lab_test = st.text_input("Enter the name of teh lab test you want to order? (You can be descriptive if you wish)")

        if lab_test:
            with st.spinner("Preparing Lab Results 🧪"):
                # Format template
                formatted_lab_template = lab_prompt.format(lab_test = lab_test, condition = condition, type = type, patient_name = st.session_state['patient_name'])
                lab_order_prompt = PromptTemplate.from_template(formatted_lab_template)

                # setup an LLM 
                llm = ChatOpenAI(openai_api_key = OPENAI_API_KEY, model = "gpt-4")
                llm_Lab = lab_order_prompt | llm 
                # get lab results form LLM
                lab_results = llm_Lab.invoke(lab_test)


                st.session_state['lab_results'] = lab_results
            st.rerun()


    ########################################################## post_interact() ##########################################################
    
    @st.experimental_dialog("Guess the Diagnosis", width="large") 
    def post_interact():
        st.session_state["remove_guess_field"] = False
        #st.session_state["case_created"] = False # Shuts down main interaction panel, NOTE: ADD A WAY TO GO BACK
        if 'first_guess_made' not in st.session_state:
            user_guess = st.text_input(
                "What condition do you think your patient was exhibiting? :mag:",
                max_chars=50,
                key="user_guess",
                value=None,
                help="Try to be as specific as possible. For example, writing 'Rhinophyma' instead of simply 'Rosacea'.",
                disabled=st.session_state["remove_guess"]
            )
        else:
            user_guess = st.session_state['guess']
        # fuzzy string matching
        if st.button("Check Guess") or 'first_guess_made' in st.session_state:
        # if user_guess:
            st.session_state['first_guess_made'] = True
            st.session_state['guess'] = user_guess
            cond_type = condition + " " + type
            tok_set_ratio = fuzz.token_set_ratio(cond_type, user_guess)
            # st.write("THE FUZZ RATIO IS: ", tok_set_ratio) # Comment out later, also consider using a non fuzzy approach
            
            placeholder = st.empty()
            if tok_set_ratio >= 70: # Consider this a 'match'
                with placeholder.container():
                    st.markdown(f"""
                                ## Your Guess: :blue[{user_guess}]
                                
                                ## The Patient's Condition: :blue[{condition}], specifically :blue[{type}]
                                
                                # :green[Nice Work!]  \n
                                #
                                ### You can now repeat the same scenario, get feedback on your last interaction, or try a new case!
                                #
                                #
                                """)
            else:
                with placeholder.container():
                    st.markdown(f"""
                                ## Sorry! You guessed: :red[{user_guess}]
                                
                                ## The patient was really exhibiting :blue[{condition}], specifically :blue[{type}]
                                #
                                ### You can now repeat the same scenario, get feedback on your last interaction, or try a new case!
                                #
                                #
                                """)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("Repeat the Previous Scenario",use_container_width=True, on_click=guess_text_callbck):
                    clear_session_state_for_repeat()
                    st.rerun()
            with col2:
                if st.button("Generate Summary Report",use_container_width=True,on_click=guess_text_callbck):
                    st.session_state['feedback_after_guess'] = True
                    st.session_state["case_created"] = False
                    st.rerun()
            with col3:
                if st.button("Generate a New Case",use_container_width=True,on_click=guess_text_callbck):
                    clear_session_state_except_password_doctor_name()
                    st.rerun()
                
        
    ################### END post_interact() ################

    if st.session_state["case_created"]:   
        main()

    if 'feedback_after_guess' not in st.session_state:
        st.session_state['feedback_after_guess'] = False

    elif st.session_state['feedback_after_guess']:
        with st.spinner("Generating Report"): # SLOW - FIND WAY TO STORE IF ALREADY GENERATED
            report_md = generate_summary_with_llm(st.session_state['message_history'])
            pdf = markdown_to_pdf(report_md)
            st.download_button(label="Download PDF",
                        data=pdf,
                        file_name="dermatology_case_report.pdf",
                        mime="application/pdf")
            
            col_1, col_2 = st.columns(2)
            with col_1:
                st.button("Repeat the Previous Scenario",use_container_width=True, on_click=repeat_interact_callbck)
                    #clear_session_state_for_repeat()
                    #st.rerun()
            with col_2:
                st.button("Generate a New Case",use_container_width=True,on_click=master_reset_callbck)
                        #clear_session_state_except_password_doctor_name()
                        #st.rerun()
            

    st.sidebar.button("Reset Tool", use_container_width=True, on_click=clear_session_state_except_password)
        # st.rerun()