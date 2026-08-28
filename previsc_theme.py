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

def aplicar(pagina: str = "interna") -> None:
    _base.aplicar(pagina)
    if pagina == "interna":
        extra = _CSS_SIDEBAR + _css_ordem("nav_") + _css_ativo()
    else:
        extra = _css_ordem("menu_")
    st.markdown(f"<style>{extra}</style>", unsafe_allow_html=True)
