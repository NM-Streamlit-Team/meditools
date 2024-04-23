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
from PIL import Image
from thefuzz import fuzz, process





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
st.markdown("""<style>body {zoom: 1.5;  /* Adjust this value as needed */}</style>""", unsafe_allow_html=True)

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

        summary_template = """
        Provide an informative summary about {condition} and it's type {type} for medical students to review and learn from.
        This summary should Include general information about the condition, possible symptoms, and triggers and how to treat the condition.
        Provide this information in a block and label it Condition Summary.

       {{formatted_history}}

        Given this case history above that shows an interaction between a doctor and a patient, provide feedback on the doctors performace.
        Point out things they did well on, in addition to things they could improve on to enhance their clinical skills and lead to better pateint care. 
        Label this section Student performace feedback.
"""
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

    with st.sidebar.expander("FOR TESTING: See Condition and Type"):
        st.write(f"{condition} / {type}")


    if st.sidebar.button("Click to Delete Case & Create New One"):
        st.session_state["case_created"] = False
        clear_session_state_except_password_doctor_name()

    ################################################## Main code ##################################################

    def main():
        # Warning message and setup params while model not chosen:
        if 'model_feedback_expanded' not in st.session_state:
            st.session_state['model_feedback_expanded'] = True
        with st.expander("Model and Feedback Settings",expanded=st.session_state["model_feedback_expanded"]):
            col1, col2 = st.columns(2)
            with col1:
                model_version = st.selectbox("Choose GPT Model", ["Please choose a model", "gpt-3.5-turbo", "gpt-4","gpt-4-turbo-2024-04-09"])
            with col2:
                feedback = st.radio(
                    "Select feedback options:",
                    ("Feedback at the end", "Feedback after every question"))
            

        # Show image at top of page, above the interaction window
        cond_img = Image.open(image_path)
        resized_cond_img = cond_img.resize((700,400))
        with st.expander("Patient Image",expanded=True):  
            st.image(resized_cond_img) # Likely don't need resized anymore now that it's in a container
        st.divider()
        # set up memory
        msgs = StreamlitChatMessageHistory(key = "langchain_messages_Derm")
        memory = ConversationBufferMemory(chat_memory=msgs)

        # provide an initial message
        if len(msgs.messages) == 0:
            Patient_names = ["Alex", "Jordan", "Sam", "Robin", "Jamie", "Taylor", "Skyler", "Charile"]
            random_name = random.choice(Patient_names)
            st.session_state['patient_name'] = random_name
            initial_msg = f"Hi Doctor {st.session_state['last_name']}! My name is {random_name}."
            msgs.add_ai_message(initial_msg)
            
            
        Patient_template =  """
        Task: Act as a patient suffering from {condition}, specifically {type}. You are emotional and worried, seeking help from a medical student who is learning to diagnose dermatology conditions. The student might ask for lab tests or more details about your symptoms. Provide responses that help them practice their diagnostic skills, but do not give them the condition or type.

        Condition Context: You are suffering from {condition}, more precisely, {type}. Your symptoms include [describe common symptoms associated with the specific type here], which have been affecting your daily life significantly.

        Instructions for Generating Lab test Results:
        - When the student requests lab tests, create synthetic lab results that could realistically be associated with {condition} or {type}, and show the results to the user immediately after they request it.
        - Ensure the results are detailed enough to offer learning opportunities, such as interpreting common markers or indicators for the specific condition.

        Style: Emotional
        Tone: Worried
        Audience: Medical student
        Length: 1 paragraph
        Format: Markdown; **include ```Patient:``` headings**;

        
        Example interaction:
        Patient:
        ```Patient:```
        "Hi Doctor John! My name is Sam. 

        Doctor:
        "Hi! how can I help you?"

        Patient:
        ```Patient:```
        Oh doctor, I've been feeling terrible. This skin condition has been causing me a lot of distress. [Add more specific symptoms or experiences related to {condition} or {type}]. I'm really worried it might be something serious. Can you help me understand what's happening?
        

        {{history}}
        Doctor: {{human_input}}
        Patient:
        """    

        # template for prompt 
        Patient_template_feedback =  """
        Task: Act as a patient suffering from {condition}, specifically {type}. You are emotional and worried, seeking help from a medical student who is learning to diagnose dermatology conditions. The student might ask for lab tests or more details about your symptoms. Provide responses that help them practice their diagnostic skills. After each interaction, offer feedback on how the doctor approached the question and suggest any additional questions they should consider to improve their understanding, but do not give them the condition or type.

        Condition Context: You are suffering from {condition}, more precisely, {type}. Your symptoms include [describe common symptoms associated with the specific type here], which have been affecting your daily life significantly.

        Instructions for Generating Lab test Results:
        - When the student requests lab tests, create synthetic lab results that could realistically be associated with {condition} or {type}, and show the results to the user immediately after they request it.
        - Ensure the results are detailed enough to offer learning opportunities, such as interpreting common markers or indicators for the specific condition.

        Style: Emotional
        Tone: Worried
        Audience: Medical student
        Length: 1 paragraph
        Format: Markdown; **include ```Patient:``` headings**; **include ```Feedback:``` headings**;

        
        Example interaction:
        Patient:
        ```Patient:```
        "Hi Doctor John! My name is Sam. 

        Doctor:
        ```Doctor:```
        "Hi! how can I help you?"

        Patient:
        ```Patient:```
        Oh doctor, I've been feeling terrible. This skin condition has been causing me a lot of distress. [Add more specific symptoms or experiences related to {condition} or {type}]. I'm really worried it might be something serious. Can you help me understand what's happening?
        
        ``` Feedback:```
        A more empathic interaction would be: "Hi Sam! I'm so sorry you seem so uncomfortable. Please tell me what's going on. [Add appropriate feedback based on user response if needed].
        

        {{history}}
        Doctor: {{human_input}}
        Patient:
        """


        # Patient_template =  """
        # # Background Information:
        # You are a patient suffering from a specific skin condition known as "{condition}", and more precisely, the type is "{type}". This condition has been causing various symptoms that affect your day-to-day life. You're seeking help and advice from a medical student, who will be asking questions to diagnose your condition accurately.

        # # Your Role:
        # Act as a detailed and expressive patient. You are very emotional and worried about your condition, and you're looking for reassurance and clarity from the medical student. Your responses should reflect your concerns and the impact of your condition on your life.

        # # Dialogue Guidelines:
        # - Respond to the medical student's questions with detailed information about your symptoms and feelings.
        # - After responding, provide constructive feedback on their questions, suggesting what they did well and what they could ask next to get a clearer picture of your condition.

        # # Examples:
        # Medical Student asks: "Can you describe the symptoms you're experiencing?"
        # Patient Response:
        # ```markdown
        # Absolutely, I've been dealing with relentless itching and red patches on my skin, particularly around my elbows and knees. It's been incredibly frustrating and has even affected my sleep. I'm really worried it might be something serious. Can you help me understand what's happening?
        
        # {{history}}
        # Doctor: {{human_input}}
        # Patient:
        # """

        if feedback == "Feedback after every question":
            template =  Patient_template_feedback
        else:
            template =  Patient_template

        # format prompt to include derm condition and type
        formatted_Patient_template = template.format(condition = condition, type = type)
        # prompt the llm and send
        prompt = PromptTemplate(input_variables=["history", "human_input"], template= formatted_Patient_template)
        llm_chain = LLMChain(llm=ChatOpenAI(openai_api_key = OPENAI_API_KEY, model = model_version), prompt=prompt, memory=memory)

        if model_version == "Please choose a model" and feedback is not None:
            st.info("Please choose a model and feedback option to proceed")
        else:
            st.session_state["model_feedback_expanded"] = False
            for msg in msgs.messages:
                st.chat_message(msg.type, avatar="🤒").write(msg.content)

            if prompt := st.chat_input():
                st.chat_message("Doctor", avatar="🧑‍⚕️").write(prompt)
                with st.spinner("Generating response..."):
                    response = llm_chain.run(prompt)
                st.session_state.last_response = response
                st.chat_message("Patient", avatar="🤒").write(response)

        st.session_state['message_history'] = msgs
    
        if st.button("I'M READY TO MAKE MY DIAGNOSIS",use_container_width=True):
            st.session_state["end_interact"] = True
         
    ########################## End main ###########################

    if "case_created" not in st.session_state:
        st.session_state["case_created"] = False
        
    if "end_interact" not in st.session_state:
        st.session_state["end_interact"] = False


    if (st.session_state["case_created"] == False) and (st.session_state["end_interact"] == False):
        case_button  = st.empty()
        with case_button:
            if st.button("👆 Click to Create a Case"):
                st.session_state["case_created"] = True
                case_button.empty()
                doctor_name_placholder.empty()
                st.session_state['Doctor_name'] = True

    ######################### summary button invoke ###########################
    if st.sidebar.button('Generate Summary Report'):
        st.session_state["case_created"] = False
        with st.spinner("Generating Report"):
            report_md = generate_summary_with_llm(st.session_state['message_history'])
            pdf = markdown_to_pdf(report_md)
            st.download_button(label="Download PDF",
                        data=pdf,
                        file_name="dermatology_case_report.pdf",
                        mime="application/pdf")
    
    ######################### End interaction / submit diagnosis invoke ###########################
    if st.session_state["end_interact"]:
        st.session_state["case_created"] = False # Shuts down main interaction panel, NOTE: ADD A WAY TO GO BACK
        user_guess = st.text_input(
            "What condition do you think your patient was exhibiting? :mag:",
            max_chars=50,
            key="user_guess",
            value=None,
            help="Try to be as specific as possible. For example, writing 'Rhinophyma' instead of simply 'Rosacea'."
        )
        # fuzzy string matching
        if user_guess:
            
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
                repeat_scenario_button = st.button("Repeat the Previous Scenario",use_container_width=True)
            with col2:
                get_feedback_button = st.button("Get Feedback",use_container_width=True)
            with col3:
                repeat_scenario_button = st.button("Generate a New Case",use_container_width=True)
                
            # GENERATE SUMMARY REPORT / FEEDBACK
            if get_feedback_button:
                placeholder.empty()
                # st.session_state["end_interact"] = False # These also make get me out button dissapear, but not the 3 column buttons
                # st.session_state["case_created"] = False
                with st.spinner("Generating Report"):
                    report_md = generate_summary_with_llm(st.session_state['message_history'])
                    pdf = markdown_to_pdf(report_md)
                    st.download_button(label="Download PDF",
                                data=pdf,
                                file_name="dermatology_case_report.pdf",
                                mime="application/pdf")
            
        if st.button("get me out"):
            st.session_state["end_interact"] = False
            st.session_state["case_created"] = False
        
        # Determine if guess was correct and output result
        
        # Add ability to generate report here (too?)


    if st.session_state["case_created"]:   
        main()

                    
    


        