"""
PREVISC - Tema visual (layout do protótipo) para o app Streamlit.

Como usar (mínima interferência no seu código):

    import previsc_theme as tema

    st.set_page_config(page_title="Previsc", layout="wide",
                       initial_sidebar_state="expanded")
    tema.aplicar()                      # 1 linha: aplica todo o CSS

    # Na tela de capa (opcional):
    if tema.capa():                     # desenha a capa e retorna True se clicou
        st.session_state.pagina = "menu"
        st.rerun()

    # Na sidebar, no lugar do título:
    tema.logo_sidebar()

Coloque os arquivos 'hero-home.jpg' e 'hero-menu.jpg' numa pasta 'assets/'
ao lado deste arquivo. Se eles não existirem, o tema cai automaticamente
num fundo só de gradiente (sem quebrar nada).
"""

from __future__ import annotations

import base64
from pathlib import Path

import streamlit as st

# --------------------------------------------------------------------------
# Paleta do protótipo
# --------------------------------------------------------------------------
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
    """Monta o valor de background: gradiente sobre a foto (se existir)."""
    img = _b64(nome)
    if img:
        return f"{gradiente}, url('data:image/jpeg;base64,{img}')"
    return gradiente


# --------------------------------------------------------------------------
# Ondas decorativas (SVG inline, escalam sozinhas)
# --------------------------------------------------------------------------
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


# --------------------------------------------------------------------------
# CSS principal
# --------------------------------------------------------------------------
def aplicar(pagina: str = "interna") -> None:
    """Injeta o tema. pagina='capa' remove padding do topo para o full-bleed."""

    fundo_interno = (
            "linear-gradient(115deg, rgba(0,179,74,.96) 0%, "
            "rgba(0,200,180,.94) 26%, rgba(30,107,255,.92) 58%, "
            "rgba(139,18,214,.94) 100%)"
    )

    st.markdown(
        f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,400;0,600;0,700;0,800;1,700;1,800;1,900&display=swap');

/* ---------- base ---------- */
html, body, [class*="css"], .stApp {{ font-family: 'Montserrat', sans-serif; }}

.stApp {{
  background: {fundo_interno};
  background-size: cover, cover;
  background-position: center, right center;
  background-attachment: fixed, fixed;
  background-blend-mode: multiply, normal;
}}

/* esconde cabeçalho/rodapé padrão do Streamlit */
header[data-testid="stHeader"] {{ background: transparent; }}
#MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"] {{ display: none !important; }}

/* área de conteúdo mais larga e colada no topo */
.stMainBlockContainer, .block-container {{
  padding-top: 2.2rem;
  padding-bottom: 4rem;
  max-width: 1180px;
}}

/* ---------- textos ---------- */
.stApp h1 {{
  font-style: italic; font-weight: 900; letter-spacing: -.5px;
  color: {VERDE_CLARO};
  text-shadow: 0 2px 14px rgba(0,0,0,.18);
}}
.stApp h2, .stApp h3 {{
  font-style: italic; font-weight: 800; color: #ffffff;
}}
.stApp p, .stApp label, .stApp li,
.stApp [data-testid="stMarkdownContainer"] {{ color: rgba(255,255,255,.94); }}
.stApp small, .stCaption, [data-testid="stCaptionContainer"] {{
  color: rgba(255,255,255,.78) !important;
}}

/* ---------- inputs ---------- */
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
.stTextInput input::placeholder, .stNumberInput input::placeholder {{
  color: #8b8ba0 !important;
}}

/* radio / checkbox em branco */
.stRadio label p, .stCheckbox label p {{ color: #fff !important; font-weight: 600; }}

/* ---------- abas ---------- */
.stTabs [data-baseweb="tab-list"] {{
  gap: .35rem; border-bottom: 1px solid rgba(255,255,255,.35);
}}
.stTabs [data-baseweb="tab"] {{
  background: rgba(255,255,255,.14);
  border-radius: 8px 8px 0 0;
  padding: .45rem 1rem; color: #fff; font-weight: 700; font-size: .84rem;
}}
.stTabs [aria-selected="true"] {{ background: rgba(255,255,255,.32) !important; }}

/* ---------- botões (gradiente do protótipo) ---------- */
.stButton > button, .stDownloadButton > button, .stFormSubmitButton > button {{
  background: linear-gradient(100deg, {VERDE} 0%, {AZUL} 45%, {ROXO} 100%);
  color: #fff !important;
  border: none; border-radius: 12px;
  padding: .65rem 1.6rem;
  font-weight: 800; font-style: italic; letter-spacing: .2px;
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

/* ---------- upload ---------- */
[data-testid="stFileUploaderDropzone"] {{
  background: rgba(255,255,255,.92);
  border: 2px dashed rgba(30,107,255,.45);
  border-radius: 14px;
}}
[data-testid="stFileUploaderDropzone"] * {{ color: #24243a !important; }}

/* ---------- tabelas / dataframes ---------- */
[data-testid="stDataFrame"], [data-testid="stTable"] {{
  background: #fff; border-radius: 14px; overflow: hidden;
  box-shadow: 0 12px 30px rgba(0,0,0,.18);
}}

/* ---------- métricas e alertas ---------- */
[data-testid="stMetric"] {{
  background: rgba(255,255,255,.14);
  border: 1px solid rgba(255,255,255,.25);
  border-radius: 14px; padding: 1rem 1.1rem;
  backdrop-filter: blur(6px);
}}
[data-testid="stMetricValue"], [data-testid="stMetricLabel"] {{ color: #fff !important; }}
.stAlert {{ border-radius: 12px; }}

/* ---------- SIDEBAR: cartão branco flutuante ---------- */
section[data-testid="stSidebar"] {{
  background: transparent;
  padding: 1.1rem .8rem 1.1rem 1.1rem;
}}
section[data-testid="stSidebar"] > div:first-child {{
  background: #f6f6f4;
  border-radius: 22px;
  box-shadow: 0 26px 60px rgba(10,10,40,.35);
  overflow: hidden;
}}
section[data-testid="stSidebar"] .stButton > button {{
  width: 100%;
  border-radius: 0;
  padding: .58rem .5rem;
  font-size: .86rem;
  box-shadow: none;
  border-bottom: 1px solid rgba(255,255,255,.35);
  color: #ffffff !important;
  font-weight: 700 !important;
  text-shadow: 0 1px 3px rgba(0,0,0,.35);
}}
section[data-testid="stSidebar"] .stButton > button p {{
  color: #ffffff !important; font-weight: 700 !important;
}}
section[data-testid="stSidebar"] .stButton > button:hover {{ transform: none; }}
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {{
  color: #6d6d7a !important; font-size: .78rem; line-height: 1.45;
}}
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {{ gap: .2rem; }}

/* logo Previsc na sidebar */
.pv-logo {{ text-align: center; padding: 1.4rem 0 1.1rem; }}
.pv-logo .pv-logo-nome {{
  font-style: italic; font-weight: 900; font-size: 2rem; letter-spacing: -1px;
  background: linear-gradient(90deg, {VERDE} 0%, {AZUL} 70%, {ROXO} 100%);
  -webkit-background-clip: text; background-clip: text; color: transparent;
  line-height: 1;
}}
.pv-logo .pv-logo-sub {{
  font-style: italic; font-weight: 800; font-size: .58rem; letter-spacing: .6px;
  color: {VERDE}; margin-top: .1rem;
}}

/* ---------- ondas decorativas ---------- */
.pv-ondas-capa {{ position: absolute !important; width: 100% !important; height: 100% !important; z-index: 1; opacity: .95; }}
.pv-ondas {{
  position: fixed; inset: 0; width: 100vw; height: 100vh;
  pointer-events: none; z-index: 0; opacity: .9;
}}
.stApp > div {{ position: relative; z-index: 1; }}

/* ---------- CAPA full-bleed ---------- */
.pv-capa {{
  position: relative;
  width: 100vw; margin-left: calc(50% - 50vw);
  aspect-ratio: auto; height: 86vh; min-height: 460px;
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  overflow: hidden;
}}
.pv-capa-bg {{
  position: absolute; inset: 0;
  background-size: cover; background-position: center;
  background-blend-mode: multiply, normal;
}}
.pv-capa-conteudo {{ position: relative; z-index: 2; text-align: center; padding: 0 5vw; }}
.stApp .pv-capa-titulo {{
  font-style: italic; font-weight: 900; color: #fff !important;
  text-transform: uppercase;
  font-size: clamp(3.5rem, 14vw, 13rem); line-height: .92;
  letter-spacing: -.03em; text-shadow: 0 8px 40px rgba(0,0,0,.28);
  margin: 0;
}}
.pv-capa-frase {{
  margin-top: clamp(1.5rem, 6vh, 4rem);
  font-style: italic; font-weight: 700; color: #fff;
  font-size: clamp(.95rem, 2.1vw, 1.65rem);
}}
.pv-capa-sub {{
  margin-top: .35rem; font-style: italic; font-weight: 500;
  color: rgba(255,255,255,.9); font-size: clamp(.75rem, 1.3vw, 1rem);
}}
/* o botão real do Streamlit, reposicionado sob a capa */
.st-key-pv_cta_box {{ margin-top: -7rem; display: flex; justify-content: center; position: relative; z-index: 3; }}
.st-key-pv_cta_box .stButton > button {{ padding: .5rem 1.6rem; font-size: .95rem; border-radius: 10px; }}

/* ---------- cartão central do MENU ---------- */
.st-key-pv_menu_card {{
  background: #f6f6f4;
  border-radius: 26px;
  padding: 2.4rem 2.2rem 1.6rem;
  box-shadow: 0 30px 70px rgba(10,10,40,.35);
  margin-top: 7vh; margin-bottom: 4vh;
}}
.st-key-pv_menu_card [data-testid="stMarkdownContainer"] p {{
  color: #6d6d7a !important; font-size: .8rem; line-height: 1.5;
}}
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


# --------------------------------------------------------------------------
# Componentes prontos
# --------------------------------------------------------------------------
def logo_sidebar() -> None:
    """Logo PREVISC no topo da sidebar."""
    st.markdown(
        '<div class="pv-logo">'
        '<div class="pv-logo-nome">PREVISC</div>'
        '<div class="pv-logo-sub">PREVIDÊNCIA COMPLEMENTAR</div>'
        "</div>",
        unsafe_allow_html=True,
    )


def fundo_menu() -> None:
    """Fundo da tela de menu: foto da direita sobre o gradiente."""
    fundo = _bg_layer(
        "hero-menu.jpg",
        (
            "linear-gradient(100deg, rgba(0,179,74,.97) 0%, "
            "rgba(0,196,180,.95) 28%, rgba(30,107,255,.86) 58%, "
            "rgba(139,18,214,.80) 100%)"
        ),
    )
    st.markdown(
        f"<style>.stApp{{background:{fundo}!important;"
        "background-size:cover,cover!important;"
        "background-position:center,right center!important;}</style>",
        unsafe_allow_html=True,
    )


def capa(
    titulo: str = "PREVISC",
    frase: str = "Planeje hoje o futuro que quer viver amanhã.",
    subfrase: str = "Quer saber quanto investir para chegar lá?",
    rotulo_botao: str = "Calcule agora",
) -> bool:
    """Desenha a capa full-width. Retorna True quando o usuário clica no CTA."""
    fundo = _bg_layer(
        "hero-home.jpg",
        (
            "linear-gradient(105deg, rgba(0,179,74,.72) 0%, "
            "rgba(0,190,190,.62) 30%, rgba(30,107,255,.62) 62%, "
            "rgba(139,18,214,.78) 100%)"
        ),
    )
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
    caixa = st.container(key="pv_cta_box")
    with caixa:
        col_a, col_b, col_c = st.columns([2, 1, 2])
        with col_b:
            clicou = st.button(rotulo_botao, key="pv_cta", use_container_width=True)
    return clicou


def titulo_pagina(texto: str, descricao: str = "") -> None:
    """Cabeçalho padrão das páginas internas (título verde + descrição)."""
    st.markdown(
        f"<h1 style='color:#fff;-webkit-text-fill-color:#fff;"
        f"text-shadow:0 2px 10px rgba(0,0,0,.25);'>{texto}</h1>",
        unsafe_allow_html=True,
    )
    if descricao:
        st.markdown(
            f"<p style='max-width:52ch;font-size:.9rem;'>{descricao}</p>",
            unsafe_allow_html=True,
        )
    st.markdown(
        "<hr style='border:none;border-top:1px solid rgba(255,255,255,.3);"
        "margin:1.1rem 0 1.4rem;'>",
        unsafe_allow_html=True,
    )


def rodape_sidebar(
    texto: str = (
        "Sistema interno desenvolvido pela equipe de Arrecadação para processar "
        "cálculos previdenciários (individuais e em lote) de Participantes Ativos "
        "e Autopatrocinados, integrado à consulta rápida das regras vigentes."
    ),
) -> None:
    st.markdown(
        f"<div style='padding:1.6rem 1rem 1.4rem;'>"
        f"<p style='color:#6d6d7a;font-size:.78rem;line-height:1.45;margin:0;'>{texto}</p>"
        f"</div>",
        unsafe_allow_html=True,
    )
