"""
PREVISC - Tema visual (layout do protótipo) para o app Streamlit.
"""
from __future__ import annotations
import base64
from pathlib import Path
import streamlit as st

VERDE = "#00B34A"
VERDE_CLARO = "#3ED18A"
CIANO = "#00E5FF"
AZUL = "#1E6BFF"
ROXO = "#8B12D6"
ROXO_CLARO = "#B14BFF"

_ASSETS = Path(__file__).parent / "assets"

def _b64(nome: str) -> str | None:
    caminho = _ASSETS / nome
    if not caminho.exists():
        return None
    return base64.b64encode(caminho.read_bytes()).decode()

def _bg_layer(nome: str, gradiente: str) -> str:
    img = _b64(nome)
    if img:
        return f"{gradiente}, url('data:image/jpeg;base64,{img}')"
    return gradiente

_ONDAS = """
<svg class="pv-ondas" viewBox="0 0 1600 900" preserveAspectRatio="none"
     xmlns="http://www.w3.org/2000/svg">
  <g fill="none" stroke-linecap="round">
    <path d="M1180,-40 C1520,120 1660,430 1610,900" stroke="#00E5FF"
          stroke-width="6" opacity=".85"/>
    <path d="M1240,-40 C1580,140 1720,450 1670,900" stroke="#3ED18A"
          stroke-width="5" opacity=".7"/>
    <path d="M1300,-40 C1640,160 1780,470 1730,900" stroke="#B14BFF"
          stroke-width="4" opacity=".6"/>
    <path d="M-260,940 C-40,600 220,430 560,470" stroke="#00E5FF"
          stroke-width="6" opacity=".8"/>
    <path d="M-300,1000 C-60,640 220,470 600,520" stroke="#3ED18A"
          stroke-width="5" opacity=".6"/>
  </g>
</svg>
"""

def aplicar(pagina: str = "interna") -> None:
    fundo_interno = (
            "linear-gradient(115deg, rgba(0,179,74,.96) 0%, "
            "rgba(0,200,180,.94) 26%, rgba(30,107,255,.92) 58%, "
            "rgba(139,18,214,.94) 100%)"
    )

    st.markdown(
        f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,400;0,600;0,700;0,800;1,700;1,800;1,900&display=swap');

html, body, [class*="css"], .stApp {{ font-family: 'Montserrat', sans-serif; }}

.stApp {{
  background: {fundo_interno};
  background-size: cover, cover;
  background-position: center, right center;
  background-attachment: fixed, fixed;
  background-blend-mode: multiply, normal;
}}

header[data-testid="stHeader"] {{ background: transparent; }}
#MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"] {{ display: none !important; }}

.stMainBlockContainer, .block-container {{
  padding-top: 2.2rem;
  padding-bottom: 4rem;
  max-width: 1180px;
}}

.stApp h1 {{
  font-style: italic; font-weight: 900; letter-spacing: -.5px;
  color: {VERDE_CLARO};
  text-shadow: 0 2px 14px rgba(0,0,0,.18);
}}
.stApp h2, .stApp h3 {{ font-style: italic; font-weight: 800; color: #ffffff; }}
.stApp p, .stApp label, .stApp li,
.stApp [data-testid="stMarkdownContainer"] {{ color: rgba(255,255,255,.94); }}
.stApp small, .stCaption, [data-testid="stCaptionContainer"] {{ color: rgba(255,255,255,.78) !important; }}

.stTextInput input, .stNumberInput input, .stDateInput input,
div[data-baseweb="select"] > div {{
  background: #ffffff !important;
  border: none !important;
  border-radius: 8px !important;
  color: #1b1b2b !important;
  font-weight: 600;
  box-shadow: 0 6px 18px rgba(0,0,0,.12);
  min-height: 44px;
}}
div[data-baseweb="select"] svg {{ color: #1b1b2b !important; }}
.stTextInput input::placeholder, .stNumberInput input::placeholder {{ color: #8b8ba0 !important; }}

.stRadio label p, .stCheckbox label p {{ color: #fff !important; font-weight: 600; }}

.stTabs [data-baseweb="tab-list"] {{ gap: .35rem; border-bottom: 1px solid rgba(255,255,255,.35); }}
.stTabs [data-baseweb="tab"] {{
  background: rgba(255,255,255,.14); border-radius: 8px 8px 0 0;
  padding: .45rem 1rem; color: #fff; font-weight: 700; font-size: .84rem;
}}
.stTabs [aria-selected="true"] {{ background: rgba(255,255,255,.32) !important; }}

.stButton > button, .stDownloadButton > button, .stFormSubmitButton > button {{
  background: linear-gradient(100deg, {VERDE} 0%, {AZUL} 45%, {ROXO} 100%) !important;
  color: #fff !important; border: none; border-radius: 12px;
  padding: .65rem 1.6rem; font-weight: 800; font-style: italic; letter-spacing: .2px;
  box-shadow: 0 10px 24px rgba(0,0,0,.22);
  transition: transform .15s ease, filter .15s ease;
}}
.stButton > button [data-testid="stMarkdownContainer"] p,
.stDownloadButton > button [data-testid="stMarkdownContainer"] p,
.stFormSubmitButton > button [data-testid="stMarkdownContainer"] p {{
  color: #ffffff !important; font-weight: 800 !important;
}}
.stButton > button:hover, .stDownloadButton > button:hover,
.stFormSubmitButton > button:hover {{
  transform: translateY(-2px); filter: brightness(1.08); color: #fff !important;
}}

[data-testid="stFileUploaderDropzone"] {{
  background: rgba(255,255,255,.92); border: 2px dashed rgba(30,107,255,.45); border-radius: 14px;
}}
[data-testid="stFileUploaderDropzone"] * {{ color: #24243a !important; }}

[data-testid="stDataFrame"], [data-testid="stTable"] {{
  background: #fff; border-radius: 14px; overflow: hidden; box-shadow: 0 12px 30px rgba(0,0,0,.18);
}}

[data-testid="stMetric"] {{
  background: rgba(255,255,255,.14); border: 1px solid rgba(255,255,255,.25);
  border-radius: 14px; padding: 1rem 1.1rem; backdrop-filter: blur(6px);
}}
[data-testid="stMetricValue"], [data-testid="stMetricLabel"] {{ color: #fff !important; }}
.stAlert {{ border-radius: 12px; }}

/* ---------- SIDEBAR: cartão escuro flutuante com fonte branca ---------- */
section[data-testid="stSidebar"] {{
  background: transparent; padding: 1.1rem .8rem 1.1rem 1.1rem;
}}
section[data-testid="stSidebar"] > div:first-child {{
  background: transparent; 
}}
section[data-testid="stSidebar"] .stButton > button {{
  width: 100%; margin-bottom: 0.5rem; padding: 0.8rem 0.5rem; font-size: 0.9rem;
}}
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {{
  color: #ffffff !important; font-size: .85rem; line-height: 1.45; /* FONTE BRANCA */
}}
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {{ gap: .2rem; }}

.pv-logo {{ text-align: center; padding: 1.4rem 0 1.1rem; }}
.pv-logo .pv-logo-nome {{
  font-style: italic; font-weight: 900; font-size: 2.2rem; letter-spacing: -1px;
  color: #ffffff !important; line-height: 1; text-shadow: none;
  background: none; -webkit-text-fill-color: #ffffff;
}}
.pv-logo .pv-logo-sub {{
  font-style: italic; font-weight: 800; font-size: .58rem; letter-spacing: .6px;
  color: {CIANO}; margin-top: .1rem; /* Subtitulo do logo em ciano */
}}

.pv-ondas-capa {{ position: absolute !important; width: 100% !important; height: 100% !important; z-index: 1; opacity: .95; }}
.pv-ondas {{ position: fixed; inset: 0; width: 100vw; height: 100vh; pointer-events: none; z-index: 0; opacity: .9; }}
.stApp > div {{ position: relative; z-index: 1; }}

.pv-capa {{
  position: relative; width: 100vw; margin-left: calc(50% - 50vw);
  aspect-ratio: auto; height: 86vh; min-height: 460px;
  display: flex; flex-direction: column; align-items: center; justify-content: center; overflow: hidden;
}}
.pv-capa-bg {{ position: absolute; inset: 0; background-size: cover; background-position: center; background-blend-mode: multiply, normal; }}
.pv-capa-conteudo {{ position: relative; z-index: 2; text-align: center; padding: 0 5vw; }}
.stApp .pv-capa-titulo {{
  font-style: italic; font-weight: 900; color: #fff !important; text-transform: uppercase;
  font-size: clamp(3.5rem, 14vw, 13rem); line-height: .92;
  letter-spacing: -.03em; text-shadow: 0 8px 40px rgba(0,0,0,.28); margin: 0;
}}
.pv-capa-frase {{
  margin-top: clamp(1.5rem, 6vh, 4rem); font-style: italic; font-weight: 700; color: #fff; font-size: clamp(.95rem, 2.1vw, 1.65rem);
}}
.pv-capa-sub {{
  margin-top: .35rem; font-style: italic; font-weight: 500;
  color: rgba(255,255,255,.9); font-size: clamp(.75rem, 1.3vw, 1rem);
}}
.st-key-pv_cta_box {{ margin-top: -7rem; display: flex; justify-content: center; position: relative; z-index: 3; }}
.st-key-pv_cta_box .stButton > button {{ padding: .5rem 1.6rem; font-size: .95rem; border-radius: 10px; }}

.st-key-pv_menu_card {{
  background: #f6f6f4; border-radius: 26px; padding: 2.4rem 2.2rem 1.6rem;
  box-shadow: 0 30px 70px rgba(10,10,40,.35); margin-top: 7vh; margin-bottom: 4vh;
}}
.st-key-pv_menu_card [data-testid="stMarkdownContainer"] p {{ color: #6d6d7a !important; font-size: .8rem; line-height: 1.5; }}
.st-key-pv_menu_card .stButton > button {{ margin-bottom: .45rem; }}

@media (max-width: 780px) {{
  .pv-capa {{ aspect-ratio: auto; min-height: 78vh; }}
  .block-container {{ padding-left: 1rem; padding-right: 1rem; }}
}}
</style>
{_ONDAS}
""",
        unsafe_allow_html=True,
    )

    if pagina == "capa":
        st.markdown(
            "<style>.block-container{padding-top:0!important;max-width:100%!important;}"
            "section[data-testid='stSidebar']{display:none;}</style>",
            unsafe_allow_html=True,
        )

def logo_sidebar() -> None:
    st.markdown(
        '<div class="pv-logo">'
        '<div class="pv-logo-nome">PREVISC</div>'
        '<div class="pv-logo-sub">PREVIDÊNCIA COMPLEMENTAR</div>'
        "</div>",
        unsafe_allow_html=True,
    )

def fundo_menu() -> None:
    fundo = _bg_layer("hero-menu.jpg", "linear-gradient(100deg, rgba(0,179,74,.97) 0%, rgba(0,196,180,.95) 28%, rgba(30,107,255,.86) 58%, rgba(139,18,214,.80) 100%)")
    st.markdown(
        f"<style>.stApp{{background:{fundo}!important;background-size:cover,cover!important;background-position:center,right center!important;}}</style>",
        unsafe_allow_html=True,
    )

def capa(titulo: str = "PREVISC", frase: str = "Planeje hoje o futuro que quer viver amanhã.", subfrase: str = "Quer saber quanto investir para chegar lá?", rotulo_botao: str = "Calcule agora") -> bool:
    fundo = _bg_layer("hero-home.jpg", "linear-gradient(105deg, rgba(0,179,74,.72) 0%, rgba(0,190,190,.62) 30%, rgba(30,107,255,.62) 62%, rgba(139,18,214,.78) 100%)")
    st.markdown(
        f"""
<div class="pv-capa">
  <div class="pv-capa-bg" style="background-image:{fundo};"></div>
  {_ONDAS.replace('class="pv-ondas"', 'class="pv-ondas pv-ondas-capa"')}
  <div class="pv-capa-conteudo">
    <h1 class="pv-capa-titulo">{titulo}</h1>
    <div class="pv-capa-frase">{frase}</div>
    <div class="pv-capa-sub">{subfrase}</div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )
    # O botão de Calcule Agora é renderizado pela própria Home no app.py
    return False

def titulo_pagina(texto: str, descricao: str = "") -> None:
    st.markdown(
        f"<h1 style='color:#fff;-webkit-text-fill-color:#fff;text-shadow:0 2px 10px rgba(0,0,0,.25);'>{texto}</h1>",
        unsafe_allow_html=True,
    )
    if descricao:
        st.markdown(f"<p style='max-width:52ch;font-size:.9rem;'>{descricao}</p>", unsafe_allow_html=True)
    st.markdown("<hr style='border:none;border-top:1px solid rgba(255,255,255,.3);margin:1.1rem 0 1.4rem;'>", unsafe_allow_html=True)

def rodape_sidebar(texto: str = "Sistema interno desenvolvido pela equipe de Arrecadação para processar cálculos previdenciários (individuais e em lote) de Participantes Ativos e Autopatrocinados, integrado à consulta rápida das regras vigentes.") -> None:
    st.markdown(
        f"<div style='padding:1.6rem 1rem 1.4rem;'><p style='color:#ffffff;font-size:.85rem;line-height:1.45;margin:0;'>{texto}</p></div>",
        unsafe_allow_html=True,
    )
