# Previsc — aplicar o novo layout (3 passos)

O motor de cálculo em Python **não muda nada**. Só o visual.

## Passo 1 — copiar os arquivos

Na pasta do seu projeto Streamlit:

```
seu_projeto/
├── app.py                  (o seu arquivo principal, já existente)
├── previsc_theme.py        <-- NOVO (baixe daqui)
└── assets/
    ├── hero-home.jpg       <-- NOVO (capa)
    └── hero-menu.jpg       <-- NOVO (fundo das páginas)
```

Se você não criar a pasta `assets/`, o tema funciona igual — só fica sem as
fotos, apenas com o gradiente verde → azul → roxo.

## Passo 2 — no topo do `app.py`

```python
import streamlit as st
import previsc_theme as tema

st.set_page_config(
    page_title="Previsc",
    layout="wide",
    initial_sidebar_state="expanded",
)
```

## Passo 3 — chamar o tema

### A) Tela de capa (imagem 1 do protótipo)

Antes do menu, mostre a capa. Ela é full-width, sem bordas, e o botão
"Calcule agora" é um `st.button` de verdade posicionado por cima —
por isso ele nunca sai do lugar em monitor nenhum.

```python
if "pagina" not in st.session_state:
    st.session_state.pagina = "capa"

if st.session_state.pagina == "capa":
    tema.aplicar("capa")
    if tema.capa():
        st.session_state.pagina = "menu"
        st.rerun()
    st.stop()

tema.aplicar()   # todas as demais telas
```

### B) Sidebar (imagens 2 e 3)

No bloco da sua sidebar, troque o título por:

```python
with st.sidebar:
    tema.logo_sidebar()

    if st.button("Simulador de Autopatrocínio", use_container_width=True):
        st.session_state.pagina = "autopatrocinio"; st.rerun()
    if st.button("Cálculo de Contribuição em Lote", use_container_width=True):
        st.session_state.pagina = "contrib_lote"; st.rerun()
    if st.button("Regras e Bases de Cálculo", use_container_width=True):
        st.session_state.pagina = "regras"; st.rerun()
    if st.button("Simulador Individual", use_container_width=True):
        st.session_state.pagina = "individual"; st.rerun()
    if st.button("Cálculo de Salário em Lote", use_container_width=True):
        st.session_state.pagina = "salario_lote"; st.rerun()

    tema.rodape_sidebar()
```

### C) Cabeçalho de cada funcionalidade

Troque os `st.title(...)` / `st.markdown("## ...")` por:

```python
tema.titulo_pagina(
    "Simulador Previsc",
    "Selecione o plano abaixo para calcular a contribuição sugerida "
    "ou calcular o salário a partir da contribuição.",
)
```

Sugestões por tela (respeitando o que cada uma faz):

| Tela | Título | Descrição |
|---|---|---|
| Simulador Individual | Simulador Previsc | Selecione o plano abaixo para calcular a contribuição sugerida ou calcular o salário a partir da contribuição. |
| Autopatrocínio | Simulador de Autopatrocínio | Verifique a cobrança a partir do salário ou faça o cálculo reverso (gross-up) a partir do valor desejado. |
| Contribuição em Lote | Cálculo de Contribuição em Lote | Baixe a planilha modelo, preencha os salários e faça o upload para processar vários cálculos de uma vez. |
| Salário em Lote | Cálculo de Salário em Lote | Baixe a planilha modelo, preencha a cobrança-alvo e faça o upload para descobrir os salários correspondentes. |
| Regras e Bases | Regras e Bases de Cálculo | Consulte os indexadores atuais e a estrutura de cálculo de cada plano. |

Pronto. Todo o resto — inputs, selectbox, radio, abas, upload, tabelas,
métricas e botões — já é estilizado automaticamente pelo CSS, sem você
precisar tocar em nenhum widget.

## Detalhes de implementação (respondendo às suas 3 perguntas)

1. **Capa full-width:** não use `st.image`. A capa é uma `<div>` com
   `width:100vw; margin-left:calc(50% - 50vw)` para furar o padding do
   `block-container`, e `aspect-ratio:16/9` para escalar proporcionalmente.
2. **Botão sobre a imagem:** em vez de um botão "invisível" (que quebra
   quando o Streamlit muda de versão), o CTA é um `st.button` real puxado
   para dentro da capa com `margin-top` negativo dentro de colunas
   `[2,1,2]`. Ele é sempre clicável, acessível e centralizado em qualquer
   monitor.
3. **Sidebar-cartão:** `section[data-testid="stSidebar"]` fica transparente
   com padding, e o primeiro filho recebe fundo branco + `border-radius:22px`
   + sombra — é isso que cria o efeito de cartão flutuante do protótipo.
