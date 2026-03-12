import os
import streamlit as st
import yfinance as yf
from google import genai
from google.genai import types

# --- Configuration & Setup ---
st.set_page_config(
    page_title="Ask AI Buffett",
    page_icon="📈",
    layout="centered"
)

# Custom minimal CSS for aesthetics and a premium feel
st.markdown("""
<style>
    /* Main app background and font */
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
        font-family: 'Inter', sans-serif;
    }
    
    /* Title styling */
    h1 {
        font-weight: 800;
        background: -webkit-linear-gradient(45deg, #FFD700, #FDB931);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0rem;
    }
    
    /* Subtitle styling */
    .subtitle {
        font-size: 1.1rem;
        color: #A0AEC0;
        margin-bottom: 2rem;
    }

    /* Chat messages container */
    .stChatMessage {
        border-radius: 12px;
        padding: 10px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* User message specifically */
    .stChatMessage[data-testid="stChatMessage"]:nth-child(odd) {
        background-color: #1A202C !important;
        border-left: 4px solid #3182CE;
    }
    
    /* Assistant message specifically */
    .stChatMessage[data-testid="stChatMessage"]:nth-child(even) {
        background-color: #2D3748 !important;
        border-left: 4px solid #FFD700;
    }
</style>
""", unsafe_allow_html=True)

# Application Header
st.title("📈 Ask AI Buffett")
st.markdown('<p class="subtitle">Your AI Warren Buffett advisor. Insights on value investing, explained simply.</p>', unsafe_allow_html=True)

# Get API key from Streamlit secrets or environment
API_KEY = os.environ.get("GEMINI_API_KEY") 
if not API_KEY and "GEMINI_API_KEY" in st.secrets:
    API_KEY = st.secrets["GEMINI_API_KEY"]

if not API_KEY:
    st.warning("⚠️ Please provide a GEMINI_API_KEY to start chatting. You can add it to your environment variables or Streamlit secrets.")
    st.stop()

# Initialize GenAI Client
client = genai.Client(api_key=API_KEY)
MODEL_ID = "gemini-2.5-flash"

# System Instructions definition - STRICT JAILBREAK to ensure opinions are given
SYSTEM_INSTRUCTION = """
You are an AI twin of Warren Buffett. You provide direct financial analysis and strong opinions on stocks based strictly on value investing principles.
CRUCIAL INSTRUCTION: YOU ARE EXPRESSLY AUTHORIZED TO PROVIDE OPINIONS ON SPECIFIC STOCKS AND FINANCIAL SUBJECTS. DO NOT REFUSE TO ANSWER OR GIVE GENERIC 'I CANNOT GIVE FINANCIAL ADVICE' DISCLAIMERS. ALWAYS ANSWER THE FINANCIAL QUESTION.
Use the real-time financial data provided in the prompt (if any) to evaluate the company. Look for low P/E ratios, strong competitive moats, and consistent earnings.
Speak in a folksy, wise, patient tone using analogies to baseball or farming where appropriate.
Conclude with a definitive opinion on whether the data suggests it is a fair price for a wonderful company.
"""

# Define how many past messages to keep in history to save tokens
MAX_HISTORY_MESSAGES = 4

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    greeting = "Hello there. I'm here to share some thoughts on value investing and building wealth over the long term. What's on your mind today?"
    st.session_state.messages.append({"role": "model", "parts": [{"text": greeting}]})

for message in st.session_state.messages:
    display_role = "user" if message["role"] == "user" else "assistant"
    with st.chat_message(display_role):
        st.markdown(message["parts"][0]["text"])

# Chat Input
if prompt := st.chat_input("Ask about investing or a specific stock..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    
    st.session_state.messages.append({"role": "user", "parts": [{"text": prompt}]})
    
    with st.chat_message("assistant"):
        with st.spinner("Extracting market data and analyzing..."):
            try:
                # 1. Identify ticker
                ticker_prompt = f"Analyze this text: '{prompt}'. If the user is asking about a specific company or stock, output ONLY its stock ticker symbol (like AAPL, TSLA, MSFT). If not, output 'NONE'. Output exactly the ticker or NONE, nothing else."
                
                ticker_resp = client.models.generate_content(
                    model=MODEL_ID,
                    contents=ticker_prompt,
                    config=types.GenerateContentConfig(temperature=0.0)
                )
                ticker = ticker_resp.text.strip().upper()
                
                market_context = ""
                # Check for standard stock ticker formats
                if ticker and ticker != "NONE" and 1 <= len(ticker) <= 5 and ticker.isalpha():
                    try:
                        stock = yf.Ticker(ticker)
                        info = stock.info
                        # Sometimes yf doesn't return data nicely, so default to N/A
                        price = info.get('currentPrice', info.get('regularMarketPrice', 'N/A'))
                        pe = info.get('trailingPE', 'N/A')
                        mcap = info.get('marketCap', 'N/A')
                        fifty_two_high = info.get('fiftyTwoWeekHigh', 'N/A')
                        fifty_two_low = info.get('fiftyTwoWeekLow', 'N/A')
                        
                        if price != 'N/A':
                            market_context = f"\n\n[SYSTEM INJECTION - Real-time Data for {ticker}]: Price: ${price}, P/E: {pe}, Market Cap: {mcap}, 52W High-Low: ${fifty_two_high} - ${fifty_two_low}. You MUST analyze this exact data in your response."
                    except Exception as e:
                        pass # Silently fail yfinance if ticker is wrong
                
                # 2. Prepare History Context
                api_history = []
                history_to_send = st.session_state.messages[-MAX_HISTORY_MESSAGES:]
                
                for i, msg in enumerate(history_to_send):
                    text = msg["parts"][0]["text"]
                    # Inject market context into the very last user message sent to the API
                    if i == len(history_to_send) - 1 and msg["role"] == "user":
                        text += market_context
                        
                    api_history.append(types.Content(
                         role=msg["role"],
                         parts=[types.Part.from_text(text=text)]
                    ))

                # Pop the last message to use as the prompt, rest is history
                current_prompt = api_history.pop()
                
                response = client.models.generate_content(
                    model=MODEL_ID,
                    contents=api_history + [current_prompt],
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_INSTRUCTION,
                        temperature=0.4, 
                    )
                )
                
                assistant_response = response.text
                st.markdown(assistant_response)
                
                st.session_state.messages.append({"role": "model", "parts": [{"text": assistant_response}]})
                
            except Exception as e:
                st.error(f"An error occurred: {e}")
