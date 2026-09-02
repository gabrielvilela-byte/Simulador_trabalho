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

def aplicar(pagina: str = "interna") -> None:
    _base.aplicar(pagina)
    if pagina == "interna":
        extra = _CSS_SIDEBAR + _css_ordem("nav_") + _css_ativo()
    else:
        extra = _CSS_SUAVE + _CSS_MENU_SUAVE + _css_ordem("menu_")
    st.markdown(f"<style>{extra}</style>", unsafe_allow_html=True)
