import base64, streamlit as st
from pathlib import Path

st.set_page_config(page_title="Previsc", layout="wide", initial_sidebar_state="expanded")

def b64(path):
    return base64.b64encode(Path(path).read_bytes()).decode()

HERO = b64("image_97db40.png")
HERO_RATIO = 1920 / 1080          # ajuste para a proporção real do arquivo
BTN = dict(top=62, left=8, w=18, h=7)   # % do botão desenhado dentro da imagem

st.markdown(f"""
<style>
/* ---------- 1. ZERAR PADDINGS ---------- */
[data-testid="stAppViewBlockContainer"],
.block-container {{
    padding: 0 !important;
    max-width: 100% !important;
}}
[data-testid="stHeader"] {{ background: transparent; height: 0; }}
[data-testid="stToolbar"] {{ right: 1rem; }}
footer, #MainMenu {{ visibility: hidden; }}
[data-testid="stVerticalBlock"] {{ gap: 0 !important; }}

/* ---------- 2. HERO FULL-BLEED ---------- */
.hero {{
    position: relative;
    width: 100%;
    aspect-ratio: {HERO_RATIO};
    background-image: url("data:image/png;base64,{HERO}");
    background-size: cover;
    background-position: center;
}}

/* ---------- 3. BOTÃO INVISÍVEL SOBREPOSTO ---------- */
.hero-wrap {{ position: relative; }}
.hero-wrap [data-testid="stButton"] {{
    position: absolute;
    top: {BTN['top']}%;
    left: {BTN['left']}%;
    width: {BTN['w']}%;
    height: {BTN['h']}%;
    margin: 0 !important;
    z-index: 10;
}}
.hero-wrap [data-testid="stButton"] > button {{
    width: 100%; height: 100%;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: transparent !important;
    cursor: pointer;
}}

/* ---------- 4. SIDEBAR ---------- */
[data-testid="stSidebar"] > div:first-child {{
    background: linear-gradient(180deg, #1B365D 0%, #4B2E83 100%);
}}
[data-testid="stSidebar"] * {{ color: #FFFFFF !important; }}
[data-testid="stSidebar"] [role="radiogroup"] label {{
    padding: .45rem .6rem; border-radius: 8px;
}}
[data-testid="stSidebar"] [role="radiogroup"] label:hover {{
    background: rgba(255,255,255,.12);
}}
</style>
""", unsafe_allow_html=True)

# ---- render ----
st.markdown('<div class="hero-wrap"><div class="hero"></div>', unsafe_allow_html=True)
clicou = st.button("Calcule agora", key="hero_cta")
st.markdown('</div>', unsafe_allow_html=True)

if clicou:
    st.session_state.pagina = "Simulador"
    st.rerun()
