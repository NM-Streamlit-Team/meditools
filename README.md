<h1 align="center">🩺🤖 MediTools - Medical Education Powered by LLMs</h1>

<p align="center" style="font-size: 1.2em;">
✨ Meditools provides interactive learning experiences and up-to-date medical information, helping medical professionals and students enhance their knowledge and skills.
</p>

<hr style="width: 60%; margin: auto;">

<p align="center">
  <img src="https://img.shields.io/badge/Powered%20by-LLMs-maroon?style=for-the-badge&logo=OpenAI&logoColor=white" alt="Powered by LLMs"/>
  <img src="https://img.shields.io/badge/Python-3.10.12-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python Version"/>
  <img src="https://img.shields.io/github/stars/NM-Streamlit-Team/meditools?style=for-the-badge&color=gold&logo=github&logoColor=white" alt="GitHub Stars"/>
  <img src="https://img.shields.io/github/last-commit/NM-Streamlit-Team/meditools?style=for-the-badge&color=pink&logo=git&logoColor=white" alt="Last Commit"/>
  <img src="https://img.shields.io/github/issues/NM-Streamlit-Team/meditools?style=for-the-badge&color=tan&logo=github&logoColor=white" alt="GitHub Issues"/>
  <img src="https://img.shields.io/github/contributors/NM-Streamlit-Team/meditools?style=for-the-badge&color=salmon&logo=github&logoColor=white" alt="GitHub Contributors"/>
</p>

<p align="center">
  <a href="https://www.dropbox.com/scl/fi/5tee7568ret1gvvuqedo7/MediTools-Ad.mp4?rlkey=bbofnzvaqdue2tkup47dd4sex&st=i536xucw&dl=0">
    <img src="https://www.dropbox.com/scl/fi/6johpso2rpzmrxc6e85ow/play_readme.png?rlkey=7f2jmr9ratwoo8euiuqh28qt2&st=d42n2vvz&raw=1" alt="Watch MediTools Promo Video" width="600"/>
  </a>
</p>

<br/>



## 🛠 Tools Available

### 1. Dermatology Case Simulation Tool
- Interactive AI-driven dermatological case scenarios
- Provides realistic clinical decision-making experiences
- Supports learning through simulated patient interactions

### 2. Medical Knowledge Tool
#### A. AI-Enhanced PubMed Search
- Advanced medical literature querying
- Intelligent summarization of research papers
- Contextual understanding of medical research

#### B. Google News Retrieval
- Real-time medical news aggregation
- AI-powered insights and summaries
- Stay updated with the latest medical developments

## 🌐 Access

- 💻 **Web Application**: [meditools.streamlit.app](https://meditools.streamlit.app/)
- 📄 **Research Paper**: [ Published on arXiv](https://doi.org/10.48550/arXiv.2503.22769)

## 🚀 Project Background

This project was developed as part of a Master's Capstone Research Project at The University of Chicago, exploring the intersection of artificial intelligence and medical education. Our comprehensive approach integrates multiple LLM technologies to create a unique learning platform.

## 🔧 Setup and Installation

### Option 1: Direct Access to Deployed Web App (Recommended for Non-Technical Users)
If you're interested in using the application without setting up your own environment:
- **Visit**: [meditools.streamlit.app](https://meditools.streamlit.app/)
- **Contact the Developers**: Reach out to us directly for authentication credentials to access the deployed application.

### Option 2: Local Installation

#### Prerequisites
- Python 3.8+
- Dependencies from `requirements.txt`
- API Access:
  - ✅ OpenAI (Required)
  - ✅ OpenRouter (Required)
  - ✅ Diffbot (Required for AI-Enhanced PubMed Tool)
  - ✅ Serper (Required for Google News Tool)
  - ❌ SendGrid (Optional, not required for tools)

#### Configuration

You will need to create a `secrets.toml` file to store API keys and app configuration securely:

```toml
# Streamlit secrets configuration template

# OpenAI
OPENAI_API_KEY = "your_openai_api_key"

#Serper
SERPER_API_KEY = "your_serper_api_key"

#openrouter
OpenRouter_API_Key = "your_openrouter_api_key"

#diffbot
DiffBot_API_Key = "your_diffbot_api_key"

#sendgrid (Not required for tools)
sendgrid_API_Key = "your_sendgrid_api_key"

# Authentication
password = "your_secure_application_password"
```
---

⚠️ **Note:** Contact the project developers if you need any help!

---

## 🚀 Installation Steps

### 1. Clone the repository
```bash
git clone https://github.com/amralshatnawi/meditools.git
cd meditools
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up Streamlit secrets
Create a 'secrets.toml' file inside the '.streamlit/' directory:
```
meditools/
├── .streamlit/
│   └── secrets.toml
```

Populate secrets.toml with the required API keys and configuration values.
📌 Use the `secrets.toml` template above and contact the developers for any questions!

### 4. Run the application

```bash 
streamlit run app.py
```
---

## 🤝 Contributions & Feedback
We welcome contributions, feedback, and ideas to improve MediTools further!

