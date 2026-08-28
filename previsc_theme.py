"""
PREVISC - Camada de layout do menu (ordem fixa + sidebar sempre visivel).

Reexporta tudo de `previsc_base.py` (tema visual) e acrescenta:
  * ordem unica dos itens do menu (cartao central e sidebar);
  * sidebar sempre visivel nas telas internas, como no prototipo;
  * destaque do item ativo.
"""

from __future__ import annotations

import re

import streamlit as st

from previsc_base import *  # noqa: F401,F403
import previsc_base as _base

# ordem oficial dos itens (de cima para baixo)
ORDEM_MENU = [
    "Simulador Individual",
    "Simulador de Autopatrocínio",
    "Cálculo de Contribuição em Lote",
    "Cálculo de Salário em Lote",
    "Regras e Bases de Cálculo",
]


def _sel(prefixo: str, chave: str) -> str:
    """Classe CSS que o Streamlit cria a partir da key do botao."""
    return ".st-key-" + re.sub(r"[^A-Za-z0-9_-]", "-", prefixo + chave)


def _css_ordem(prefixo: str) -> str:
    return ""  # ordem agora vem da lista PAGINAS no app
    regras = [
        'section[data-testid="stSidebar"] [data-testid="stVerticalBlock"],'
        " .st-key-pv_menu_card{display:flex;flex-direction:column;}"
        'section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] > *:first-child,'
        " .st-key-pv_menu_card > *:first-child{order:0;}"
        'section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] > *:last-child,'
        " .st-key-pv_menu_card > *:last-child{order:30;}"
    ]
    for i, chave in enumerate(ORDEM_MENU):
        regras.append(f"{_sel(prefixo, chave)}{{order:{i + 2};}}")
    regras.append(".st-key-nav_home{order:20;}")
    return "".join(regras)


def _css_ativo() -> str:
    atual = st.session_state.get("menu_selecionado", "")
    if atual not in ORDEM_MENU:
        return ""
    return (
        f'section[data-testid="stSidebar"] {_sel("nav_", atual)} button'
        "{background:linear-gradient(90deg,#1E6BFF 0%,#8B12D6 100%)!important;}"
    )


_CSS_SIDEBAR = """
section[data-testid="stSidebar"]{
  display:block!important; visibility:visible!important;
  transform:none!important; margin-left:0!important;
  min-width:310px!important; width:310px!important;
}
[data-testid="stSidebarCollapsedControl"],
[data-testid="stSidebarCollapseButton"]{display:none!important;}
section[data-testid="stSidebar"] .stButton > button{
  background:linear-gradient(90deg,#00C2A8 0%,#16A6D9 100%)!important;
}
section[data-testid="stSidebar"] .stButton > button:hover{filter:brightness(1.08);}
"""


def aplicar(pagina: str = "interna") -> None:
    """Aplica o tema base e, por cima, as regras de menu/sidebar."""
    _base.aplicar(pagina)
    if pagina == "interna":
        extra = _CSS_SIDEBAR + _css_ordem("nav_") + _css_ativo()
    else:
        extra = _css_ordem("menu_")
    st.markdown(f"<style>{extra}</style>", unsafe_allow_html=True)
