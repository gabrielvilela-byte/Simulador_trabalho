import streamlit as st

# =================================================================
# 1. CONFIGURAÇÃO DA PÁGINA E CORES DA PREVISC
# =================================================================
st.set_page_config(page_title="Simulador Previsc", page_icon="🏢", layout="wide")

# Injeção de CSS para usar a paleta de cores da Previsc (Azul Escuro #1B365D)
st.markdown("""
    <style>
    /* Cor dos Títulos */
    h1, h2, h3 {
        color: #1B365D !important;
    }
    /* Estilo dos Botões Principais */
    div.stButton > button:first-child {
        background-color: #1B365D;
        color: white;
        border-radius: 6px;
        border: none;
        padding: 10px 24px;
        font-weight: bold;
    }
    /* Efeito ao passar o mouse no botão */
    div.stButton > button:first-child:hover {
        background-color: #274D85;
        color: white;
    }
    /* Cor do texto das abas (Tabs) */
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-weight: bold;
        color: #1B365D;
    }
    /* Cor da linha divisória */
    hr {
        border-color: #1B365D;
    }
    </style>
""", unsafe_allow_html=True)


# =================================================================
# 2. BANCO DE DADOS DOS PLANOS
# =================================================================
planos = {
    "FIESCPREV": {"ur": 716.54, "teto_urs": 7.0, "aliq_1": 0.030, "aliq_2": 0.1400, "tipo": "fatias"},
    "FIEP": {"ur": 742.37, "teto_urs": 8.5, "aliq_1": 0.030, "aliq_2": 0.0750, "tipo": "fatias"},
    "SENACPREV": {"ur": 699.76, "teto_urs": 8.0, "aliq_1": 0.023, "aliq_2": 0.0740, "tipo": "fatias"},
    "SENAI-PIPREV": {"ur": 7376.89, "teto_urs": 0.5, "aliq_1": 0.010, "aliq_2": 0.040, "tipo": "fatias"}, 
    "PREVSENAI-MA": {"ur": 5042.89, "teto_urs": 7.0, "aliq_1": 0.030, "aliq_2": 0.140, "tipo": "fatias"},
    "PREVISC SENAI-MA": {"ur": 560.37, "teto_urs": 7.0, "aliq_1": 0.030, "aliq_2": 0.140, "tipo": "fatias"},
    "PREVITÊ": {"ur": 682.87, "teto_urs": 0, "aliq_1": 0, "aliq_2": 0, "tipo": "fixo"},
    "PREVIFIEA": {"ur": 8258.59, "teto_urs": 0, "aliq_1": 0.01, "aliq_2": 0, "tipo": "livre"},
    "PREVISC SISTEMA FIEP": {"ur": 742.37, "teto_urs": 8.5, "aliq_1": 0.03, "aliq_2": 0.075, "tipo": "fatias"},
    "FECOMERCIO": {"ur": 504.97, "teto_urs": 8.0, "aliq_1": 0.023, "aliq_2": 0.074, "tipo": "fatias"},
    "FIEMTPREV": {"ur": 688.24, "teto_urs": 12.06, "aliq_1": 0.020, "aliq_2": 0.0725, "tipo": "fatias"},
    "PREVFIEPA": {"ur": 7740.09, "teto_urs": 0, "aliq_1": 0.01, "aliq_2": 0, "tipo": "livre"},
    "PREVISC": {"ur": 710.76, "teto_urs": 7.0, "aliq_1": 0.03, "aliq_2": 0.14, "tipo": "fatias"},
    "LUNELLIPREV": {"ur": 535.87, "teto_urs": 0, "aliq_1": 0.01, "aliq_2": 0, "tipo": "livre"},
    "SESC SC (SESCPREV)": {"ur": 878.70, "teto_urs": 10.0, "aliq_1": 0.0139, "aliq_2": 0.0558, "aliq_3": 0.1366, "tipo": "sesc_triplo"},
    "UNIVALIPrevidencia": {"ur": 623.33, "teto_urs": 8.0, "aliq_1": 0.030, "aliq_2": 0.1400, "tipo": "fatias"},
    "SESI-PIPREV": {"ur": 6812.53, "teto_urs": 1.0, "aliq_1": 0.017218, "aliq_2": 0.137741, "tipo": "fatias"},
    "UNERJPREV": {"ur": 8475.55, "teto_urs": 1.0, "aliq_1": 0.0025, "aliq_2": 0.03, "tipo": "idade"} 
}

# =================================================================
# 3. MOTORES MATEMÁTICOS
# =================================================================
def calcular_contribuicao(plano_nome, salario):
    plano = planos[plano_nome]
    tipo = plano.get("tipo", "fatias")
    
    if tipo in ["livre", "fixo", "idade"]:
        return 0.0, 0.0, 0.0 
        
    if tipo == "sesc_triplo":
        ur = plano["ur"]
        teto1_rs = ur * 10.0
        teto2_rs = ur * 11.4288
        
        if salario <= teto1_rs:
            return salario * plano["aliq_1"], salario * plano["aliq_1"], 0.0
        elif salario <= teto2_rs:
            f1 = teto1_rs * plano["aliq_1"]
            f2 = (salario * plano["aliq_2"]) - (0.4190 * ur)
            return f1 + f2, f1, f2
        else:
            f1 = teto1_rs * plano["aliq_1"]
            f2 = (teto2_rs * plano["aliq_2"]) - (0.4190 * ur)
            f3 = (salario * plano["aliq_3"]) - (1.3424 * ur)
            return f1 + f2 + f3, f1, f2+f3

    teto_rs = plano["ur"] * plano["teto_urs"]
    if salario <= teto_rs:
        return salario * plano["aliq_1"], salario * plano["aliq_1"], 0.0
    else:
        f1 = teto_rs * plano["aliq_1"]
        f2 = (salario - teto_rs) * plano["aliq_2"]
        return f1 + f2, f1, f2

def calcular_salario_reverso(plano_nome, contribuicao):
    plano = planos[plano_nome]
    tipo = plano.get("tipo", "fatias")
    
    if tipo in ["livre", "fixo", "idade", "sesc_triplo"]:
        return 0.0 
        
    teto_rs = plano["ur"] * plano["teto_urs"]
    max_f1 = teto_rs * plano["aliq_1"]
    
    if contribuicao <= max_f1:
        return contribuicao / plano["aliq_1"]
    else:
        return teto_rs + ((contribuicao - max_f1) / plano["aliq_2"])

# =================================================================
# 4. INTERFACE VISUAL 
# =================================================================
st.title("🏢 Simulador Previsc")
st.write("Base de cálculos atualizada com as regras de Custeio oficiais.")

plano_selecionado = st.selectbox("Selecione o Plano de Previdência:", options=list(planos.keys()))

st.divider()

aba_normal, aba_reversa = st.tabs(["📊 Simulador Normal", "🔍 Simulador Reverso"])

with aba_normal:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Calcular Contribuição")
        salario_input = st.number_input("Digite o Salário de Participação (R$):", min_value=0.0, value=0.0, step=100.0, format="%.2f")
        
        if st.button("Gerar Cálculo", type="primary"):
            if salario_input > 0:
                total, f1, f2 = calcular_contribuicao(plano_selecionado, salario_input)
                if total == 0:
                    st.info("Este plano utiliza regra de Alíquota Livre (escolha do participante), Mínimo Fixo ou baseada em Idade. Consulte o regulamento.")
                else:
                    st.success(f"**Contribuição Ideal:** R$ {total:,.2f}")
                    st.write(f"**Fatia 1:** R$ {f1:,.2f} | **Fatia 2/Excedente:** R$ {f2:,.2f}")
            else:
                st.warning("Insira um salário válido.")

with aba_reversa:
    col3, col4 = st.columns(2)
    with col3:
        st.subheader("Engenharia Reversa")
        contrib_input = st.number_input("Digite a Contribuição Alvo (R$):", min_value=0.0, value=0.0, step=10.0, format="%.2f")
        
        if st.button("Descobrir Salário", type="primary"):
            if contrib_input > 0:
                salario_descob = calcular_salario_reverso(plano_selecionado, contrib_input)
                if salario_descob == 0:
                    st.info("A engenharia reversa para este plano específico requer alinhamento de variáveis livres ou de idade.")
                else:
                    st.success(f"**Salário Exato Necessário:** R$ {salario_descob:,.2f}")
            else:
                st.warning("Insira uma contribuição válida.")