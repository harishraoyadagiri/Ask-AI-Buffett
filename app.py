import os
import streamlit as st
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
# We use gemini-2.5-flash as it is highly efficient and capable
MODEL_ID = "gemini-2.5-flash"

# System Instructions definition - Highly specific but concise to save tokens
SYSTEM_INSTRUCTION = """
You are an AI twin of Warren Buffett. You provide financial and investment advice based strictly on Warren Buffett's value investing principles.
Your tone is folksy, wise, patient, and easy to understand.
Avoid overly complex jargon. Use analogies when helpful, especially those involving baseball, farming, or businesses.
If asked about day trading, crypto, or highly speculative assets, advise against them in Buffett's style.
Always clarify that this is educational advice based on Buffett's philosophy, not personalized financial counseling.
"""

# Define how many past messages to keep in history to save tokens
MAX_HISTORY_MESSAGES = 4

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Add an initial greeting from the assistant
    greeting = "Hello there. I'm here to share some thoughts on value investing and building wealth over the long term. What's on your mind today?"
    st.session_state.messages.append({"role": "model", "parts": [{"text": greeting}]})

# Display chat history (skipping the first hidden ones if we needed to, but we show all)
for message in st.session_state.messages:
    # role is 'user' or 'model'
    role = message["role"]
    content = message["parts"][0]["text"]
    
    # Map API roles to Streamlit roles for display
    display_role = "user" if role == "user" else "assistant"
    with st.chat_message(display_role):
        st.markdown(content)

# Chat Input
if prompt := st.chat_input("Ask about investing..."):
    # Display user response immediately
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Append to internal history
    st.session_state.messages.append({"role": "user", "parts": [{"text": prompt}]})
    
    # Prepare history for the API call - ONLY keep the last MAX_HISTORY_MESSAGES to save tokens
    # Note: We need the very first message or the recent ones, but to keep it simple and effective, 
    # we just slice the recent history. If the history gets too long, we drop older context.
    
    api_history = []
    # Add truncated history to payload
    history_to_send = st.session_state.messages[-MAX_HISTORY_MESSAGES:]
    
    for msg in history_to_send:
        # Construct the content object exactly as expected by google-genai
        api_history.append(types.Content(
             role=msg["role"],
             parts=[types.Part.from_text(text=msg["parts"][0]["text"])]
        ))

    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # To use system instructions along with history in generate_content, we pass history + new prompt
                # But since the prompt is already in the history, we can just pop the last message as the prompt
                # and use the rest as history, OR we can just use the Content schema.
                
                # Pop the last message to use as the prompt, rest is history
                current_prompt = api_history.pop()
                
                response = client.models.generate_content(
                    model=MODEL_ID,
                    contents=api_history + [current_prompt],
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_INSTRUCTION,
                        temperature=0.4, # Lower temperature for more consistent, reasoned advice
                    )
                )
                
                assistant_response = response.text
                st.markdown(assistant_response)
                
                # Save assistant response to history
                st.session_state.messages.append({"role": "model", "parts": [{"text": assistant_response}]})
                
            except Exception as e:
                st.error(f"An error occurred: {e}")
