import streamlit as st
from openai import OpenAI
from streamlit.logger import get_logger
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, TemplateId, Personalization



st.set_page_config(page_title='MediTools', layout = 'centered', page_icon = ':stethoscope:', initial_sidebar_state = 'auto')
st.markdown("""<style>body {zoom: 1.5;  /* Adjust this value as needed */}</style>""", unsafe_allow_html=True)


video_path = "https://dl.dropboxusercontent.com/scl/fi/gy9w12c85ivtg9itbimg3/MediTools.mp4?rlkey=di01s1pmjzzhdzycqjzpbvpup&st=d4zfq6m8&dl=0"
# Embed the video with autoplay and loop
video_html = f'''
<style>
    .non-interactive-video {{
        width: 100%;  /* Responsive width */
        height: auto; /* Maintain aspect ratio */
        pointer-events: none;  /* Disables click interactions */
    }}
</style>
<video class="non-interactive-video" autoplay loop muted>
    <source src="{video_path}" type="video/mp4">
    Your browser does not support the video tag.
</video>
'''
st.markdown(video_html, unsafe_allow_html=True)



with st.expander("⚠️Please read before using"):
    st.write("This app contains a collection of prototype medical education tools, powered by LLMs and AI. All information provided by the tools herein is for training purposes only and should not be taken as pure fact.")
    st.write("Authors: Remi Sampaleanu, Amr Alshatnawi, Dr. David Liebovitz")

st.divider()

st.subheader("👋 Welcome to MediTools")

st.markdown("""
            At MediTools, we harness the power of cutting-edge language models to transform medical education.
            Our tools are designed to provide interactive learning experiences and up-to-date medical information,
            making it easier for medical professionals and students to enhance their knowledge and skills.
            Explore our innovative solutions:
            """)

st.markdown("""
            - **Dermatology Case Simulation Tool:** Dive into realistic dermatology case scenarios, improve diagnostic skills,
             and receive instant feedback. Engage with language models acting as patients, hone your diagnostic techniques,
             and get feedback on your clinical decisions.
            """)

st.markdown("""
            - **Medical Knowledge Tool:** Enhance your medical knowledge with our dual-feature tool designed to keep you at the forefront of medical advancements. This tool includes two separate tabs:
                - **AI-Enhanced PubMed: Query and Understand with LLMs:** Access a wealth of medical research papers from PubMed. Query available full-text papers with our large language models, allowing you to delve deeper into the research and better understand complex medical content.
                - **Google News Retrieval:** Stay updated with the latest in your medical specialization. Retrieve current news articles from Google News and get concise, LLM-generated summaries to quickly grasp the key points.

            Each feature is tailored to provide targeted information, ensuring that medical professionals and students have the latest and most relevant insights at their fingertips.
""")

st.markdown("Discover how MediTools can enhance your medical learning journey today!")

st.divider()

st.subheader('Meet the Team')
col1, col2, col3 = st.columns(3)
with col1:
    html = """
    <div style='text-align: center; width: 200px;'>
        <div style='border-radius: 50%; width: 200px; height: 200px; overflow: hidden;'>
            <img src='https://dl.dropboxusercontent.com/scl/fi/xmgkjrwb31nzpd9y8x5j1/Amr_pro_1.jpg?rlkey=aj71j2dobuolluuhtz5ffy1p1&st=shlfksny&dl=0' style='width: 100%; height: 100%; object-fit: cover;'>
        </div>
        <p style='margin: 10px 0 0; font-size: 18px;'>Amr Alshatnawi</p>
        <a href='https://www.linkedin.com/in/amralshatnawi/' target='_blank' style='font-size: 16px; color: blue; text-decoration: none;'>Connect on LinkedIn</a>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
with col2:
    html_1 = """
    <div style='text-align: center; width: 200px;'>
        <div style='border-radius: 50%; width: 200px; height: 200px; overflow: hidden;'>
            <img src='https://dl.dropboxusercontent.com/scl/fi/lawuhett4hsy3t9vcvm1i/remi_photo.jpg?rlkey=l7wvu4cvuj5s4wcegqex6mwox&st=wv9i8s5l&dl=0' style='width: 100%; height: 100%; object-fit: cover; object-position: center 10%;'>
        </div>
        <p style='margin: 10px 0 0; font-size: 18px;'>Remi Sampaleanu</p>
        <a href='https://www.linkedin.com/in/rsampale/' target='_blank' style='font-size: 16px; color: blue; text-decoration: none;'>Connect on LinkedIn</a>
    </div>
    """
    st.markdown(html_1, unsafe_allow_html=True)

with col3:
    html_2 = """
    <div style='text-align: center; width: 200px;'>
        <div style='border-radius: 50%; width: 200px; height: 200px; overflow: hidden;'>
            <img src='https://dl.dropboxusercontent.com/scl/fi/66fzp9rfzd7ptp5uepxgq/Dr.David.jpg?rlkey=v3tqkhuzotyy5gaee0wu1pnl9&st=pdudpmks&dl=0' style='width: 100%; height: 100%; object-fit: cover; object-position: center 10%;'>
        </div>
        <p style='margin: 10px 0 0; font-size: 18px;'>Dr. David Liebovitz</p>
        <a href='https://www.linkedin.com/in/liebovitz/' target='_blank' style='font-size: 16px; color: blue; text-decoration: none;'>Connect on LinkedIn</a>
    </div>
    """
    st.markdown(html_2, unsafe_allow_html=True)

st.divider()

sendgrid_api_key = st.secrets['sendgrid_API_Key']

# Email settings
def send_to_help_email(user_name, user_email, message):
    sg = SendGridAPIClient(sendgrid_api_key)

    formatted_message = message.replace('\n', '<br>')
    email_content = f"<strong>From:</strong> {user_name} &lt;{user_email}&gt;<br><strong>Message:</strong><br>{formatted_message}"
    email = Mail(
        from_email='no.reply.meditools@outlook.com',  # This should be a verified sender
        to_emails='help.meditools@outlook.com',
        subject=f'Feedback/Inquiry from {user_name}',
        html_content=email_content
    )
    email.reply_to = user_email  # Set reply-to to user's email

    response = sg.send(email)
    return response

def send_confirmation_email(user_email):
    sg = SendGridAPIClient(sendgrid_api_key)
    message = Mail(
        from_email='no.reply.meditools@outlook.com',
        to_emails=user_email,
    )

    message.template_id = TemplateId(st.secrets['sendgrid_template_ID'])

    # Add dynamic template data directly to the Mail object
    message.dynamic_template_data = {
        "feedback_received": "We have received your feedback"
    }
    response = sg.send(message)
    return response

st.subheader("📩 Contact US & Provide Feedback")

# Streamlit form for feedback

# Initialize session state
if 'form_submitted' not in st.session_state:
    st.session_state['form_submitted'] = False
    
form_placeholder = st.empty()
message_placeholder = st.empty()
with form_placeholder.form("feedback_form"):
    st.markdown("We are always happy to hear your feedback or suggestions. Please don't hesitate to contact us!")
    name = st.text_input("**Name**", placeholder="John Doe")
    email = st.text_input("**Email***", placeholder="JohnDoe@gmail.com")
    message = st.text_area("**Message***")
    st.markdown("***Required**")
    submitted = st.form_submit_button("Send")

    if submitted:
        if email == "" or message == "":
            message_placeholder.warning("Please enter your email and a message to send")
        else:
            response_help = send_to_help_email(name, email, message)
            if response_help.status_code == 202:
                response_user = send_confirmation_email(email)
                if response_user.status_code == 202:
                    form_placeholder.empty()
                    message_placeholder.success("Thank you for your feedback! A confirmation email has been sent to you.")
                else:
                    message_placeholder.error("Failed to send confirmation email.")
            else:
                message_placeholder.error("Failed to send your feedback. Please try again later.")