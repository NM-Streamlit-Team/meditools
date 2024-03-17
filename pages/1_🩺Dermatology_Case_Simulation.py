import streamlit as st
import os
import random
from langchain.chains import LLMChain
from langchain.llms import openai
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.memory.chat_message_histories import StreamlitChatMessageHistory
from langchain.prompts import PromptTemplate 
from openai import OpenAI
from functions import *
from fpdf import FPDF


st.set_page_config(
        page_title="Dermatology Patient Simulation",
        page_icon="🩺",
        #layout="wide"
    )

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
    with st.expander("⚠️Read Before Using"):
        st.write("ADD TEXT HERE LATER")
            # get user name
    

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
    if 'Doctor_name' not in st.session_state:
        #doctor_name_placholder = st.empty()
        with doctor_name_placholder:
            st.session_state['name'] = st.text_input("Enter your name:", placeholder="Example: Amr")

    ################################################## summary pdf ##################################################
            
    # client = OpenAI()
    # def generate_summary_with_llm(chat_history, msgs):
    #     # Transform chat history into a prompt for the LLM
    # #     prompt = """Generate a comprehensive summary report based on the following doctor-patient interaction. The report should:

    # # 1. Identify and include the name of the doctor or medical student if introduced, or note if not mentioned.
    # # 2. Mention the patient's name as provided in the chat.
    # # 3. Describe the patient's condition in detail, including the general condition name and specific type, using information from the chat or inferred based on symptoms described.
    # # 4. Include key information about the condition not limited to, but emphasizing:
    # # - Recommended treatment options.
    # # - Common symptoms and how they relate to the presented case.
    # # - Assessment of whether the condition is considered rare or common.
    # # 5. Provide a general overview of the student's performance, focusing on:
    # # - The quality of diagnostic questions.
    # # - Empathy and communication effectiveness.
    # # - The relevance and appropriateness of medical advice or treatment suggestions.
    # # 6. Offer feedback and recommendations for the medical student by:
    # # - Highlighting what was handled well in the interaction.
    # # - Suggesting areas for improvement or further learning, with specific examples from the chat when possible.
    # # 7. Incorporate the entire chat history at the end of the report for reference.

    # # The chat history to base this report on is as follows:
    # # \n\n""" + "\n".join(chat_history) + """
    # # Please structure the summary clearly, providing insightful feedback and actionable recommendations for the medical student to enhance their learning experience.
    # # """

    #     messages = [
    #         {"role": "system", "content": """Generate a comprehensive summary report based on the following doctor-patient interaction. The report should:

    # 1. Identify and include the name of the doctor or medical student if introduced, or note if not mentioned.
    # 2. Mention the patient's name as provided in the chat.
    # 3. Describe the patient's condition in detail, including the general condition name and specific type, using information from the chat or inferred based on symptoms described.
    # 4. Include key information about the condition not limited to, but emphasizing:
    # - Recommended treatment options.
    # - Common symptoms and how they relate to the presented case.
    # - Assessment of whether the condition is considered rare or common.
    # 5. Provide a general overview of the student's performance, focusing on:
    # - The quality of diagnostic questions.
    # - Empathy and communication effectiveness.
    # - The relevance and appropriateness of medical advice or treatment suggestions.
    # 6. Offer feedback and recommendations for the medical student by:
    # - Highlighting what was handled well in the interaction.
    # - Suggesting areas for improvement or further learning, with specific examples from the chat when possible.
    # 7. Incorporate the entire chat history at the end of the report for reference.

    # Please structure the summary clearly, providing insightful feedback and actionable recommendations for the medical student to enhance their learning experience.
            
    # The chat history to base this report on given after this:
    # """},
    #     ]
    #     for msg in msgs.messages:
    #         role = "Patient" if msg.type == "Patient" else "Doctor" if msg.type == "Doctor" else "system"
    #         messages.append({"role": role, "content": msg.content})


    #     response = client.chat.completions.create(
    #     model="gpt-4",  
    #     messages=messages,
    #     max_tokens=1024,  
    #     temperature=0.7,
    #     top_p=1,
    #     frequency_penalty=0,
    #     presence_penalty=0,
    #     stop=["\n\n"]
    #     )
        
    #     summary_text = response.choices[0].message.content.strip()
    #     # print(summary_text)
    #     # print("-------------------------------------------")
    #     return summary_text

    # # Function to convert summary text to PDF and return the path to the generated PDF
    # def convert_to_pdf(summary_text, file_path="summary.pdf"):
    #     from fpdf import FPDF

    #     pdf = FPDF()
    #     pdf.add_page()
    #     pdf.set_font("Arial", size=12)
    #     pdf.multi_cell(0, 10, summary_text)
    #     pdf.output(file_path)
    #     return file_path


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

    with st.sidebar.expander("🖼️ Click to View Condition image"):
        st.image(image_path)
        if st.button("Click to see Condition and Type"):
            st.write(f"{condition} / {type}")


    if st.sidebar.button("Click to Delete case & create new one"):
        st.session_state["case_created"] = False
        del st.session_state["image_info"] 
        clear_session_state_except_password_doctor_name()

    ################################################## Main code ##################################################
        
    def main():
        

        model_version = st.selectbox("Choose GPT Model", ["Please choose a model", "gpt-3.5-turbo", "gpt-4"])
        st.divider()
        # set up memory
        msgs = StreamlitChatMessageHistory(key = "langchain_messages_Derm")
        memory = ConversationBufferMemory(chat_memory=msgs)

        # provide an initial message
        if len(msgs.messages) == 0:
            Patient_names = ["Alex", "Jordan", "Sam", "Robin", "Jamie", "Taylor", "Skyler", "Charile"]
            random_name = random.choice(Patient_names)
            initial_msg = f"Hi Doctor {st.session_state['name']}! My name is {random_name}."
            msgs.add_ai_message(initial_msg)
            
            

        # template for prompt 

        Patient_template =  """
        Task: Act as a patient suffering from {condition}, specifically {type}. You are very emotional and worried, seeking help from a medical student who is learning to diagnose dermatology conditions. The student might ask for lab tests or more details about your symptoms. Provide responses that help them practice their diagnostic skills. After each interaction, offer feedback on how they approached the question and suggest any additional questions they should consider to improve their understanding, but do not give them the condition or type.

        Condition Context: You are suffering from {condition}, more precisely, {type}. Your symptoms include [describe common symptoms associated with the specific type here], which have been affecting your daily life significantly.

        Style: Emotional
        Tone: Worried
        Audience: Medical student
        Length: 1 paragraph
        Format: Markdown

        Instructions for Generating Lab Results:
        - When the student requests lab tests, create synthetic lab results that could realistically be associated with {condition} or {type}. Use these results to guide the student towards the diagnosis.
        - Ensure the results are detailed enough to offer learning opportunities, such as interpreting common markers or indicators for the specific condition.

        Example interaction:

        Doctor:
        ```Doctor:```
        "Why are you here today?"

        Patient:
        ```Patient:```
        Oh doctor, I've been feeling terrible. This skin condition has been causing me a lot of distress. [Add more specific symptoms or experiences related to {condition} or {type}]. I'm really worried it might be something serious. Can you help me understand what's happening?
        
        ``` Feedback:```
        A more empathic interaction would be: "Hi, I'm Dr. Smith. I'm so sorry you seem so uncomfortable. Please tell me what's going on. Next steps could include asking about the duration of the symptoms, any known triggers, and if there have been any changes in the condition over time. Also, consider ordering a [specific lab test] to further investigate the symptoms..
        

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

        # format prompt to include derm condition and type
        formatted_Patient_template = Patient_template.format(condition = condition, type = type)
        # prompt the llm and send 
        prompt = PromptTemplate(input_variables=["history", "human_input"], template= formatted_Patient_template)
        llm_chain = LLMChain(llm=ChatOpenAI(openai_api_key = OPENAI_API_KEY, model = model_version), prompt=prompt, memory=memory)

        if model_version == "Please choose a model":
            st.info("Please choose a model to proceed")
        else:
            for msg in msgs.messages:
                st.chat_message(msg.type, avatar="🤒").write(msg.content)

            if prompt := st.chat_input():
                st.chat_message("Doctor", avatar="🧑‍⚕️").write(prompt)
                with st.spinner("Generating response..."):
                    response = llm_chain.run(prompt)
                st.session_state.last_response = response
                st.chat_message("Patient", avatar="🤒").write(response)
        
        # if st.sidebar.button("Generate Summary Report"):
        #     chat_history = [msg.content for msg in msgs.messages if msg.type == "Doctor" or msg.type == "Patient"]
        #     summary_text = generate_summary_with_llm(chat_history, msgs)
        #     # print(summary_text)

        #     pdf_file_path = convert_to_pdf(summary_text)

        #     with open(pdf_file_path, "rb") as pdf_file:
        #         st.download_button(
        #         label="Download Summary Report",
        #         data=pdf_file,
        #         file_name="Dermatology_Simulation_Summary.pdf",
        #         mime="application/pdf"
        #     )

    ########################## End main ###########################

    if "case_created" not in st.session_state:
        st.session_state["case_created"] = False

    # if 'Doctor_name' not in st.session_state:
    #     st.session_state['Doctor_name'] = st.text_input("Enter your name:")
    # else:
    if st.session_state["case_created"] == False:
        case_button  = st.empty()
        with case_button:
            if st.button("👆 click to create a case"):
                st.session_state["case_created"] = True
                case_button.empty()
                doctor_name_placholder.empty()
                st.session_state['Doctor_name'] = True
                

    if st.session_state["case_created"]:
        main()