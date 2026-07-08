import streamlit as st

# =================================================================
# 1. CONFIGURAÇÃO DA PÁGINA E CORES
# =================================================================
st.set_page_config(page_title="Simulador Previsc", page_icon="🏢", layout="wide")

st.markdown("""
    <style>
    h1, h2, h3 { color: #1B365D !important; }
    div.stButton > button:first-child {
        background-color: #1B365D; color: white; border-radius: 6px;
        border: none; padding: 10px 24px; font-weight: bold;
    }
    div.stButton > button:first-child:hover { background-color: #274D85; color: white; }
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-weight: bold; color: #1B365D;
    }
    hr { border-color: #1B365D; }
    </style>
""", unsafe_allow_html=True)


# =================================================================
# 2. BANCO DE DADOS DOS PLANOS ATUALIZADO
# =================================================================
planos = {
    "FIESCPREV": {"ur": 716.54, "teto_urs": 7.0, "aliq_1": 0.030, "aliq_2": 0.1400, "tipo": "fatias"},
    "FIEP": {"ur": 742.37, "teto_urs": 8.5, "aliq_1": 0.030, "aliq_2": 0.0750, "tipo": "fatias"},
    "SENACPREV": {"ur": 699.76, "teto_urs": 8.0, "aliq_1": 0.023, "aliq_2": 0.0740, "tipo": "fatias"},
    "PREVISC SENAI-MA": {"ur": 560.37, "teto1_urs": 4.5, "teto2_urs": 9.0, "aliq_1": 0.030, "aliq_2": 0.05, "aliq_3": 0.23, "tipo": "fatias_triplas_senai"},
    "PREVISC SISTEMA FIEP": {"ur": 742.37, "teto_urs": 8.5, "aliq_1": 0.03, "aliq_2": 0.075, "tipo": "fatias"},
    "FECOMERCIO": {"ur": 504.97, "teto_urs": 8.0, "aliq_1": 0.023, "aliq_2": 0.074, "tipo": "fatias"},
    "FIEMTPREV": {"ur": 688.24, "teto_urs": 12.06, "aliq_1": 0.020, "aliq_2": 0.0725, "tipo": "fatias"},
    "PREVISC": {"ur": 710.76, "teto_urs": 7.0, "aliq_1": 0.03, "aliq_2": 0.14, "tipo": "fatias"},
    "UNIVALIPrevidencia": {"ur": 623.33, "teto_urs": 8.0, "aliq_1": 0.030, "aliq_2_migrante": 0.1400, "aliq_2_nao_migrante": 0.1700, "tipo": "fatias_univali"},
    "SESI-PIPREV": {"ur": 6812.53, "teto_urs": 1.0, "aliq_1": 0.02, "aliq_2": 0.14, "tipo": "fatias"},
    "SESC SC (SESCPREV)": {"ur": 878.70, "teto_urs": 10.0, "aliq_1": 0.0139, "aliq_2": 0.0558, "aliq_3": 0.1366, "tipo": "sesc_triplo"},
    "LUNELLIPREV": {"ur": 535.87, "teto_urs": 0, "aliq_1": 0.01, "aliq_2": 0, "tipo": "up_sem_teto"},
    "PREVITÊ": {"ur": 682.87, "teto_urs": 0, "aliq_1": 0, "aliq_2": 0, "tipo": "fixo"},
    "UNERJPREV": {"ur": 8475.55, "teto_urs": 1.0, "aliq_1": 0.0025, "tipo": "unerjprev_idade"} # 0.25% = 0.0025
}


# =================================================================
# 3. MOTORES MATEMÁTICOS AVANÇADOS
# =================================================================
def calcular_contribuicao(plano_nome, salario, aliq_escolhida=None, univali_migrante=True, idade=30):
    plano = planos[plano_nome]
    tipo = plano.get("tipo", "fatias")
    
    if tipo == "fixo":
        return 0.0, 0.0, 0.0, 0.0 
        
    if tipo == "up_sem_teto":
        aliq_aplicar = aliq_escolhida if aliq_escolhida else plano["aliq_1"]
        return (salario * aliq_aplicar), (salario * aliq_aplicar), 0.0, 0.0
        
    if tipo == "unerjprev_idade":
        teto_inss = plano["ur"] # 8475.55
        
        # Define alíquota excedente pela idade
        if idade <= 44:
            aliq_2 = 0.03
        elif 45 <= idade <= 49:
            aliq_2 = 0.04
        elif 50 <= idade <= 54:
            aliq_2 = 0.05
        else: # 55 a 64 (ou mais)
            aliq_2 = 0.06
            
        if salario <= teto_inss:
            f1 = salario * plano["aliq_1"] # 0.25%
            return f1, f1, 0.0, 0.0
        else:
            f1 = teto_inss * plano["aliq_1"]
            f2 = (salario - teto_inss) * aliq_2
            return f1 + f2, f1, f2, 0.0

    if tipo == "sesc_triplo":
        ur = plano["ur"]
        teto1_rs = ur * 10.0
        teto2_rs = ur * 11.4288
        
        if salario <= teto1_rs:
            f1 = salario * plano["aliq_1"]
            return f1, f1, 0.0, 0.0
        elif salario <= teto2_rs:
            f1 = teto1_rs * plano["aliq_1"]
            f2 = (salario * plano["aliq_2"]) - (0.4190 * ur)
            return f1 + f2, f1, f2, 0.0
        else:
            f1 = teto1_rs * plano["aliq_1"]
            f2 = (teto2_rs * plano["aliq_2"]) - (0.4190 * ur)
            f3 = (salario * plano["aliq_3"]) - (1.3424 * ur)
            return f1 + f2 + f3, f1, f2, f3

    if tipo == "fatias_triplas_senai":
        ur = plano["ur"]
        teto1_rs = ur * plano["teto1_urs"]
        teto2_rs = ur * plano["teto2_urs"]
        
        if salario <= teto1_rs:
            f1 = salario * plano["aliq_1"]
            return f1, f1, 0.0, 0.0
        elif salario <= teto2_rs:
            f1 = teto1_rs * plano["aliq_1"]
            f2 = (salario - teto1_rs) * plano["aliq_2"]
            return f1 + f2, f1, f2, 0.0
        else:
            f1 = teto1_rs * plano["aliq_1"]
            f2 = (teto2_rs - teto1_rs) * plano["aliq_2"]
            f3 = (salario - teto2_rs) * plano["aliq_3"]
            return f1 + f2 + f3, f1, f2, f3

    if tipo == "fatias_univali":
        teto_rs = plano["ur"] * plano["teto_urs"]
        aliq_2 = plano["aliq_2_migrante"] if univali_migrante else plano["aliq_2_nao_migrante"]
        
        if salario <= teto_rs:
            f1 = salario * plano["aliq_1"]
            return f1, f1, 0.0, 0.0
        else:
            f1 = teto_rs * plano["aliq_1"]
            f2 = (salario - teto_rs) * aliq_2
            return f1 + f2, f1, f2, 0.0

    # Categoria Fatias (Padrão)
    teto_rs = plano["ur"] * plano["teto_urs"]
    if salario <= teto_rs:
        f1 = salario * plano["aliq_1"]
        return f1, f1, 0.0, 0.0
    else:
        f1 = teto_rs * plano["aliq_1"]
        f2 = (salario - teto_rs) * plano["aliq_2"]
        return f1 + f2, f1, f2, 0.0


def calcular_salario_reverso(plano_nome, contribuicao, aliq_escolhida=None, univali_migrante=True, idade=30):
    plano = planos[plano_nome]
    tipo = plano.get("tipo", "fatias")
    
    if tipo in ["fixo", "sesc_triplo"]:
        return 0.0 
        
    if tipo == "up_sem_teto":
        aliq_aplicar = aliq_escolhida if aliq_escolhida else plano["aliq_1"]
        return contribuicao / aliq_aplicar
        
    if tipo == "unerjprev_idade":
        teto_inss = plano["ur"]
        
        if idade <= 44:
            aliq_2 = 0.03
        elif 45 <= idade <= 49:
            aliq_2 = 0.04
        elif 50 <= idade <= 54:
            aliq_2 = 0.05
        else: 
            aliq_2 = 0.06
            
        max_f1 = teto_inss * plano["aliq_1"]
        
        if contribuicao <= max_f1:
            return contribuicao / plano["aliq_1"]
        else:
            return teto_inss + ((contribuicao - max_f1) / aliq_2)

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

    if tipo == "fatias_univali":
        teto_rs = plano["ur"] * plano["teto_urs"]
        max_f1 = teto_rs * plano["aliq_1"]
        aliq_2 = plano["aliq_2_migrante"] if univali_migrante else plano["aliq_2_nao_migrante"]
        
        if contribuicao <= max_f1:
            return contribuicao / plano["aliq_1"]
        else:
            return teto_rs + ((contribuicao - max_f1) / aliq_2)

    # Categoria Fatias (Padrão)
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
plano_dados = planos[plano_selecionado]

# Controles Dinâmicos Exclusivos
univali_migrante = True
idade_input = 30

col_ctrl1, col_ctrl2 = st.columns(2)
with col_ctrl1:
    if plano_selecionado == "UNIVALIPrevidencia":
        tipo_univali = st.radio("Categoria do participante:", ["Migrante", "Não Migrante"], horizontal=True)
        univali_migrante = (tipo_univali == "Migrante")
    
    if plano_dados.get("tipo") == "unerjprev_idade":
        idade_input = st.number_input("Idade do Participante na Adesão:", min_value=16, max_value=80, value=30, step=1)

st.divider()

aba_normal, aba_reversa = st.tabs(["📊 Simulador Normal", "🔍 Simulador Reverso"])

with aba_normal:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Calcular Contribuição")
        salario_input = st.number_input("Digite o Salário de Participação (R$):", min_value=0.0, value=0.0, step=100.0, format="%.2f")
        
        aliq_escolhida = None
        if plano_dados["tipo"] == "up_sem_teto":
            st.info(f"A UP atual deste plano é de R$ {plano_dados['ur']:,.2f}")
            if salario_input > 0:
                qtd_ups = salario_input / plano_dados["ur"]
                st.write(f"O seu salário equivale a **{qtd_ups:,.2f} UPs**.")
            aliq_input = st.number_input("Alíquota de Contribuição (%):", min_value=1.0, value=plano_dados["aliq_1"]*100, step=0.5)
            aliq_escolhida = aliq_input / 100
            
        if plano_dados.get("tipo") == "unerjprev_idade":
            st.info(f"O Teto do INSS (1 UR) utilizado é de R$ {plano_dados['ur']:,.2f}")
        
        if st.button("Gerar Cálculo", type="primary"):
            if salario_input > 0:
                total, f1, f2, f3 = calcular_contribuicao(plano_selecionado, salario_input, aliq_escolhida, univali_migrante, idade_input)
                
                if total == 0:
                    st.info("Este plano utiliza uma regra de Mínimo Fixo. Consulte o regulamento.")
                elif plano_dados["tipo"] == "up_sem_teto":
                    st.success(f"**Contribuição Ideal:** R$ {total:,.2f}")
                else:
                    st.success(f"**Contribuição Ideal:** R$ {total:,.2f}")
                    if f3 > 0:
                        st.write(f"**Fatia 1:** R$ {f1:,.2f} | **Fatia 2:** R$ {f2:,.2f} | **Fatia 3/Excedente:** R$ {f3:,.2f}")
                    elif f2 > 0 or plano_dados.get("tipo") == "unerjprev_idade":
                        st.write(f"**Fatia 1 (Até Teto):** R$ {f1:,.2f} | **Fatia 2 (Excedente):** R$ {f2:,.2f}")
            else:
                st.warning("Insira um salário válido.")

with aba_reversa:
    col3, col4 = st.columns(2)
    with col3:
        st.subheader("Engenharia Reversa")
        contrib_input = st.number_input("Digite a Contribuição Alvo (R$):", min_value=0.0, value=0.0, step=10.0, format="%.2f")
        
        aliq_escolhida_rev = None
        if plano_dados["tipo"] == "up_sem_teto":
            aliq_input_rev = st.number_input("Alíquota Utilizada (%):", min_value=1.0, value=plano_dados["aliq_1"]*100, step=0.5, key="aliq_rev")
            aliq_escolhida_rev = aliq_input_rev / 100
            
        if st.button("Descobrir Salário", type="primary"):
            if contrib_input > 0:
                salario_descob = calcular_salario_reverso(plano_selecionado, contrib_input, aliq_escolhida_rev, univali_migrante, idade_input)
                if salario_descob == 0:
                    st.info("A engenharia reversa para este plano específico requer alinhamento de variáveis complexas e fatias de dedução.")
                else:
                    st.success(f"**Salário Exato Necessário:** R$ {salario_descob:,.2f}")
            else:
                st.warning("Insira uma contribuição válida.")
