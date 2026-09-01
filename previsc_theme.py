"""
PREVISC - Camada de layout do menu (ordem fixa + sidebar sempre visivel).
"""
from __future__ import annotations
import re
import streamlit as st
from previsc_base import *  
import previsc_base as _base

ORDEM_MENU = [
    "Simulador Individual",
    "Simulador de Autopatrocínio",
    "Cálculo de Contribuição em Lote",
    "Cálculo de Salário em Lote",
    "Regras e Bases de Cálculo",
]

def _sel(prefixo: str, chave: str) -> str:
    return ".st-key-" + re.sub(r"[^A-Za-z0-9_-]", "-", prefixo + chave)

def _css_ordem(prefixo: str) -> str:
    return ""  

def _css_ativo() -> str:
    atual = st.session_state.get("menu_selecionado", "")
    if atual not in ORDEM_MENU:
        return ""
    return (
        f'section[data-testid="stSidebar"] {_sel("nav_", atual)} button'
        "{border: 2px solid white !important; filter: brightness(1.15) !important; transform: scale(1.02);}"
    )

_CSS_SIDEBAR = """
section[data-testid="stSidebar"]{
  display:block!important; visibility:visible!important;
  transform:none!important; margin-left:0!important;
  min-width:320px!important; width:320px!important;
}
[data-testid="stSidebarCollapsedControl"],
[data-testid="stSidebarCollapseButton"]{display:none!important;}
section[data-testid="stSidebar"] .stButton > button:hover{filter:brightness(1.08);}
"""


_CSS_SUAVE = """
/* 1. Overlay mais suave sobre as fotos */
.pv-capa-bg{background-blend-mode:soft-light,normal!important;}
.pv-capa::after{content:"";position:absolute;inset:0;z-index:1;
  background:linear-gradient(180deg,rgba(8,12,40,.10) 0%,rgba(8,12,40,.34) 100%);}
.pv-capa-conteudo{z-index:2;}

/* 2. Subtitulo do logo legivel */
.pv-logo .pv-logo-sub{font-size:.74rem!important;letter-spacing:1.4px!important;
  color:rgba(255,255,255,.92)!important;margin-top:.35rem!important;}
"""

_CSS_MENU_SUAVE = """
.stApp{background-blend-mode:soft-light,normal!important;}
.st-key-pv_menu_card .pv-logo .pv-logo-nome{
  background:linear-gradient(90deg,#0b8ad1 0%,#5a19c9 100%);
  -webkit-background-clip:text;background-clip:text;color:transparent;}
.st-key-pv_menu_card .pv-logo .pv-logo-sub{color:#4a4a63!important;}
"""

_CSS_INTERNA_CLARA = """
/* 3. Area de conteudo clara (protótipo pagina 3) */
.stApp .stMainBlockContainer, .stApp .block-container{
  background:#ffffff; border-radius:26px; padding:2.4rem 2.6rem 2.6rem!important;
  margin-top:1.6rem; margin-bottom:2rem;
  box-shadow:0 26px 60px rgba(10,10,40,.22);
}
section.main h1, section.main h2, section.main h3,
.stMainBlockContainer h1, .stMainBlockContainer h2, .stMainBlockContainer h3{
  color:#1B365D!important;-webkit-text-fill-color:#1B365D!important;text-shadow:none!important;}
.stMainBlockContainer p, .stMainBlockContainer label, .stMainBlockContainer li,
.stMainBlockContainer [data-testid="stMarkdownContainer"]{color:#2b2b3d!important;}
.stMainBlockContainer small, .stMainBlockContainer [data-testid="stCaptionContainer"]{color:#6b6b80!important;}
.stMainBlockContainer .stRadio label p, .stMainBlockContainer .stCheckbox label p{color:#2b2b3d!important;}
.stMainBlockContainer hr{border-top:1px solid rgba(27,54,93,.18)!important;}
.stMainBlockContainer .stTextInput input, .stMainBlockContainer .stNumberInput input,
.stMainBlockContainer div[data-baseweb="select"] > div{
  border:1px solid #d8dce8!important; box-shadow:none!important;}
.stMainBlockContainer .stTabs [data-baseweb="tab-list"]{border-bottom:1px solid rgba(27,54,93,.18);}
.stMainBlockContainer .stTabs [data-baseweb="tab"]{background:#eef1f7;color:#1B365D;}
.stMainBlockContainer .stTabs [aria-selected="true"]{background:#dbe3f3!important;}
.stMainBlockContainer [data-testid="stMetric"]{background:#f3f5fa;border:1px solid #e2e6f0;}
.stMainBlockContainer [data-testid="stMetricValue"],
.stMainBlockContainer [data-testid="stMetricLabel"]{color:#1B365D!important;}

/* 4. Sidebar branca com textos escuros */
section[data-testid="stSidebar"] > div:first-child{background:#ffffff!important;
  box-shadow:0 26px 60px rgba(10,10,40,.22)!important;}
section[data-testid="stSidebar"] .pv-logo .pv-logo-nome{
  background:linear-gradient(90deg,#0b8ad1 0%,#5a19c9 100%);
  -webkit-background-clip:text;background-clip:text;color:transparent;}
section[data-testid="stSidebar"] .pv-logo .pv-logo-sub{color:#4a4a63!important;}
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p{color:#5a5a70!important;}
section[data-testid="stSidebar"] .stButton > button{
  background:#f1f3f9!important;color:#1B365D!important;box-shadow:none!important;
  border:1px solid #e0e4ee!important;}
section[data-testid="stSidebar"] .stButton > button [data-testid="stMarkdownContainer"] p{
  color:#1B365D!important;}
section[data-testid="stSidebar"] .stButton > button:hover{
  background:#e6ebf7!important;transform:none;}

/* 5. Sem sobra de gradiente no fim da pagina */
.stApp{background-attachment:fixed,fixed!important;}
"""

def _css_ativo_claro() -> str:
    atual = st.session_state.get("menu_selecionado", "")
    if atual not in ORDEM_MENU:
        return ""
    return (
        f'section[data-testid="stSidebar"] {_sel("nav_", atual)} button'
        "{background:linear-gradient(100deg,#00B34A 0%,#1E6BFF 45%,#8B12D6 100%)!important;"
        "border:none!important;}"
        f'section[data-testid="stSidebar"] {_sel("nav_", atual)} button '
        '[data-testid="stMarkdownContainer"] p{color:#ffffff!important;}'
    )

def aplicar(pagina: str = "interna") -> None:
    _base.aplicar(pagina)
    if pagina == "interna":
        extra = (_CSS_SIDEBAR + _CSS_SUAVE + _CSS_INTERNA_CLARA
                 + _css_ordem("nav_") + _css_ativo_claro())
    else:
        extra = _CSS_SUAVE + _CSS_MENU_SUAVE + _css_ordem("menu_")
    st.markdown(f"<style>{extra}</style>", unsafe_allow_html=True)
