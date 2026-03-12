# Ask-AI-Buffett
Your AI Warren Buffett advisor. Gemini-powered insights on value investing, explained simply. Analyze data, ask questions, invest smarter long-term.

## Overview
This project is a lightweight, **highly token-efficient** Streamlit web application that simulates a conversation with Warren Buffett. It leverages Google's cutting-edge **Gemini 2.5 Flash** model to provide financial insights grounded tightly in Buffett's famous value investing philosophy. 

With a premium and aesthetic user interface, the chatbot guides users with folksy, patient wisdom while strictly avoiding speculative assets like day trading and cryptocurrency.

### Key Features
- **Token Efficient**: The chatbot naturally caps the chat history sent to the LLM. It limits conversation context (keeping only the most recent messages) explicitly to minimize API token usage over long sessions.
- **Pure Knowledge Driven**: Runs purely off the deep intrinsic knowledge of the Gemini 2.5 Flash model specifically configured with an optimized, concise system persona. No unnecessary RAG pipelines or large documents are embedded in the prompt, saving vast amounts of tokens and execution time.
- **Folksy & Wise Persona**: Strictly uses "Buffettisms" such as analogies to farming and baseball when explaining investment concepts.
- **Beautiful UI**: Built with Streamlit but heavily customized with modern CSS for a glassmorphism and premium dark-mode aesthetic.

---

## Architecture
1. **Frontend**: Streamlit with custom HTML/CSS injections for a rich UI.
2. **Backend Engine**: `google-genai` official Python SDK.
3. **Model**: `gemini-2.5-flash` natively integrated with a strict `GenerateContentConfig` for optimal temperature and persona.
4. **State Management**: Streamlit's `session_state` preserves chat history natively, and slicing logic prevents token bloat.

---

## 🚀 Quick Setup & Installation

### Prerequisites
- Python 3.9+
- A Google Gemini API Key. Get one for free at the [Google AI Studio](https://aistudio.google.com/).

### 1. Clone & Install
```bash
git clone https://github.com/harishraoyadagiri/Ask-AI-Buffett.git
cd Ask-AI-Buffett

# Create a virtual environment (recommended)
python -m venv venv
# Activate on Windows:
venv\Scripts\activate
# Activate on Mac/Linux:
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 2. Configure Environment
Copy the example environment file:
```bash
cp .env.example .env
```
Edit `.env` and add your actual Gemini API Key:
```env
GEMINI_API_KEY=your_actual_api_key_here
```

### 3. Run the App Locally
Launch the Streamlit server:
```bash
streamlit run app.py
```
The application will automatically pop open in your default browser at `http://localhost:8501`.

---

## 🌐 Deploying to the Cloud (Free)

To make this chatbot accessible via a public link (so anyone can use it without needing to type in an API key or run code locally), the easiest method is to deploy it for free using **Streamlit Community Cloud**.

### Steps to Deploy:
1. **Push to GitHub**: Ensure this repository is pushed to your GitHub account and is set to **Public** (or Private if you prefer).
2. **Go to Streamlit Cloud**: Navigate to [share.streamlit.io](https://share.streamlit.io/) and log in with your GitHub account.
3. **Create the App**: Click **"New App"**.
   - **Repository:** Select your `Ask-AI-Buffett` repo.
   - **Branch:** `main` (or whichever branch your code is on).
   - **Main file path:** `app.py`
4. **Add your API Key as a Secret**:
   - Before clicking "Deploy", click on **"Advanced settings..."**.
   - In the **Secrets** box, add your Gemini API key just like you did in the `.env` file:
     ```toml
     GEMINI_API_KEY="your_actual_api_key_here"
     ```
   - Click **Save**.
5. **Deploy**: Click the **"Deploy!"** button.

Streamlit will build your app and give you a public URL (e.g., `https://your-app-name.streamlit.app/`). Anyone who visits this link will be able to talk to the AI Buffett, and it will securely use the API key you provided in the secrets!

---

## Token Optimization Strategy Deep Dive
To fulfill the requirement of using *less tokens*, the following measures were taken:
1. **Context Window Capping**: The chatbot only references a sliding window of the last `4` interactions. Therefore, a 100-turn conversation will only consume the API token cost of a 4-turn conversation during the 100th message.
2. **Short System Instructions**: Instead of 100+ lines of prompting, a concise ~60-word instruction block precisely locks the model into the Buffett persona without wasting tokens per request.
3. **Flash Models**: Utilitizes `gemini-2.5-flash` for high intelligence at extreme speeds and high token-efficiency limits.

## Disclaimer
> **Note**: This is an educational tool and simulation. It does not provide personalized, professional financial advice. All investments carry risk. Never make investment decisions solely based on an AI chatbot's responses.
