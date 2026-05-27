import streamlit as st
from openai import OpenAI

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="JARVIS AI",
    page_icon="🧠",
    layout="wide"
)

# =====================================================
# NEURAL BRAIN CSS THEME
# =====================================================

st.markdown("""
<style>

/* ── Google Font ── */
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;600&display=swap');

/* ── Global Reset ── */
*, *::before, *::after { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"] {
    background: #020b18 !important;
    color: #c8e6ff !important;
    font-family: 'Rajdhani', sans-serif !important;
}

[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(ellipse 80% 60% at 60% 20%, rgba(0,150,255,0.07) 0%, transparent 70%),
        radial-gradient(ellipse 50% 40% at 20% 80%, rgba(255,140,0,0.05) 0%, transparent 60%),
        #020b18 !important;
}

/* ── Animated neural-node dots in background ── */
[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image:
        radial-gradient(circle, rgba(0,180,255,0.18) 1px, transparent 1px),
        radial-gradient(circle, rgba(255,140,0,0.10) 1px, transparent 1px);
    background-size: 60px 60px, 90px 90px;
    background-position: 0 0, 30px 45px;
    animation: neuralDrift 20s linear infinite;
    pointer-events: none;
    z-index: 0;
}

@keyframes neuralDrift {
    0%   { background-position: 0 0, 30px 45px; }
    100% { background-position: 60px 60px, 90px 105px; }
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #020f22 0%, #010c1a 100%) !important;
    border-right: 1px solid rgba(0,180,255,0.15) !important;
}

[data-testid="stSidebar"] * {
    font-family: 'Rajdhani', sans-serif !important;
    color: #8ec8f0 !important;
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #00b4ff !important;
    font-family: 'Orbitron', sans-serif !important;
    font-size: 1rem !important;
    letter-spacing: 2px !important;
    text-shadow: 0 0 12px rgba(0,180,255,0.6) !important;
}

/* Sidebar sliders */
[data-testid="stSlider"] > div > div > div {
    background: rgba(0,180,255,0.15) !important;
}
[data-testid="stSlider"] [data-baseweb="slider"] div[role="slider"] {
    background: #00b4ff !important;
    box-shadow: 0 0 10px #00b4ff !important;
}

/* Sidebar selectbox */
[data-testid="stSelectbox"] > div > div {
    background: rgba(0,20,50,0.8) !important;
    border: 1px solid rgba(0,180,255,0.3) !important;
    color: #00b4ff !important;
    border-radius: 8px !important;
}

/* Sidebar button */
[data-testid="stSidebar"] button {
    background: linear-gradient(135deg, rgba(0,80,160,0.3), rgba(0,40,100,0.5)) !important;
    border: 1px solid rgba(0,180,255,0.4) !important;
    color: #00b4ff !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 600 !important;
    letter-spacing: 1px !important;
    transition: all 0.3s ease !important;
}
[data-testid="stSidebar"] button:hover {
    background: rgba(0,180,255,0.15) !important;
    box-shadow: 0 0 15px rgba(0,180,255,0.3) !important;
}

/* ── Main Title ── */
h1 {
    font-family: 'Orbitron', sans-serif !important;
    font-weight: 900 !important;
    font-size: 2.2rem !important;
    background: linear-gradient(90deg, #00b4ff 0%, #ffffff 50%, #ff8c00 100%);
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
    letter-spacing: 4px !important;
    text-shadow: none !important;
    animation: titlePulse 4s ease-in-out infinite;
}

@keyframes titlePulse {
    0%, 100% { filter: brightness(1); }
    50%       { filter: brightness(1.3); }
}

/* Caption */
[data-testid="stCaptionContainer"] p {
    color: rgba(0,180,255,0.5) !important;
    font-family: 'Rajdhani', sans-serif !important;
    letter-spacing: 2px !important;
    font-size: 0.85rem !important;
}

/* ── Chat Messages ── */
[data-testid="stChatMessage"] {
    background: rgba(0,20,50,0.55) !important;
    border: 1px solid rgba(0,180,255,0.12) !important;
    border-radius: 14px !important;
    backdrop-filter: blur(8px) !important;
    margin-bottom: 12px !important;
    padding: 14px 18px !important;
    transition: border-color 0.3s ease !important;
}
[data-testid="stChatMessage"]:hover {
    border-color: rgba(0,180,255,0.3) !important;
}

/* User messages — warm amber accent */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
    border-left: 3px solid rgba(255,140,0,0.6) !important;
    background: rgba(30,15,0,0.45) !important;
}

/* Assistant messages — cool blue accent */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {
    border-left: 3px solid rgba(0,180,255,0.6) !important;
}

[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li,
[data-testid="stChatMessage"] td {
    color: #c8e6ff !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 1.05rem !important;
    line-height: 1.7 !important;
}

/* Code blocks */
[data-testid="stChatMessage"] code {
    background: rgba(0,180,255,0.1) !important;
    color: #7dd3fc !important;
    border: 1px solid rgba(0,180,255,0.2) !important;
    border-radius: 4px !important;
    padding: 1px 5px !important;
}
[data-testid="stChatMessage"] pre {
    background: rgba(0,10,30,0.8) !important;
    border: 1px solid rgba(0,180,255,0.2) !important;
    border-radius: 10px !important;
}

/* ── Chat Input ── */
[data-testid="stChatInput"] {
    background: rgba(0,20,50,0.7) !important;
    border: 1px solid rgba(0,180,255,0.3) !important;
    border-radius: 30px !important;
    backdrop-filter: blur(10px) !important;
    box-shadow: 0 0 20px rgba(0,180,255,0.1) !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: rgba(0,180,255,0.7) !important;
    box-shadow: 0 0 25px rgba(0,180,255,0.25) !important;
}
[data-testid="stChatInput"] textarea {
    color: #c8e6ff !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 1rem !important;
    background: transparent !important;
}
[data-testid="stChatInput"] textarea::placeholder {
    color: rgba(0,180,255,0.35) !important;
}

/* Send button */
[data-testid="stChatInput"] button {
    background: radial-gradient(circle, rgba(0,150,255,0.4), rgba(0,60,150,0.4)) !important;
    border: 1px solid rgba(0,180,255,0.5) !important;
    border-radius: 50% !important;
    box-shadow: 0 0 12px rgba(0,180,255,0.3) !important;
}

/* ── Brain Thinking Animation ── */
.brain-thinking {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 16px 20px;
    background: rgba(0,20,50,0.7);
    border: 1px solid rgba(0,180,255,0.2);
    border-left: 3px solid rgba(0,180,255,0.6);
    border-radius: 14px;
    margin-bottom: 12px;
    backdrop-filter: blur(8px);
}

.brain-svg {
    flex-shrink: 0;
    width: 48px;
    height: 48px;
    animation: brainPulse 2s ease-in-out infinite;
    filter: drop-shadow(0 0 8px rgba(0,180,255,0.7));
}

@keyframes brainPulse {
    0%, 100% { transform: scale(1);   filter: drop-shadow(0 0 6px rgba(0,180,255,0.6)); }
    50%       { transform: scale(1.08); filter: drop-shadow(0 0 16px rgba(0,180,255,0.95)); }
}

.brain-right {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.brain-label {
    font-family: 'Orbitron', sans-serif;
    font-size: 0.75rem;
    letter-spacing: 3px;
    color: #00b4ff;
    animation: labelFlicker 3s ease-in-out infinite;
}

@keyframes labelFlicker {
    0%, 90%, 100% { opacity: 1; }
    95%            { opacity: 0.4; }
}

.synapses {
    display: flex;
    gap: 5px;
    align-items: center;
}

.synapse {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    animation: synapsefire 1.4s ease-in-out infinite;
}
.synapse:nth-child(1) { background: #00b4ff; animation-delay: 0s; }
.synapse:nth-child(2) { background: #0090e0; animation-delay: 0.2s; }
.synapse:nth-child(3) { background: #ff8c00; animation-delay: 0.4s; }
.synapse:nth-child(4) { background: #0090e0; animation-delay: 0.6s; }
.synapse:nth-child(5) { background: #00b4ff; animation-delay: 0.8s; }
.synapse:nth-child(6) { background: #ff8c00; animation-delay: 1.0s; }
.synapse:nth-child(7) { background: #0090e0; animation-delay: 1.2s; }

@keyframes synapsefire {
    0%, 100% { transform: scale(1);   opacity: 0.3; box-shadow: none; }
    50%       { transform: scale(1.6); opacity: 1;   box-shadow: 0 0 8px currentColor; }
}

.neural-bar {
    width: 180px;
    height: 3px;
    background: rgba(0,180,255,0.15);
    border-radius: 3px;
    overflow: hidden;
}
.neural-bar-fill {
    height: 100%;
    width: 40%;
    background: linear-gradient(90deg, transparent, #00b4ff, #ff8c00, #00b4ff, transparent);
    border-radius: 3px;
    animation: neuralScan 1.8s ease-in-out infinite;
}
@keyframes neuralScan {
    0%   { transform: translateX(-200%); }
    100% { transform: translateX(400%); }
}

/* ── Divider ── */
hr {
    border-color: rgba(0,180,255,0.1) !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: #010c1a; }
::-webkit-scrollbar-thumb {
    background: rgba(0,180,255,0.3);
    border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover { background: rgba(0,180,255,0.6); }

</style>
""", unsafe_allow_html=True)

# =====================================================
# BRAIN THINKING HTML COMPONENT
# =====================================================

BRAIN_THINKING_HTML = """
<div class="brain-thinking">
  <svg class="brain-svg" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
    <!-- Brain outline glow paths -->
    <path d="M32 8C24 8 18 13 17 20C13 20 10 23 10 27C8 28 6 31 7 35C6 38 8 42 12 43C13 47 17 50 22 50C24 52 27 53 32 53C37 53 40 52 42 50C47 50 51 47 52 43C56 42 58 38 57 35C58 31 56 28 54 27C54 23 51 20 47 20C46 13 40 8 32 8Z"
      stroke="#00b4ff" stroke-width="1.5" fill="rgba(0,40,100,0.3)"/>
    <!-- Neural connections animated -->
    <line x1="32" y1="8"  x2="32" y2="53" stroke="rgba(0,180,255,0.2)" stroke-width="0.5"/>
    <line x1="17" y1="20" x2="47" y2="20" stroke="rgba(0,180,255,0.2)" stroke-width="0.5"/>
    <line x1="12" y1="43" x2="52" y2="43" stroke="rgba(0,180,255,0.2)" stroke-width="0.5"/>
    <!-- Synaptic nodes -->
    <circle cx="32" cy="20" r="2" fill="#ff8c00">
      <animate attributeName="opacity" values="0.3;1;0.3" dur="1.2s" repeatCount="indefinite"/>
    </circle>
    <circle cx="20" cy="31" r="2" fill="#00b4ff">
      <animate attributeName="opacity" values="1;0.3;1" dur="1.4s" repeatCount="indefinite"/>
    </circle>
    <circle cx="44" cy="31" r="2" fill="#00b4ff">
      <animate attributeName="opacity" values="0.3;1;0.3" dur="1.0s" repeatCount="indefinite"/>
    </circle>
    <circle cx="32" cy="42" r="2" fill="#ff8c00">
      <animate attributeName="opacity" values="1;0.3;1" dur="1.6s" repeatCount="indefinite"/>
    </circle>
    <circle cx="25" cy="25" r="1.5" fill="#7dd3fc">
      <animate attributeName="opacity" values="0.2;1;0.2" dur="0.9s" repeatCount="indefinite"/>
    </circle>
    <circle cx="39" cy="25" r="1.5" fill="#7dd3fc">
      <animate attributeName="opacity" values="1;0.2;1" dur="1.1s" repeatCount="indefinite"/>
    </circle>
    <!-- Spark lines -->
    <line x1="20" y1="31" x2="32" y2="20" stroke="#00b4ff" stroke-width="0.8" opacity="0.5">
      <animate attributeName="opacity" values="0.1;0.7;0.1" dur="1.3s" repeatCount="indefinite"/>
    </line>
    <line x1="44" y1="31" x2="32" y2="20" stroke="#00b4ff" stroke-width="0.8">
      <animate attributeName="opacity" values="0.7;0.1;0.7" dur="1.3s" repeatCount="indefinite"/>
    </line>
    <line x1="20" y1="31" x2="32" y2="42" stroke="#ff8c00" stroke-width="0.8">
      <animate attributeName="opacity" values="0.1;0.8;0.1" dur="1.5s" repeatCount="indefinite"/>
    </line>
    <line x1="44" y1="31" x2="32" y2="42" stroke="#ff8c00" stroke-width="0.8">
      <animate attributeName="opacity" values="0.8;0.1;0.8" dur="1.5s" repeatCount="indefinite"/>
    </line>
  </svg>

  <div class="brain-right">
    <div class="brain-label">NEURAL PROCESSING ...</div>
    <div class="synapses">
      <div class="synapse"></div>
      <div class="synapse"></div>
      <div class="synapse"></div>
      <div class="synapse"></div>
      <div class="synapse"></div>
      <div class="synapse"></div>
      <div class="synapse"></div>
    </div>
    <div class="neural-bar"><div class="neural-bar-fill"></div></div>
  </div>
</div>
"""

# =====================================================
# API CONFIG
# =====================================================

API_KEY = "fw_TUbfVQ2rJ6sJpuWPptaHoC"   # ← paste your key here

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

@st.cache_data(show_spinner="🧠 Scanning neural networks...")
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
    st.title("⚙ JARVIS CONFIG")

    if not AVAILABLE_MODELS:
        st.error("No models available. Check your API key.")
        st.stop()

    selected_model = st.selectbox("🧬 Neural Model", AVAILABLE_MODELS)

    temperature = st.slider("🌡 Temperature", 0.0, 1.5, 0.7, 0.1,
                            help="Higher = more creative, Lower = more focused")

    max_tokens = st.slider("⚡ Max Tokens", 100, 4096, 1024, 100,
                           help="Maximum length of each response")

    st.divider()

    if st.button("🗑 Clear Memory", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.markdown("### 📡 Status")
    st.markdown(f"**Model:** `{selected_model.split('/')[-1]}`")
    st.caption("JARVIS AI · Fireworks AI")

# =====================================================
# MAIN UI
# =====================================================

st.title("JARVIS AI")
st.caption("NEURAL INTELLIGENCE SYSTEM · POWERED BY FIREWORKS AI")

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

if prompt := st.chat_input("Interface with JARVIS..."):

    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Show brain thinking animation while generating
        thinking_placeholder = st.empty()
        thinking_placeholder.markdown(BRAIN_THINKING_HTML, unsafe_allow_html=True)

        response_placeholder = st.empty()
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

            first_chunk = True
            for chunk in stream:
                delta = chunk.choices[0].delta.content if chunk.choices else None
                if delta:
                    if first_chunk:
                        # Hide brain animation once text starts arriving
                        thinking_placeholder.empty()
                        first_chunk = False
                    full_response += delta
                    response_placeholder.markdown(full_response + " ▌")

            response_placeholder.markdown(full_response)

        except Exception as e:
            thinking_placeholder.empty()
            st.error(f"⚠️ Neural error: {str(e)}")
            full_response = "Sorry, something went wrong. Please try again."
            response_placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})

# =====================================================
# FOOTER
# =====================================================

st.divider()
st.caption("⚡ JARVIS AI · Neural Intelligence System · Streamlit + Fireworks AI")
