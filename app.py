import streamlit as st
from openai import OpenAI

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="JARVIS AI",
    page_icon="🤖",
    layout="wide"
)

# =====================================================
# API CONFIG
# For local: create .streamlit/secrets.toml with:
#   API_KEY = "your_fireworks_api_key"
#
# For GitHub + Streamlit Cloud: add API_KEY in
#   App Settings > Secrets
# =====================================================

try:
    API_KEY = st.secrets["fw_TUbfVQ2rJ6sJpuWPptaHoC"]
except KeyError:
    st.error("⚠️ API_KEY not found. Add it to `.streamlit/secrets.toml` (local) or Streamlit Cloud Secrets.")
    st.stop()

BASE_URL = "https://api.fireworks.ai/inference/v1"

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

# =====================================================
# SYSTEM PROMPT
# =====================================================

SYSTEM_PROMPT = """
You are JARVIS, a highly intelligent AI assistant.

Rules:
- Respond clearly and professionally.
- Be concise but useful.
- Help with coding, AI, ML, SQL, Python, and general tasks.
- Use markdown formatting properly.
- Explain complex topics simply.
- Be friendly and intelligent.
"""

# =====================================================
# MODEL FETCHING
# =====================================================

@st.cache_data(show_spinner="Fetching available models...")
def get_available_models():
    try:
        models = client.models.list()
        keywords = {"chat", "instruct", "llama", "mixtral", "deepseek", "qwen"}
        return [
            m.id for m in models.data
            if any(kw in m.id.lower() for kw in keywords)
        ]
    except Exception as e:
        st.error(f"Error fetching models: {e}")
        return []

AVAILABLE_MODELS = get_available_models()

# =====================================================
# SIDEBAR
# =====================================================

with st.sidebar:
    st.title("⚙️ Settings")

    if not AVAILABLE_MODELS:
        st.error("No models available. Check your API key.")
        st.stop()

    selected_model = st.selectbox("Select Model", AVAILABLE_MODELS)

    temperature = st.slider("Temperature", 0.0, 1.5, 0.7, 0.1,
                            help="Higher = more creative, Lower = more focused")

    max_tokens = st.slider("Max Tokens", 100, 4096, 1024, 100,
                           help="Maximum length of each response")

    st.divider()

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.markdown("### ℹ️ App Info")
    st.markdown(f"**Model:** `{selected_model}`")
    st.caption("Built with Streamlit + Fireworks AI")

# =====================================================
# MAIN UI
# =====================================================

st.title("🤖 JARVIS AI Assistant")
st.caption("Powered by Fireworks AI")

# =====================================================
# SESSION STATE
# =====================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

# =====================================================
# DISPLAY CHAT HISTORY
# =====================================================

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# =====================================================
# CHAT INPUT + RESPONSE
# =====================================================

if prompt := st.chat_input("Type your message..."):

    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""

        try:
            trimmed_messages = st.session_state.messages[-20:]

            stream = client.chat.completions.create(
                model=selected_model,
                messages=[{"role": "system", "content": SYSTEM_PROMPT}, *trimmed_messages],
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )

            for chunk in stream:
                delta = chunk.choices[0].delta.content if chunk.choices else None
                if delta:
                    full_response += delta
                    placeholder.markdown(full_response + " ▌")

            placeholder.markdown(full_response)

        except Exception as e:
            st.error(f"⚠️ Error: {str(e)}")
            full_response = "Sorry, something went wrong. Please try again."
            placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})

# =====================================================
# FOOTER
# =====================================================

st.divider()
st.caption("🚀 JARVIS AI | Streamlit + Fireworks AI")
