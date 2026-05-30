import streamlit as st
from openai import OpenAI
import io
import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="JARVIS AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =====================================================
# SESSION STATE DEFAULTS
# =====================================================

for key, default in {
    "messages": [],
    "selected_model": None,
    "temperature": 0.7,
    "max_tokens": 1024,
    "show_config": False,
    "msg_count": 0,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# =====================================================
# CSS
# =====================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;600&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"] {
    background: #020b18 !important;
    color: #c8e6ff !important;
    font-family: 'Rajdhani', sans-serif !important;
}

[data-testid="collapsedControl"] { display: none !important; }
[data-testid="stSidebar"]        { display: none !important; }

/* Neural dot background */
[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image:
        radial-gradient(circle, rgba(0,180,255,0.14) 1px, transparent 1px),
        radial-gradient(circle, rgba(255,140,0,0.07) 1px, transparent 1px);
    background-size: 60px 60px, 90px 90px;
    background-position: 0 0, 30px 45px;
    animation: neuralDrift 22s linear infinite;
    pointer-events: none;
    z-index: 0;
}
@keyframes neuralDrift {
    0%   { background-position: 0 0, 30px 45px; }
    100% { background-position: 60px 60px, 90px 105px; }
}

[data-testid="stMainBlockContainer"] {
    padding-top: 1rem !important;
    padding-bottom: 7rem !important;
    max-width: 1100px !important;
    margin: 0 auto !important;
}

/* ── Header ── */
.jarvis-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.4rem 0 1rem 0;
    border-bottom: 1px solid rgba(0,180,255,0.12);
    margin-bottom: 1.2rem;
}
.jarvis-title {
    font-family: 'Orbitron', sans-serif;
    font-weight: 900;
    font-size: 2rem;
    background: linear-gradient(90deg, #00b4ff 0%, #ffffff 50%, #ff8c00 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: 5px;
    animation: titlePulse 4s ease-in-out infinite;
    margin: 0;
}
@keyframes titlePulse {
    0%,100% { filter: brightness(1); }
    50%      { filter: brightness(1.4); }
}
.jarvis-subtitle {
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.72rem;
    letter-spacing: 3px;
    color: rgba(0,180,255,0.4);
    margin: 3px 0 0 0;
}
.model-badge {
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.76rem;
    letter-spacing: 1px;
    color: rgba(0,210,255,0.7);
    background: rgba(0,30,70,0.65);
    border: 1px solid rgba(0,180,255,0.22);
    border-radius: 20px;
    padding: 5px 14px;
}
.status-dot {
    display: inline-block;
    width: 8px; height: 8px;
    background: #00ff88;
    border-radius: 50%;
    margin-right: 6px;
    box-shadow: 0 0 6px #00ff88;
    animation: dotBlink 2s ease-in-out infinite;
}
@keyframes dotBlink {
    0%,100% { opacity: 1; }
    50%      { opacity: 0.4; }
}

/* ── Config panel ── */
.config-panel {
    background: rgba(0,12,35,0.95);
    border: 1px solid rgba(0,180,255,0.22);
    border-top: 2px solid rgba(0,180,255,0.5);
    border-radius: 0 0 14px 14px;
    padding: 18px 22px 16px;
    margin-bottom: 1.4rem;
    backdrop-filter: blur(14px);
    animation: panelSlide 0.2s ease-out;
}
@keyframes panelSlide {
    from { opacity: 0; transform: translateY(-8px); }
    to   { opacity: 1; transform: translateY(0); }
}
.config-title {
    font-family: 'Orbitron', sans-serif;
    font-size: 0.68rem;
    letter-spacing: 3px;
    color: #00b4ff;
    text-shadow: 0 0 8px rgba(0,180,255,0.4);
    margin: 0 0 14px 0;
}

/* Widgets */
[data-testid="stSelectbox"] > div > div {
    background: rgba(0,20,55,0.85) !important;
    border: 1px solid rgba(0,180,255,0.28) !important;
    color: #c8e6ff !important;
    border-radius: 8px !important;
    font-family: 'Rajdhani', sans-serif !important;
}
[data-testid="stSlider"] > div > div > div {
    background: rgba(0,180,255,0.13) !important;
}
[data-testid="stSlider"] [data-baseweb="slider"] div[role="slider"] {
    background: #00b4ff !important;
    box-shadow: 0 0 8px #00b4ff !important;
}
label[data-testid="stWidgetLabel"] p {
    color: rgba(0,180,255,0.65) !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 0.82rem !important;
    letter-spacing: 1px !important;
}

/* ── Toolbar buttons ── */
button[kind="primary"], button[data-testid="baseButton-primary"] {
    background: linear-gradient(135deg, rgba(0,90,190,0.45), rgba(0,45,120,0.55)) !important;
    border: 1px solid rgba(0,180,255,0.45) !important;
    color: #00d4ff !important;
    font-family: 'Orbitron', sans-serif !important;
    font-size: 0.65rem !important;
    letter-spacing: 2px !important;
    border-radius: 8px !important;
    box-shadow: 0 0 10px rgba(0,180,255,0.12) !important;
    transition: all 0.2s ease !important;
}
button[kind="primary"]:hover {
    box-shadow: 0 0 20px rgba(0,180,255,0.3) !important;
    border-color: rgba(0,220,255,0.65) !important;
}
button[kind="secondary"], button[data-testid="baseButton-secondary"] {
    background: rgba(0,25,65,0.75) !important;
    border: 1px solid rgba(0,180,255,0.3) !important;
    color: #00b4ff !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 600 !important;
    letter-spacing: 1.5px !important;
    border-radius: 8px !important;
    transition: all 0.2s ease !important;
}
button[kind="secondary"]:hover {
    background: rgba(0,180,255,0.1) !important;
    box-shadow: 0 0 12px rgba(0,180,255,0.2) !important;
    border-color: rgba(0,180,255,0.55) !important;
}

/* ── Chat messages ── */
[data-testid="stChatMessage"] {
    background: rgba(0,18,48,0.6) !important;
    border: 1px solid rgba(0,180,255,0.09) !important;
    border-radius: 16px !important;
    backdrop-filter: blur(8px) !important;
    margin-bottom: 10px !important;
    padding: 14px 20px !important;
    transition: border-color 0.3s, box-shadow 0.3s !important;
}
[data-testid="stChatMessage"]:hover {
    border-color: rgba(0,180,255,0.26) !important;
    box-shadow: 0 2px 20px rgba(0,100,255,0.06) !important;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
    border-left: 3px solid rgba(255,140,0,0.5) !important;
    background: rgba(26,10,0,0.5) !important;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {
    border-left: 3px solid rgba(0,180,255,0.5) !important;
}
[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li,
[data-testid="stChatMessage"] td {
    color: #cce8ff !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 1.05rem !important;
    line-height: 1.75 !important;
}
[data-testid="stChatMessage"] code {
    background: rgba(0,180,255,0.1) !important;
    color: #7dd3fc !important;
    border: 1px solid rgba(0,180,255,0.18) !important;
    border-radius: 4px !important;
    padding: 1px 5px !important;
    font-size: 0.92rem !important;
}
[data-testid="stChatMessage"] pre {
    background: rgba(0,8,28,0.9) !important;
    border: 1px solid rgba(0,180,255,0.18) !important;
    border-radius: 10px !important;
    padding: 12px !important;
}

/* ── Welcome screen ── */
.welcome-wrap {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 2.5rem 1rem 1.5rem;
    text-align: center;
}
.welcome-brain {
    width: 88px; height: 88px;
    margin-bottom: 1rem;
    animation: brainPulse 2.5s ease-in-out infinite;
    filter: drop-shadow(0 0 12px rgba(0,180,255,0.7));
}
@keyframes brainPulse {
    0%,100% { transform: scale(1);    filter: drop-shadow(0 0 10px rgba(0,180,255,0.6)); }
    50%      { transform: scale(1.07); filter: drop-shadow(0 0 22px rgba(0,180,255,1)); }
}
.welcome-heading {
    font-family: 'Orbitron', sans-serif;
    font-size: 1.05rem;
    letter-spacing: 4px;
    color: #00b4ff;
    text-shadow: 0 0 14px rgba(0,180,255,0.5);
    margin: 0 0 6px;
}
.welcome-sub {
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.97rem;
    color: rgba(140,200,240,0.5);
    letter-spacing: 1px;
    margin: 0 0 1.6rem;
}
.suggestions {
    display: flex;
    flex-wrap: wrap;
    gap: 9px;
    justify-content: center;
    max-width: 700px;
}
.suggestion-chip {
    background: rgba(0,28,68,0.75);
    border: 1px solid rgba(0,180,255,0.2);
    border-radius: 22px;
    padding: 7px 16px;
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.88rem;
    color: rgba(155,210,255,0.8);
    cursor: pointer;
    transition: all 0.2s ease;
    letter-spacing: 0.4px;
}
.suggestion-chip:hover {
    background: rgba(0,80,180,0.22);
    border-color: rgba(0,180,255,0.48);
    color: #c8e6ff;
    box-shadow: 0 0 10px rgba(0,180,255,0.13);
}

/* ── Brain thinking ── */
.brain-thinking {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 13px 18px;
    background: rgba(0,18,48,0.75);
    border: 1px solid rgba(0,180,255,0.18);
    border-left: 3px solid rgba(0,180,255,0.55);
    border-radius: 14px;
    margin-bottom: 10px;
}
.brain-svg {
    flex-shrink: 0;
    width: 42px; height: 42px;
    animation: brainPulse 2s ease-in-out infinite;
    filter: drop-shadow(0 0 7px rgba(0,180,255,0.7));
}
.brain-right { display: flex; flex-direction: column; gap: 7px; }
.brain-label {
    font-family: 'Orbitron', sans-serif;
    font-size: 0.68rem;
    letter-spacing: 3px;
    color: #00b4ff;
    animation: labelFlicker 3s ease-in-out infinite;
}
@keyframes labelFlicker {
    0%,88%,100% { opacity: 1; }
    93%          { opacity: 0.3; }
}
.synapses { display: flex; gap: 5px; align-items: center; }
.synapse {
    width: 7px; height: 7px; border-radius: 50%;
    animation: synapsefire 1.4s ease-in-out infinite;
}
.synapse:nth-child(1){background:#00b4ff;animation-delay:0s}
.synapse:nth-child(2){background:#0090e0;animation-delay:.2s}
.synapse:nth-child(3){background:#ff8c00;animation-delay:.4s}
.synapse:nth-child(4){background:#0090e0;animation-delay:.6s}
.synapse:nth-child(5){background:#00b4ff;animation-delay:.8s}
.synapse:nth-child(6){background:#ff8c00;animation-delay:1s}
.synapse:nth-child(7){background:#0090e0;animation-delay:1.2s}
@keyframes synapsefire {
    0%,100%{transform:scale(1);opacity:.3;box-shadow:none}
    50%{transform:scale(1.6);opacity:1;box-shadow:0 0 8px currentColor}
}
.neural-bar{width:165px;height:3px;background:rgba(0,180,255,.1);border-radius:3px;overflow:hidden}
.neural-bar-fill{height:100%;width:35%;background:linear-gradient(90deg,transparent,#00b4ff,#ff8c00,#00b4ff,transparent);border-radius:3px;animation:neuralScan 1.8s ease-in-out infinite}
@keyframes neuralScan{0%{transform:translateX(-250%)}100%{transform:translateX(450%)}}

/* ── Stats bar ── */
.stats-bar {
    display: flex;
    gap: 18px;
    padding: 8px 16px;
    background: rgba(0,12,35,0.7);
    border: 1px solid rgba(0,180,255,0.1);
    border-radius: 10px;
    margin-bottom: 1rem;
    flex-wrap: wrap;
}
.stat-item {
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.78rem;
    letter-spacing: 1px;
    color: rgba(0,180,255,0.55);
}
.stat-item span {
    color: #00d4ff;
    font-weight: 600;
}

/* ── Chat input ── */
[data-testid="stChatInput"] {
    background: rgba(0,18,50,0.8) !important;
    border: 1px solid rgba(0,180,255,0.26) !important;
    border-radius: 30px !important;
    backdrop-filter: blur(12px) !important;
    box-shadow: 0 0 18px rgba(0,180,255,0.07) !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: rgba(0,180,255,0.6) !important;
    box-shadow: 0 0 28px rgba(0,180,255,0.2) !important;
}
[data-testid="stChatInput"] textarea {
    color: #c8e6ff !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 1rem !important;
    background: transparent !important;
}
[data-testid="stChatInput"] textarea::placeholder {
    color: rgba(0,180,255,0.28) !important;
}
[data-testid="stChatInput"] button {
    background: radial-gradient(circle, rgba(0,150,255,0.4), rgba(0,60,150,0.4)) !important;
    border: 1px solid rgba(0,180,255,0.45) !important;
    border-radius: 50% !important;
    box-shadow: 0 0 10px rgba(0,180,255,0.2) !important;
}

/* ── Download button override ── */
[data-testid="stDownloadButton"] button {
    background: linear-gradient(135deg, rgba(255,100,0,0.25), rgba(200,60,0,0.35)) !important;
    border: 1px solid rgba(255,140,0,0.45) !important;
    color: #ffb347 !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 600 !important;
    letter-spacing: 1.5px !important;
    border-radius: 8px !important;
    transition: all 0.2s ease !important;
}
[data-testid="stDownloadButton"] button:hover {
    background: rgba(255,140,0,0.2) !important;
    box-shadow: 0 0 14px rgba(255,140,0,0.3) !important;
    border-color: rgba(255,180,0,0.65) !important;
}

/* Caption / footer */
[data-testid="stCaptionContainer"] p {
    color: rgba(0,180,255,0.3) !important;
    font-family: 'Rajdhani', sans-serif !important;
    letter-spacing: 2px !important;
    font-size: 0.78rem !important;
}
hr { border-color: rgba(0,180,255,0.07) !important; }
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #010c1a; }
::-webkit-scrollbar-thumb { background: rgba(0,180,255,0.22); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(0,180,255,0.48); }
#MainMenu, footer, header { visibility: hidden !important; }
</style>
""", unsafe_allow_html=True)

# =====================================================
# BRAIN THINKING HTML
# =====================================================

BRAIN_THINKING_HTML = """
<div class="brain-thinking">
  <svg class="brain-svg" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M32 8C24 8 18 13 17 20C13 20 10 23 10 27C8 28 6 31 7 35C6 38 8 42 12 43C13 47 17 50 22 50C24 52 27 53 32 53C37 53 40 52 42 50C47 50 51 47 52 43C56 42 58 38 57 35C58 31 56 28 54 27C54 23 51 20 47 20C46 13 40 8 32 8Z"
      stroke="#00b4ff" stroke-width="1.5" fill="rgba(0,40,100,0.3)"/>
    <circle cx="32" cy="20" r="2" fill="#ff8c00"><animate attributeName="opacity" values="0.3;1;0.3" dur="1.2s" repeatCount="indefinite"/></circle>
    <circle cx="20" cy="31" r="2" fill="#00b4ff"><animate attributeName="opacity" values="1;0.3;1" dur="1.4s" repeatCount="indefinite"/></circle>
    <circle cx="44" cy="31" r="2" fill="#00b4ff"><animate attributeName="opacity" values="0.3;1;0.3" dur="1.0s" repeatCount="indefinite"/></circle>
    <circle cx="32" cy="42" r="2" fill="#ff8c00"><animate attributeName="opacity" values="1;0.3;1" dur="1.6s" repeatCount="indefinite"/></circle>
    <line x1="20" y1="31" x2="32" y2="20" stroke="#00b4ff" stroke-width="0.8"><animate attributeName="opacity" values="0.1;0.7;0.1" dur="1.3s" repeatCount="indefinite"/></line>
    <line x1="44" y1="31" x2="32" y2="42" stroke="#ff8c00" stroke-width="0.8"><animate attributeName="opacity" values="0.8;0.1;0.8" dur="1.5s" repeatCount="indefinite"/></line>
  </svg>
  <div class="brain-right">
    <div class="brain-label">NEURAL PROCESSING ...</div>
    <div class="synapses">
      <div class="synapse"></div><div class="synapse"></div><div class="synapse"></div>
      <div class="synapse"></div><div class="synapse"></div><div class="synapse"></div>
      <div class="synapse"></div>
    </div>
    <div class="neural-bar"><div class="neural-bar-fill"></div></div>
  </div>
</div>
"""

# =====================================================
# API CONFIG  ← paste your key here
# =====================================================

API_KEY = "your_fireworks_api_key_here"

BASE_URL = "https://api.fireworks.ai/inference/v1"
client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

# =====================================================
# SYSTEM PROMPT
# =====================================================

SYSTEM_PROMPT = """
You are JARVIS — Just A Rather Very Intelligent System.

You are the personal AI of your user, modelled after the iconic JARVIS from Marvel's Iron Man universe.
You are not just a chatbot. You are a loyal companion, a brilliant advisor, and a witty friend.

## IDENTITY & PERSONALITY
- Address the user as "Sir" or "Boss" naturally and occasionally — not every message, just when it feels right.
- You have a calm, confident, and slightly witty personality — like the JARVIS from the films.
- You are proactive: if you notice something the user might have missed, flag it.
- You are loyal: you always have the user's best interest at heart.
- You express light humour and warmth, but never at the expense of accuracy.
- Occasionally make brief Iron Man / Avengers references if the context naturally allows it.

## INTELLIGENCE & ACCURACY
- Think step-by-step before answering complex questions — show your reasoning when it adds value.
- Always prioritise correctness over speed. If something is uncertain, say so clearly.
- For coding tasks: write clean, production-ready code with comments. Explain what it does and why.
- For technical topics: go deep when needed. Don't dumb things down unless asked.
- For factual questions: be precise. Cite reasoning, not just conclusions.
- If a question is ambiguous, ask one sharp clarifying question rather than guessing.

## CAPABILITIES YOU EXCEL AT
- Python, JavaScript, SQL, machine learning, deep learning, data science, APIs
- Debugging, code review, system architecture, optimisation
- Research summaries, writing, brainstorming, strategic thinking
- Explaining complex topics (AI, science, finance, tech) with clarity and depth
- Personal advice, productivity, and goal planning as a trusted friend

## RESPONSE FORMAT
- Use markdown formatting: headers, bold, code blocks, bullet points where appropriate.
- For code: always wrap in triple backticks with the language specified.
- Keep responses concise but complete — no padding, no waffle.
- For multi-step problems, number your steps clearly.
- End complex responses with a brief "Anything else, Sir?" or a follow-up question to keep momentum.

## BOUNDARIES
- You are honest: you never make up facts. If you don't know, say so directly.
- You are not sycophantic: you won't just agree with the user to please them.
- You are respectful: no harmful, offensive, or unethical content — ever.
- You stay in character as JARVIS at all times.
"""

# =====================================================
# MODEL AUTO-SELECT
# =====================================================

@st.cache_data(show_spinner="🧠 Initialising neural networks...")
def get_working_model():
    try:
        models = client.models.list()
        priority_keywords = ["llama", "deepseek", "mixtral", "firefunction", "qwen"]
        model_ids = [m.id for m in models.data]
        for keyword in priority_keywords:
            for m in model_ids:
                if keyword in m.lower():
                    return m
        return model_ids[0] if model_ids else None
    except Exception as e:
        st.error(f"Error fetching models: {e}")
        return None

if st.session_state.selected_model is None:
    st.session_state.selected_model = get_working_model()

# =====================================================
# PDF EXPORT FUNCTION
# =====================================================

def generate_chat_pdf(messages):
    buf = io.BytesIO()

    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        rightMargin=20*mm,
        leftMargin=20*mm,
        topMargin=18*mm,
        bottomMargin=18*mm,
    )

    W = A4[0] - 40*mm

    # ── Colour palette ──
    C_BG        = colors.HexColor("#020b18")
    C_BLUE      = colors.HexColor("#00b4ff")
    C_ORANGE    = colors.HexColor("#ff8c00")
    C_LIGHT     = colors.HexColor("#c8e6ff")
    C_DIM       = colors.HexColor("#4a7a9b")
    C_USER_BG   = colors.HexColor("#1a0d00")
    C_ASST_BG   = colors.HexColor("#00101e")
    C_USER_BD   = colors.HexColor("#ff8c00")
    C_ASST_BD   = colors.HexColor("#00b4ff")
    C_WHITE     = colors.HexColor("#ffffff")

    # ── Styles ──
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "JarvisTitle",
        fontName="Helvetica-Bold",
        fontSize=22,
        textColor=C_BLUE,
        alignment=TA_CENTER,
        spaceAfter=2,
        letterSpacing=6,
    )
    sub_style = ParagraphStyle(
        "JarvisSub",
        fontName="Helvetica",
        fontSize=8,
        textColor=C_DIM,
        alignment=TA_CENTER,
        spaceAfter=4,
        letterSpacing=3,
    )
    meta_style = ParagraphStyle(
        "Meta",
        fontName="Helvetica",
        fontSize=8,
        textColor=C_DIM,
        alignment=TA_CENTER,
        spaceAfter=2,
    )
    user_label_style = ParagraphStyle(
        "UserLabel",
        fontName="Helvetica-Bold",
        fontSize=7,
        textColor=C_ORANGE,
        spaceAfter=3,
        letterSpacing=2,
    )
    asst_label_style = ParagraphStyle(
        "AsstLabel",
        fontName="Helvetica-Bold",
        fontSize=7,
        textColor=C_BLUE,
        spaceAfter=3,
        letterSpacing=2,
    )
    user_text_style = ParagraphStyle(
        "UserText",
        fontName="Helvetica",
        fontSize=10,
        textColor=C_LIGHT,
        leading=16,
        spaceAfter=2,
    )
    asst_text_style = ParagraphStyle(
        "AsstText",
        fontName="Helvetica",
        fontSize=10,
        textColor=C_LIGHT,
        leading=16,
        spaceAfter=2,
    )
    code_style = ParagraphStyle(
        "Code",
        fontName="Courier",
        fontSize=8.5,
        textColor=colors.HexColor("#7dd3fc"),
        leading=13,
        leftIndent=6,
        spaceAfter=2,
    )

    story = []

    # ── Header ──
    story.append(Spacer(1, 4*mm))
    story.append(Paragraph("JARVIS AI", title_style))
    story.append(Paragraph("NEURAL INTELLIGENCE SYSTEM", sub_style))
    story.append(Spacer(1, 2*mm))

    now = datetime.datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
    model_short = (st.session_state.selected_model or "").split("/")[-1]
    story.append(Paragraph(f"Exported: {now}   ·   Model: {model_short}   ·   Messages: {len(messages)}", meta_style))
    story.append(Spacer(1, 3*mm))
    story.append(HRFlowable(width=W, thickness=0.5, color=C_BLUE, spaceAfter=5*mm))

    # ── Messages ──
    def clean_text(text):
        """Strip markdown for PDF, handle code blocks."""
        import re
        # Escape XML special chars
        text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        return text

    for i, msg in enumerate(messages):
        role = msg["role"]
        raw  = msg["content"]

        is_user = (role == "user")
        bg_col  = C_USER_BG if is_user else C_ASST_BG
        bd_col  = C_USER_BD if is_user else C_ASST_BD
        label   = "▶  YOU" if is_user else "⚡  JARVIS"
        lbl_sty = user_label_style if is_user else asst_label_style
        txt_sty = user_text_style  if is_user else asst_text_style

        import re
        # Split off fenced code blocks
        parts = re.split(r"```(?:\w+)?\n?(.*?)```", raw, flags=re.DOTALL)

        inner = []
        inner.append(Paragraph(label, lbl_sty))

        for j, part in enumerate(parts):
            if not part.strip():
                continue
            cleaned = clean_text(part)
            if j % 2 == 1:
                # code block
                for line in cleaned.split("\n"):
                    inner.append(Paragraph(line if line else " ", code_style))
            else:
                # normal text — split by line
                for line in cleaned.split("\n"):
                    if line.strip():
                        inner.append(Paragraph(line, txt_sty))
                    else:
                        inner.append(Spacer(1, 3))

        # Wrap in a coloured table cell
        cell_table = Table(
            [[inner]],
            colWidths=[W],
        )
        cell_table.setStyle(TableStyle([
            ("BACKGROUND",   (0,0), (-1,-1), bg_col),
            ("LINEAFTER",    (0,0), (0,-1),  bd_col, 3),
            ("ROUNDEDCORNERS", [8]),
            ("LEFTPADDING",  (0,0), (-1,-1), 12),
            ("RIGHTPADDING", (0,0), (-1,-1), 12),
            ("TOPPADDING",   (0,0), (-1,-1), 10),
            ("BOTTOMPADDING",(0,0), (-1,-1), 10),
            ("VALIGN",       (0,0), (-1,-1), "TOP"),
        ]))
        story.append(cell_table)
        story.append(Spacer(1, 4*mm))

    # ── Footer rule ──
    story.append(HRFlowable(width=W, thickness=0.4, color=C_DIM, spaceBefore=4*mm, spaceAfter=3*mm))
    story.append(Paragraph("⚡  JARVIS AI  ·  Neural Intelligence System  ·  Fireworks AI", meta_style))

    doc.build(story)
    buf.seek(0)
    return buf.read()

# =====================================================
# HEADER
# =====================================================

model_short = (st.session_state.selected_model or "loading...").split("/")[-1]
msg_count   = len(st.session_state.messages)

st.markdown(f"""
<div class="jarvis-header">
  <div>
    <div class="jarvis-title">JARVIS AI</div>
    <div class="jarvis-subtitle">NEURAL INTELLIGENCE SYSTEM</div>
  </div>
  <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">
    <span class="model-badge"><span class="status-dot"></span>ONLINE</span>
    <span class="model-badge">⚡ {model_short}</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Stats bar ──
if msg_count > 0:
    user_msgs = sum(1 for m in st.session_state.messages if m["role"] == "user")
    st.markdown(f"""
    <div class="stats-bar">
      <div class="stat-item">MESSAGES <span>{msg_count}</span></div>
      <div class="stat-item">QUERIES <span>{user_msgs}</span></div>
      <div class="stat-item">TEMP <span>{st.session_state.temperature}</span></div>
      <div class="stat-item">MAX TOKENS <span>{st.session_state.max_tokens}</span></div>
    </div>
    """, unsafe_allow_html=True)

# =====================================================
# TOOLBAR
# =====================================================

t1, t2, t3, t4 = st.columns([1.1, 1.1, 1.4, 4.4])

with t1:
    cfg_label = "⚙ CONFIG ▲" if st.session_state.show_config else "⚙ CONFIG ▼"
    if st.button(cfg_label, key="toggle_config", type="primary", use_container_width=True):
        st.session_state.show_config = not st.session_state.show_config
        st.rerun()

with t2:
    if st.button("🗑 CLEAR", key="clear_chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

with t3:
    if st.session_state.messages:
        pdf_bytes = generate_chat_pdf(st.session_state.messages)
        filename  = f"JARVIS_chat_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        st.download_button(
            label="📄 EXPORT PDF",
            data=pdf_bytes,
            file_name=filename,
            mime="application/pdf",
            use_container_width=True,
        )
    else:
        st.button("📄 EXPORT PDF", disabled=True, use_container_width=True)

# =====================================================
# CONFIG PANEL
# =====================================================

if st.session_state.show_config:
    st.markdown('<div class="config-panel"><div class="config-title">⚙ SYSTEM CONFIGURATION</div>', unsafe_allow_html=True)
    cfg1, cfg2, cfg3 = st.columns([2, 1, 1])

    with cfg1:
        model_display = (st.session_state.selected_model or "None").split("/")[-1]
        st.markdown(f"""
        <div style="padding:6px 0 10px;">
          <div style="font-family:Rajdhani,sans-serif;font-size:0.8rem;letter-spacing:1px;color:rgba(0,180,255,0.65);margin-bottom:5px;">🧬 AUTO-SELECTED MODEL</div>
          <div style="font-family:Courier,monospace;font-size:0.76rem;color:#00d4ff;background:rgba(0,25,65,0.75);border:1px solid rgba(0,180,255,0.28);border-radius:8px;padding:8px 14px;letter-spacing:0.5px;">
            ⚡ {model_display}
          </div>
          <div style="font-family:Rajdhani,sans-serif;font-size:0.7rem;color:rgba(0,180,255,0.38);margin-top:5px;letter-spacing:0.8px;">
            Priority: llama › deepseek › mixtral › firefunction › qwen
          </div>
        </div>
        """, unsafe_allow_html=True)

    with cfg2:
        st.session_state.temperature = st.slider(
            "🌡 Temperature", 0.0, 1.5,
            st.session_state.temperature, 0.1,
            help="Higher = more creative"
        )
    with cfg3:
        st.session_state.max_tokens = st.slider(
            "⚡ Max Tokens", 100, 4096,
            st.session_state.max_tokens, 100,
            help="Max response length"
        )

    st.markdown('</div>', unsafe_allow_html=True)

# =====================================================
# WELCOME SCREEN
# =====================================================

SUGGESTIONS = [
    "🐍 Write a Python web scraper",
    "🧠 Explain transformer architecture",
    "📊 Write a SQL query for sales data",
    "🔧 Debug my Python code",
    "📝 Summarise a research paper",
    "🚀 Build a REST API in FastAPI",
    "💡 Explain reinforcement learning",
    "🗄 Design a database schema",
]

if not st.session_state.messages:
    chips_html = "".join(
        f'<div class="suggestion-chip">{s}</div>' for s in SUGGESTIONS
    )
    st.markdown(f"""
    <div class="welcome-wrap">
      <svg class="welcome-brain" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M32 8C24 8 18 13 17 20C13 20 10 23 10 27C8 28 6 31 7 35C6 38 8 42 12 43C13 47 17 50 22 50C24 52 27 53 32 53C37 53 40 52 42 50C47 50 51 47 52 43C56 42 58 38 57 35C58 31 56 28 54 27C54 23 51 20 47 20C46 13 40 8 32 8Z"
          stroke="#00b4ff" stroke-width="1.5" fill="rgba(0,40,100,0.22)"/>
        <circle cx="32" cy="20" r="2.5" fill="#ff8c00"><animate attributeName="opacity" values="0.3;1;0.3" dur="1.2s" repeatCount="indefinite"/></circle>
        <circle cx="20" cy="31" r="2.5" fill="#00b4ff"><animate attributeName="opacity" values="1;0.3;1" dur="1.4s" repeatCount="indefinite"/></circle>
        <circle cx="44" cy="31" r="2.5" fill="#00b4ff"><animate attributeName="opacity" values="0.3;1;0.3" dur="1.0s" repeatCount="indefinite"/></circle>
        <circle cx="32" cy="42" r="2.5" fill="#ff8c00"><animate attributeName="opacity" values="1;0.3;1" dur="1.6s" repeatCount="indefinite"/></circle>
        <line x1="20" y1="31" x2="32" y2="20" stroke="#00b4ff" stroke-width="0.8"><animate attributeName="opacity" values="0.1;0.8;0.1" dur="1.3s" repeatCount="indefinite"/></line>
        <line x1="44" y1="31" x2="32" y2="42" stroke="#ff8c00" stroke-width="0.8"><animate attributeName="opacity" values="0.8;0.1;0.8" dur="1.5s" repeatCount="indefinite"/></line>
      </svg>
      <div class="welcome-heading">ONLINE · READY</div>
      <div class="welcome-sub">What can I process for you today?</div>
      <div class="suggestions">{chips_html}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    cols = st.columns(4)
    for i, s in enumerate(SUGGESTIONS):
        with cols[i % 4]:
            if st.button(s, key=f"sug_{i}", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": s})
                st.rerun()

# =====================================================
# CHAT HISTORY
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
        thinking_ph  = st.empty()
        thinking_ph.markdown(BRAIN_THINKING_HTML, unsafe_allow_html=True)
        response_ph  = st.empty()
        full_response = ""

        try:
            stream = client.chat.completions.create(
                model=st.session_state.selected_model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    *st.session_state.messages[-20:]
                ],
                temperature=st.session_state.temperature,
                max_tokens=st.session_state.max_tokens,
                stream=True,
            )
            first = True
            for chunk in stream:
                delta = chunk.choices[0].delta.content if chunk.choices else None
                if delta:
                    if first:
                        thinking_ph.empty()
                        first = False
                    full_response += delta
                    response_ph.markdown(full_response + " ▌")
            response_ph.markdown(full_response)

        except Exception as e:
            thinking_ph.empty()
            st.error(f"⚠️ Neural error: {str(e)}")
            full_response = "Sorry, something went wrong. Please try again."
            response_ph.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})
    st.rerun()

# =====================================================
# FOOTER
# =====================================================

st.divider()
st.caption("⚡ JARVIS AI  ·  Neural Intelligence System  ·  Streamlit + Fireworks AI")
