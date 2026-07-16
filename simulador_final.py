import streamlit as st
import pandas as pd
import io

# =================================================================
# 1. CONFIGURAÇÃO DA PÁGINA E CORES
# =================================================================
st.set_page_config(page_title="Sistema Previsc", page_icon="🏢", layout="centered")

st.markdown("""
    <style>
    h1, h2, h3 { color: #1B365D !important; }
    div.stButton > button:first-child {
        background-color: #1B365D; color: white; border-radius: 6px;
        border: none; padding: 10px 24px; font-weight: bold;
        width: 100%;
    }
    div.stButton > button:first-child:hover { background-color: #274D85; color: white; }
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-weight: bold; color: #1B365D;
    }
    hr { border-color: #1B365D; }
    
    div[data-testid="metric-container"] {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        padding: 15px;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)


# =================================================================
# 2. BANCO DE DADOS DOS PLANOS E ALIASES
# =================================================================
planos = {
    "FIESCPREV": {"ur": 716.84, "teto_urs": 7.0, "aliq_1": 0.030, "aliq_2": 0.1400, "tipo": "fatias"},
    "FIEP": {"ur": 742.37, "teto_urs": 8.5, "aliq_1": 0.030, "aliq_2": 0.0750, "tipo": "fatias"},
    "SENACPREV": {"ur": 699.76, "teto_urs": 8.0, "aliq_1": 0.023, "aliq_2": 0.0740, "tipo": "fatias"},
    "SENAI-PIPREV": {"ur": 7376.89, "teto1_urs": 0.5, "teto2_urs": 1.0, "aliq_1": 0.01, "aliq_2": 0.04, "aliq_3": 0.08, "superavit": 0.0728, "tipo": "fatias_triplas_senai"},
    "PREVISC SENAI-MA": {"teto1_rs": 2521.45, "teto2_rs": 5042.89, "tipo": "fatias_triplas_fiema"},
    "PREVFIEPA": {"teto1_rs": 2824.00, "teto2_rs": 7786.02, "tipo": "fatias_triplas_fiepa"},
    "PREVISC SISTEMA FIEP": {"ur": 742.37, "teto_urs": 8.5, "aliq_1": 0.03, "aliq_2": 0.075, "tipo": "fatias"},
    "FECOMERCIO": {"ur": 504.97, "teto_urs": 8.0, "aliq_1": 0.023, "aliq_2": 0.074, "tipo": "fatias"},
    "FIEMTPREV": {"ur": 688.24, "teto_urs": 12.06, "aliq_1": 0.020, "aliq_2": 0.0725, "tipo": "fatias"},
    "PREVISC": {"ur": 710.76, "teto_urs": 7.0, "aliq_1": 0.03, "aliq_2": 0.14, "tipo": "fatias"},
    "UNIVALIPrevidencia": {"ur": 627.19, "teto_urs": 8.0, "aliq_1": 0.030, "tipo": "fatias_univali"},
    "SESI-PIPREV": {"ur": 6812.53, "teto_urs": 1.0, "aliq_1": 0.02, "aliq_2": 0.14, "tipo": "fatias"},
    "SESC SC (SESCPREV)": {"ur": 878.70, "teto1_rs": 8787.00, "teto2_rs": 10042.49, "aliq_1": 0.0139, "aliq_2": 0.0558, "aliq_3": 0.1366, "tipo": "sesc_triplo"},
    "LUNELLIPREV": {"ur": 535.87, "teto_urs": 0, "aliq_1": 0.01, "aliq_2": 0, "tipo": "up_sem_teto"},
    "PREVIFIEA": {"ur": 5998.34, "aliq_1": 0.03, "aliq_2": 0.05, "aliq_3": 0.12, "aliq_4": 0.15, "tipo": "fatias_quadruplas_fiea"},
    "PREVITÊ": {"ur": 682.87, "teto_urs": 0, "aliq_1": 0, "aliq_2": 0, "tipo": "fixo"},
    "UNERJPREV": {"ur": 8475.55, "teto_urs": 1.0, "aliq_1": 0.0025, "tipo": "unerjprev_idade"} 
}

apelidos_planilha = {
    "SESCPREV": "SESC SC (SESCPREV)",
    "SESC SC": "SESC SC (SESCPREV)",
    "SENAI-PI": "SENAI-PIPREV",
    "SENAI-MA": "PREVISC SENAI-MA",
    "FIEMA": "PREVISC SENAI-MA",
    "PREVSENAI": "PREVISC SENAI-MA",
    "FIEPA": "PREVFIEPA",
    "SESI-PI": "SESI-PIPREV"
}

# =================================================================
# 3. MOTORES MATEMÁTICOS E FORMATAÇÃO
# =================================================================
def formatar_br(valor):
    if isinstance(valor, (int, float)):
        return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return valor

def calcular_contribuicao(plano_nome, salario, aliq_escolhida=None, univali_migrante="Migrante", univali_tipo="Normal", idade=30, faixa_opcao="Faixa 1"):
    plano = planos.get(plano_nome)
    if not plano:
        return 0.0, 0.0, 0.0, 0.0, 0.0
        
    tipo = plano.get("tipo", "fatias")
    taxa_superavit = plano.get("superavit", 0.0)
    
    if tipo == "fixo":
        return 0.0, 0.0, 0.0, 0.0, 0.0
        
    if tipo == "up_sem_teto":
        aliq_aplicar = aliq_escolhida if aliq_escolhida else plano["aliq_1"]
        total_bruto = salario * aliq_aplicar
        superavit = total_bruto * taxa_superavit
        return (total_bruto - superavit), total_bruto, 0.0, 0.0, superavit
        
    if tipo == "unerjprev_idade":
        teto_inss = plano["ur"] 
        if salario <= teto_inss:
            aliq = plano["aliq_1"]
        else:
            if idade <= 44:
                aliq = 0.03
            elif 45 <= idade <= 49:
                aliq = 0.04
            elif 50 <= idade <= 54:
                aliq = 0.05
            else: 
                aliq = 0.06
        total_bruto = salario * aliq
        superavit = total_bruto * taxa_superavit
        return (total_bruto - superavit), total_bruto, 0.0, 0.0, superavit

    if tipo == "fatias_quadruplas_fiea":
        up = plano["ur"]
        teto1 = up * 0.5   
        teto2 = up         
        teto3 = up * 3.0   
        f1 = f2 = f3 = f4 = 0.0
        
        if salario <= teto1:
            f1 = salario * plano["aliq_1"]
        elif salario <= teto2:
            f1 = teto1 * plano["aliq_1"]
            f2 = (salario - teto1) * plano["aliq_2"]
        elif salario <= teto3:
            f1 = teto1 * plano["aliq_1"]
            f2 = (teto2 - teto1) * plano["aliq_2"]
            f3 = (salario - teto2) * plano["aliq_3"]
        else:
            f1 = teto1 * plano["aliq_1"]
            f2 = (teto2 - teto1) * plano["aliq_2"]
            f3 = (teto3 - teto2) * plano["aliq_3"]
            f4 = (salario - teto3) * plano["aliq_4"]
            
        total_bruto = f1 + f2 + f3 + f4
        superavit = total_bruto * taxa_superavit
        return (total_bruto - superavit), f1, (f2 + f3), f4, superavit

    if tipo == "fatias_univali":
        teto_rs = plano["ur"] * plano["teto_urs"]
        if univali_migrante == "Migrante":
            aliq_2 = 0.14
        else: 
            if univali_tipo == "Reduzida":
                aliq_2 = 0.14
            else: 
                aliq_2 = 0.17
                    
        if salario <= teto_rs:
            f1 = salario * plano["aliq_1"]
            f2 = 0.0
        else:
            f1 = teto_rs * plano["aliq_1"]
            f2 = (salario - teto_rs) * aliq_2
            
        total_bruto = f1 + f2
        superavit = total_bruto * taxa_superavit
        return (total_bruto - superavit), f1, f2, 0.0, superavit

    if tipo == "sesc_triplo":
        ur = plano["ur"]
        teto1_rs = plano["teto1_rs"]
        teto2_rs = plano["teto2_rs"]
        
        if salario <= teto1_rs:
            total_bruto = salario * plano["aliq_1"]
            f1 = total_bruto
            f2 = f3 = 0.0
        elif salario <= teto2_rs:
            total_bruto = (salario * plano["aliq_2"]) - (0.4190 * ur)
            f1 = teto1_rs * plano["aliq_1"]
            f2 = total_bruto - f1
            f3 = 0.0
        else:
            total_bruto = (salario * plano["aliq_3"]) - (1.3424 * ur)
            f1 = teto1_rs * plano["aliq_1"]
            f2 = ((teto2_rs * plano["aliq_2"]) - (0.4190 * ur)) - f1
            f3 = total_bruto - f1 - f2
            
        superavit = total_bruto * taxa_superavit
        return (total_bruto - superavit), f1, f2, f3, superavit

    if tipo == "fatias_triplas_senai":
        ur = plano["ur"]
        teto1_rs = ur * plano["teto1_urs"]
        teto2_rs = ur * plano["teto2_urs"]
        
        if salario <= teto1_rs:
            f1 = salario * plano["aliq_1"]
            f2 = f3 = 0.0
        elif salario <= teto2_rs:
            f1 = teto1_rs * plano["aliq_1"]
            f2 = (salario - teto1_rs) * plano["aliq_2"]
            f3 = 0.0
        else:
            f1 = teto1_rs * plano["aliq_1"]
            f2 = (teto2_rs - teto1_rs) * plano["aliq_2"]
            f3 = (salario - teto2_rs) * plano["aliq_3"]
            
        total_bruto = f1 + f2 + f3
        superavit = total_bruto * taxa_superavit
        return (total_bruto - superavit), f1, f2, f3, superavit
        
    if tipo == "fatias_triplas_fiema":
        teto1_rs = plano["teto1_rs"]
        teto2_rs = plano["teto2_rs"]
        
        if faixa_opcao == "Faixa 2":
            a1, a2, a3 = 0.0180, 0.0300, 0.1380
        elif faixa_opcao == "Faixa 3":
            a1, a2, a3 = 0.0150, 0.0250, 0.1150
        else: 
            a1, a2, a3 = 0.0210, 0.0350, 0.1610
            
        if salario <= teto1_rs:
            f1 = salario * a1
            f2 = f3 = 0.0
        elif salario <= teto2_rs:
            f1 = teto1_rs * a1
            f2 = (salario - teto1_rs) * a2
            f3 = 0.0
        else:
            f1 = teto1_rs * a1
            f2 = (teto2_rs - teto1_rs) * a2
            f3 = (salario - teto2_rs) * a3
            
        total_bruto = f1 + f2 + f3
        return total_bruto, f1, f2, f3, 0.0

    if tipo == "fatias_triplas_fiepa":
        teto1_rs = plano["teto1_rs"]
        teto2_rs = plano["teto2_rs"]
        
        if faixa_opcao == "Faixa 2":
            a1, a2, a3 = 0.0150, 0.0300, 0.0600
        elif faixa_opcao == "Faixa 3":
            a1, a2, a3 = 0.0200, 0.0400, 0.0700
        else: 
            a1, a2, a3 = 0.0100, 0.0200, 0.0500
            
        if salario <= teto1_rs:
            f1 = salario * a1
            f2 = f3 = 0.0
        elif salario <= teto2_rs:
            f1 = teto1_rs * a1
            f2 = (salario - teto1_rs) * a2
            f3 = 0.0
        else:
            f1 = teto1_rs * a1
            f2 = (teto2_rs - teto1_rs) * a2
            f3 = (salario - teto2_rs) * a3
            
        total_bruto = f1 + f2 + f3
        return total_bruto, f1, f2, f3, 0.0

    teto_rs = plano["ur"] * plano["teto_urs"]
    if salario <= teto_rs:
        f1 = salario * plano["aliq_1"]
        f2 = 0.0
    else:
        f1 = teto_rs * plano["aliq_1"]
        f2 = (salario - teto_rs) * plano["aliq_2"]
        
    total_bruto = f1 + f2
    superavit = total_bruto * taxa_superavit
    return (total_bruto - superavit), f1, f2, 0.0, superavit


def calcular_salario_reverso(plano_nome, contribuicao_liquida, aliq_escolhida=None, univali_migrante="Migrante", univali_tipo="Normal", idade=30, faixa_opcao="Faixa 1"):
    plano = planos.get(plano_nome)
    if not plano:
        return 0.0
        
    tipo = plano.get("tipo", "fatias")
    taxa_superavit = plano.get("superavit", 0.0)
    
    contribuicao = contribuicao_liquida / (1 - taxa_superavit)
    
    if tipo in ["fixo"]:
        return 0.0 
        
    if tipo == "up_sem_teto":
        aliq_aplicar = aliq_escolhida if aliq_escolhida else plano["aliq_1"]
        return contribuicao / aliq_aplicar
        
    if tipo == "unerjprev_idade":
        teto_inss = plano["ur"]
        max_025 = teto_inss * plano["aliq_1"]
        if contribuicao <= max_025:
            return contribuicao / plano["aliq_1"]
        else:
            if idade <= 44:
                aliq = 0.03
            elif 45 <= idade <= 49:
                aliq = 0.04
            elif 50 <= idade <= 54:
                aliq = 0.05
            else: 
                aliq = 0.06
            return contribuicao / aliq

    if tipo == "fatias_quadruplas_fiea":
        up = plano["ur"]
        teto1 = up * 0.5
        teto2 = up
        teto3 = up * 3.0
        
        max_f1 = teto1 * plano["aliq_1"]
        max_f2 = (teto2 - teto1) * plano["aliq_2"]
        max_f3 = (teto3 - teto2) * plano["aliq_3"]
        
        if contribuicao <= max_f1:
            return contribuicao / plano["aliq_1"]
        elif contribuicao <= (max_f1 + max_f2):
            return teto1 + ((contribuicao - max_f1) / plano["aliq_2"])
        elif contribuicao <= (max_f1 + max_f2 + max_f3):
            return teto2 + ((contribuicao - max_f1 - max_f2) / plano["aliq_3"])
        else:
            return teto3 + ((contribuicao - max_f1 - max_f2 - max_f3) / plano["aliq_4"])

    if tipo == "fatias_univali":
        teto_rs = plano["ur"] * plano["teto_urs"]
        max_f1 = teto_rs * plano["aliq_1"]
        
        if univali_migrante == "Migrante":
            aliq_2 = 0.14
        else:
            if univali_tipo == "Reduzida":
                aliq_2 = 0.14
            else:
                aliq_2 = 0.17
                    
        if contribuicao <= max_f1:
            return contribuicao / plano["aliq_1"]
        else:
            return teto_rs + ((contribuicao - max_f1) / aliq_2)

    if tipo == "sesc_triplo":
        ur = plano["ur"]
        teto1_rs = plano["teto1_rs"]
        teto2_rs = plano["teto2_rs"]
        
        max_c1 = teto1_rs * plano["aliq_1"]
        max_c2 = (teto2_rs * plano["aliq_2"]) - (0.4190 * ur)
        
        if contribuicao <= max_c1:
            salario = contribuicao / plano["aliq_1"]
        elif contribuicao <= max_c2:
            salario = (contribuicao + (0.4190 * ur)) / plano["aliq_2"]
        else:
            salario = (contribuicao + (1.3424 * ur)) / plano["aliq_3"]
        return round(salario)

    if tipo == "fatias_triplas_senai":
        ur = plano["ur"]
        teto1_rs = ur * plano["teto1_urs"]
        teto2_rs = ur * plano["teto2_urs"]
        max_f1 = teto1_rs * plano["aliq_1"]
        max_f2 = (teto2_rs - teto1_rs) * plano["aliq_2"]
        
        if contribuicao <= max_f1:
            return contribuicao / plano["aliq_1"]
        elif contribuicao <= max_f1 + max_f2:
            return teto1_rs + ((contribuicao - max_f1) / plano["aliq_2"])
        else:
            return teto2_rs + ((contribuicao - max_f1 - max_f2) / plano["aliq_3"])
            
    if tipo == "fatias_triplas_fiema":
        teto1_rs = plano["teto1_rs"]
        teto2_rs = plano["teto2_rs"]
        
        if faixa_opcao == "Faixa 2":
            a1, a2, a3 = 0.0180, 0.0300, 0.1380
        elif faixa_opcao == "Faixa 3":
            a1, a2, a3 = 0.0150, 0.0250, 0.1150
        else: 
            a1, a2, a3 = 0.0210, 0.0350, 0.1610
            
        max_f1 = teto1_rs * a1
        max_f2 = (teto2_rs - teto1_rs) * a2
        
        if contribuicao <= max_f1:
            return substituicao / a1
        elif substituicao <= max_f1 + max_f2:
            return teto1_rs + ((contribuicao - max_f1) / a2)
        else:
            return teto2_rs + ((contribuicao - max_f1 - max_f2) / a3)

    if tipo == "fatias_triplas_fiepa":
        teto1_rs = plano["teto1_rs"]
        teto2_rs = plano["teto2_rs"]
        
        if faixa_opcao == "Faixa 2":
            a1, a2, a3 = 0.0150, 0.0300, 0.0600
        elif faixa_opcao == "Faixa 3":
            a1, a2, a3 = 0.0200, 0.0400, 0.0700
        else: 
            a1, a2, a3 = 0.0100, 0.0200, 0.0500
            
        max_f1 = teto1_rs * a1
        max_f2 = (teto2_rs - teto1_rs) * a2
        
        if contribuicao <= max_f1:
            return contribuicao / a1
        elif substituicao <= max_f1 + max_f2:
            return teto1_rs + ((contribuicao - max_f1) / a2)
        else:
            return teto2_rs + ((contribuicao - max_f1 - max_f2) / a3)

    teto_rs = plano["ur"] * plano["teto_urs"]
    max_f1 = teto_rs * plano["aliq_1"]
    if contribuicao <= max_f1:
        return substituicao / plano["aliq_1"]
    else:
        return teto_rs + ((contribuicao - max_f1) / plano["aliq_2"])


# =================================================================
# 4. NAVEGAÇÃO LATERAL (SIDEBAR)
# =================================================================
st.sidebar.title("📌 Menu de Navegação")
menu_selecionado = st.sidebar.radio(
    "Escolha a ferramenta:",
    [
        "📊 Simulador Individual", 
        "📂 Cálculo de Contribuição em Lote", 
        "📂 Cálculo de Salário em Lote",
        "📖 Regras e Bases de Cálculo"
    ]
)
st.sidebar.divider()
st.sidebar.info("Sistema interno desenvolvido para cálculos previdenciários precisos e consulta de regras vigentes.")


# =================================================================
# 5. TELA 1: SIMULADOR INDIVIDUAL
# =================================================================
if menu_selecionado == "📊 Simulador Individual":
    st.title("🏢 Simulador Previsc")
    st.write("Selecione o plano abaixo para calcular a contribuição ideal ou calcular o salário a partir da contribuição.")

    plano_selecionado = st.selectbox("Selecione o Plano de Previdência:", options=list(planos.keys()))
    plano_dados = planos[plano_selecionado]

    univali_migrante = "Migrante"
    univali_tipo = "Normal"
    idade_input = 30
    faixa_opcao_selecionada = "Faixa 1"

    if plano_selecionado == "UNIVALIPrevidencia":
        col_u1, col_u2, col_u3 = st.columns(3)
        with col_u1:
            univali_migrante = st.radio("Categoria:", ["Migrante", "Não Migrante"])
        with col_u2:
            univali_tipo = st.radio("Contribuição:", ["Normal", "Reduzida"])
        with col_u3:
            idade_input = st.number_input("Idade:", min_value=16, max_value=80, value=30, step=1)
            
    elif plano_dados.get("tipo") == "unerjprev_idade":
        idade_input = st.number_input("Idade do Participante na Adesão:", min_value=16, max_value=80, value=30, step=1)
        
    elif plano_selecionado == "PREVISC SENAI-MA":
        st.markdown("""
        **Escolha a faixa de contribuição desejada:**
        | Faixa | Salários até R$ 2.521,45 | Salários entre R$ 2.521,45 e R$ 5.042,89 | Salários acima de R$ 5.042,89 |
        |:---:|:---:|:---:|:---:|
        | **1** | 2,10% | 3,50% | 16,10% |
        | **2** | 1,80% | 3,00% | 13,80% |
        | **3** | 1,50% | 2,50% | 11,50% |
        """)
        faixa_opcao_selecionada = st.radio("Selecione a Faixa:", ["Faixa 1", "Faixa 2", "Faixa 3"], horizontal=True, key="faixa_fiema")

    elif plano_selecionado == "PREVFIEPA":
        st.markdown("""
        **Escolha a faixa de contribuição desejada:**
        | Faixa | Salários até R$ 2.824,00 | Salários entre R$ 2.824,00 e R$ 7.786,02 | Salários acima de R$ 7.786,02 |
        |:---:|:---:|:---:|:---:|
        | **1** | 1,00% | 2,00% | 5,00% |
        | **2** | 1,50% | 3,00% | 6,00% |
        | **3** | 2,00% | 4,00% | 7,00% |
        """)
        faixa_opcao_selecionada = st.radio("Selecione a Faixa:", ["Faixa 1", "Faixa 2", "Faixa 3"], horizontal=True, key="faixa_fiepa")

    st.divider()

    aba_normal, aba_reversa = st.tabs(["📊 Cálculo de Contribuição", "🔍 Cálculo de Salário"])

    with aba_normal:
        st.subheader("Calcular Contribuição")
        salario_input = st.number_input("Digite o Salário de Participação (R$):", min_value=0.0, value=0.0, step=100.0, format="%.2f")
        
        aliq_escolhida
