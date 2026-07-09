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
# 2. BANCO DE DADOS DOS PLANOS E ALIASES (APELIDOS)
# =================================================================
planos = {
    "FIESCPREV": {"ur": 716.54, "teto_urs": 7.0, "aliq_1": 0.030, "aliq_2": 0.1400, "tipo": "fatias"},
    "FIEP": {"ur": 742.37, "teto_urs": 8.5, "aliq_1": 0.030, "aliq_2": 0.0750, "tipo": "fatias"},
    "SENACPREV": {"ur": 699.76, "teto_urs": 8.0, "aliq_1": 0.023, "aliq_2": 0.0740, "tipo": "fatias"},
    "SENAI-PIPREV": {"ur": 7376.89, "teto1_urs": 0.5, "teto2_urs": 1.0, "aliq_1": 0.01, "aliq_2": 0.04, "aliq_3": 0.08, "superavit": 0.0728, "tipo": "fatias_triplas_senai"},
    "PREVISC SENAI-MA": {"ur": 560.37, "teto1_urs": 4.5, "teto2_urs": 9.0, "aliq_1": 0.030, "aliq_2": 0.05, "aliq_3": 0.23, "tipo": "fatias_triplas_senai"},
    "PREVISC SISTEMA FIEP": {"ur": 742.37, "teto_urs": 8.5, "aliq_1": 0.03, "aliq_2": 0.075, "tipo": "fatias"},
    "FECOMERCIO": {"ur": 504.97, "teto_urs": 8.0, "aliq_1": 0.023, "aliq_2": 0.074, "tipo": "fatias"},
    "FIEMTPREV": {"ur": 688.24, "teto_urs": 12.06, "aliq_1": 0.020, "aliq_2": 0.0725, "tipo": "fatias"},
    "PREVISC": {"ur": 710.76, "teto_urs": 7.0, "aliq_1": 0.03, "aliq_2": 0.14, "tipo": "fatias"},
    "UNIVALIPrevidencia": {"ur": 623.33, "teto_urs": 8.0, "aliq_1": 0.030, "tipo": "fatias_univali"},
    "SESI-PIPREV": {"ur": 6812.53, "teto_urs": 1.0, "aliq_1": 0.02, "aliq_2": 0.14, "tipo": "fatias"},
    "SESC SC (SESCPREV)": {"ur": 878.70, "teto_urs": 10.0, "aliq_1": 0.0139, "aliq_2": 0.0558, "aliq_3": 0.1366, "tipo": "sesc_triplo"},
    "LUNELLIPREV": {"ur": 535.87, "teto_urs": 0, "aliq_1": 0.01, "aliq_2": 0, "tipo": "up_sem_teto"},
    "PREVIFIEA": {"ur": 5998.34, "aliq_1": 0.03, "aliq_2": 0.05, "aliq_3": 0.12, "aliq_4": 0.15, "tipo": "fatias_quadruplas_fiea"},
    "PREVITÊ": {"ur": 682.87, "teto_urs": 0, "aliq_1": 0, "aliq_2": 0, "tipo": "fixo"},
    "UNERJPREV": {"ur": 8475.55, "teto_urs": 1.0, "aliq_1": 0.0025, "tipo": "unerjprev_idade"} 
}

# Tradutor de apelidos na planilha para o nome oficial do banco de dados
apelidos_planilha = {
    "SESCPREV": "SESC SC (SESCPREV)",
    "SESC SC": "SESC SC (SESCPREV)",
    "SENAI-PI": "SENAI-PIPREV",
    "SENAI-MA": "PREVISC SENAI-MA",
    "FIEMA": "PREVISC SENAI-MA"
}

# =================================================================
# 3. MOTORES MATEMÁTICOS E FORMATAÇÃO
# =================================================================
def formatar_br(valor):
    if isinstance(valor, (int, float)):
        # Formata com separador de milhar americano e ponto decimal, depois inverte para o padrão PT-BR
        return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return valor

def calcular_contribuicao(plano_nome, salario, aliq_escolhida=None, univali_migrante="Migrante", univali_tipo="Normal", idade=30):
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
        teto1_rs = ur * 10.0
        teto2_rs = ur * 11.4288
        
        if salario <= teto1_rs:
            f1 = salario * plano["aliq_1"]
            f2 = f3 = 0.0
        elif salario <= teto2_rs:
            f1 = teto1_rs * plano["aliq_1"]
            f2 = (salario * plano["aliq_2"]) - (0.4190 * ur)
            f3 = 0.0
        else:
            f1 = teto1_rs * plano["aliq_1"]
            f2 = (teto2_rs * plano["aliq_2"]) - (0.4190 * ur)
            f3 = (salario * plano["aliq_3"]) - (1.3424 * ur)
            
        total_bruto = f1 + f2 + f3
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

    # Categoria Fatias (Padrão)
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


def calcular_salario_reverso(plano_nome, contribuicao_liquida, aliq_escolhida=None, univali_migrante="Migrante", univali_tipo="Normal", idade=30):
    plano = planos.get(plano_nome)
    if not plano:
        return 0.0
        
    tipo = plano.get("tipo", "fatias")
    taxa_superavit = plano.get("superavit", 0.0)
    
    # Se houver superávit, o valor recebido na tela (líquido) é "inflado" para o bruto original
    contribuicao = contribuicao_liquida / (1 - taxa_superavit)
    
    if tipo in ["fixo", "sesc_triplo"]:
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

    # Categoria Fatias (Padrão)
    teto_rs = plano["ur"] * plano["teto_urs"]
    max_f1 = teto_rs * plano["aliq_1"]
    if contribuicao <= max_f1:
        return contribuicao / plano["aliq_1"]
    else:
        return teto_rs + ((contribuicao - max_f1) / plano["aliq_2"])


# =================================================================
# 4. NAVEGAÇÃO LATERAL (SIDEBAR)
# =================================================================
st.sidebar.title("📌 Menu de Navegação")
menu_selecionado = st.sidebar.radio(
    "Escolha a ferramenta:",
    ["📊 Simulador de Contribuição", "📂 Cálculo em Lote", "📖 Regras e Bases de Cálculo"]
)
st.sidebar.divider()
st.sidebar.info("Sistema interno desenvolvido para cálculos previdenciários precisos e consulta de regras vigentes.")


# =================================================================
# 5. TELA 1: SIMULADOR DE CONTRIBUIÇÃO (INDIVIDUAL)
# =================================================================
if menu_selecionado == "📊 Simulador de Contribuição":
    st.title("🏢 Simulador Previsc")
    st.write("Selecione o plano abaixo para calcular a contribuição ideal ou realizar a engenharia reversa do salário.")

    plano_selecionado = st.selectbox("Selecione o Plano de Previdência:", options=list(planos.keys()))
    plano_dados = planos[plano_selecionado]

    # Controles Dinâmicos Exclusivos
    univali_migrante = "Migrante"
    univali_tipo = "Normal"
    idade_input = 30

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

    st.divider()

    aba_normal, aba_reversa = st.tabs(["📊 Simulador Normal", "🔍 Simulador Reverso"])

    with aba_normal:
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
            
        if plano_selecionado == "PREVIFIEA":
            st.info(f"A UP atual adotada para o plano PreviFIEA é de R$ {plano_dados['ur']:,.2f}")
            
        if plano_dados.get("tipo") == "unerjprev_idade":
            st.info(f"O Teto do INSS (1 UR) utilizado é de R$ {plano_dados['ur']:,.2f}")
            
        if plano_selecionado == "SENAI-PIPREV":
            st.info(f"A UR atual adotada para o plano SENAI-PI é de R$ {plano_dados['ur']:,.2f}")
        
        if st.button("Gerar Cálculo", type="primary"):
            if salario_input > 0:
                total, f1, f2, f3, superavit = calcular_contribuicao(plano_selecionado, salario_input, aliq_escolhida, univali_migrante, univali_tipo, idade_input)
                
                if total == 0:
                    st.info("Este plano utiliza uma regra de Mínimo Fixo. Consulte o regulamento.")
                elif plano_dados["tipo"] in ["up_sem_teto", "unerjprev_idade"]:
                    st.success(f"**Contribuição Ideal:** R$ {total:,.2f}")
                elif plano_selecionado == "PREVIFIEA":
                    st.success(f"**Contribuição Ideal (Cascata):** R$ {total:,.2f}")
                    col_f1, col_f2, col_f3 = st.columns(3)
                    col_f1.metric("Fatia Base (Até 0,5 UP)", f"R$ {f1:,.2f}")
                    col_f2.metric("Fatias Intermédias", f"R$ {f2:,.2f}")
                    col_f3.metric("Fatia Topo (> 3 UPs)", f"R$ {f3:,.2f}")
                else:
                    st.success(f"**Contribuição Ideal:** R$ {total:,.2f}")
                    if superavit > 0:
                        st.info(f"Desconto de Superávit Participante (7,28%): **- R$ {superavit:,.2f}**")
                        
                    if f3 > 0:
                        col_f1, col_f2, col_f3 = st.columns(3)
                        col_f1.metric("Fatia 1", f"R$ {f1:,.2f}")
                        col_f2.metric("Fatia 2", f"R$ {f2:,.2f}")
                        col_f3.metric("Fatia 3 (Excedente)", f"R$ {f3:,.2f}")
                    elif f2 > 0:
                        col_f1, col_f2 = st.columns(2)
                        col_f1.metric("Fatia 1 (Até Teto)", f"R$ {f1:,.2f}")
                        col_f2.metric("Fatia 2 (Excedente)", f"R$ {f2:,.2f}")
            else:
                st.warning("Insira um salário válido.")

    with aba_reversa:
        st.subheader("Engenharia Reversa")
        contrib_input = st.number_input("Digite a Contribuição Alvo (R$):", min_value=0.0, value=0.0, step=10.0, format="%.2f")
        
        aliq_escolhida_rev = None
        if plano_dados["tipo"] == "up_sem_teto":
            aliq_input_rev = st.number_input("Alíquota Utilizada (%):", min_value=1.0, value=plano_dados["aliq_1"]*100, step=0.5, key="aliq_rev")
            aliq_escolhida_rev = aliq_input_rev / 100
            
        if st.button("Descobrir Salário", type="primary"):
            if contrib_input > 0:
                salario_descob = calcular_salario_reverso(plano_selecionado, contrib_input, aliq_escolhida_rev, univali_migrante, univali_tipo, idade_input)
                if salario_descob == 0:
                    st.info("A engenharia reversa para este plano específico requer alinhamento de variáveis complexas e fatias de dedução.")
                else:
                    st.success(f"**Salário Exato Necessário:** R$ {salario_descob:,.2f}")
            else:
                st.warning("Insira uma contribuição válida.")


# =================================================================
# 6. TELA 2: CÁLCULO EM LOTE (PLANILHA EXCEL)
# =================================================================
elif menu_selecionado == "📂 Cálculo em Lote":
    st.title("📂 Cálculo em Lote")
    st.write("Baixe a planilha modelo, preencha as informações dos participantes e faça o upload para processar múltiplos cálculos de uma só vez.")
    
    # Gerar a Planilha Modelo para Download (Baseada nas colunas que você enviou + opcionais)
    df_modelo = pd.DataFrame({
        "Plano": ["FIESCPREV", "SESCPREV", "UNIVALIPrevidencia"],
        "Salário Bruto": [4500.00, 8000.00, 5200.00],
        "Idade (Opcional)": [30, 45, 35],
        "Aliquota Opcional % (Opcional)": [0.0, 0.0, 0.0],
        "Univali Categoria (Opcional)": ["-", "-", "Migrante"],
        "Univali Tipo (Opcional)": ["-", "-", "Normal"]
    })
    
    buffer_modelo = io.BytesIO()
    with pd.ExcelWriter(buffer_modelo, engine='openpyxl') as writer:
        df_modelo.to_excel(writer, index=False, sheet_name="Modelo_Previsc")
    
    st.download_button(
        label="📥 Baixar Planilha Modelo", 
        data=buffer_modelo.getvalue(), 
        file_name="modelo_calculo_lote.xlsx", 
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    
    st.divider()
    
    # Upload da Planilha Preenchida pelo Usuário
    st.subheader("Processar Base de Dados")
    arquivo_upload = st.file_uploader("Faça o upload da planilha preenchida (.xlsx)", type=["xlsx"])
    
    if arquivo_upload is not None:
        try:
            df_lote = pd.read_excel(arquivo_upload)
            
            resultados = []
            for idx, row in df_lote.iterrows():
                # Pega o nome do plano da planilha e verifica se tem algum apelido
                plano_excel = str(row.get("Plano", "")).strip().upper()
                plano_oficial = apelidos_planilha.get(plano_excel, str(row.get("Plano", "")).strip())
                
                if plano_oficial in planos:
                    salario = float(row.get("Salário Bruto", 0.0)) if pd.notna(row.get("Salário Bruto")) else 0.0
                    
                    idade = int(row.get("Idade (Opcional)", 30)) if "Idade (Opcional)" in df_lote.columns and pd.notna(row.get("Idade (Opcional)")) else 30
                    aliq_bruta = row.get("Aliquota Opcional % (Opcional)", 0.0) if "Aliquota Opcional % (Opcional)" in df_lote.columns else 0.0
                    aliq = float(aliq_bruta) / 100 if pd.notna(aliq_bruta) and float(aliq_bruta) > 0 else None
                    univ_cat = str(row.get("Univali Categoria (Opcional)", "Migrante")).strip() if "Univali Categoria (Opcional)" in df_lote.columns else "Migrante"
                    univ_tipo = str(row.get("Univali Tipo (Opcional)", "Normal")).strip() if "Univali Tipo (Opcional)" in df_lote.columns else "Normal"
                    
                    total_pagar = calcular_contribuicao(plano_oficial, salario, aliq, univ_cat, univ_tipo, idade)[0]
                    resultados.append(total_pagar)
                else:
                    resultados.append("Plano Não Encontrado")
            
            # Adiciona a coluna com a formatação monetária 0,00
            df_lote["Contribuição Sugerida (R$)"] = [formatar_br(v) for v in resultados]
            
            st.success("Cálculo em lote finalizado com sucesso! Veja a prévia abaixo e faça o download do resultado.")
            st.dataframe(df_lote, use_container_width=True)
            
            # Gerar arquivo de Resultado para Download
            buffer_resultado = io.BytesIO()
            with pd.ExcelWriter(buffer_resultado, engine='openpyxl') as writer:
                df_lote.to_excel(writer, index=False, sheet_name="Resultados_Previsc")
                
            st.download_button(
                label="📤 Baixar Resultados Processados", 
                data=buffer_resultado.getvalue(), 
                file_name="resultado_calculo_lote.xlsx", 
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
        except Exception as e:
            st.error(f"Erro ao ler a planilha. Certifique-se de que o arquivo segue o formato do modelo. Detalhe: {e}")


# =================================================================
# 7. TELA 3: REGRAS E BASES DE CÁLCULO (TABELA EXPLICATIVA)
# =================================================================
elif menu_selecionado == "📖 Regras e Bases de Cálculo":
    st.title("📖 Regras e Bases de Cálculo")
    st.write("Consulte abaixo os indexadores atuais e a estrutura de cálculo configurada para cada plano de previdência no sistema.")
    
    dados_tabela = [
        {"Plano": "FIESCPREV", "Indexador": "UR", "Valor (R$)": "716,54", "Regra de Cálculo": "Fatias: 3% (Até 7 UR) | 14% (Acima)"},
        {"Plano": "FIEP", "Indexador": "UR", "Valor (R$)": "742,37", "Regra de Cálculo": "Fatias: 3% (Até 8,5 UR) | 7,5% (Acima)"},
        {"Plano": "SENACPREV", "Indexador": "UR", "Valor (R$)": "699,76", "Regra de Cálculo": "Fatias: 2,3% (Até 8 UR) | 7,4% (Acima)"},
        {"Plano": "SENAI-PIPREV", "Indexador": "UR", "Valor (R$)": "7.376,89", "Regra de Cálculo": "Fatias Cascata: 1% (Até 0,5) | 4% (0,5 a 1) | 8% (Acima) - Desconto de Superávit (7,28%)"},
        {"Plano": "PREVISC SENAI-MA", "Indexador": "UR", "Valor (R$)": "560,37", "Regra de Cálculo": "Fatias Triplas: 3% (Até 4,5 UR) | 5% (Até 9 UR) | 23% (Acima)"},
        {"Plano": "PREVISC SISTEMA FIEP", "Indexador": "UR", "Valor (R$)": "742,37", "Regra de Cálculo": "Fatias: 3% (Até 8,5 UR) | 7,5% (Acima)"},
        {"Plano": "FECOMERCIO", "Indexador": "UR", "Valor (R$)": "504,97", "Regra de Cálculo": "Fatias: 2,3% (Até 8 UR) | 7,4% (Acima)"},
        {"Plano": "FIEMTPREV", "Indexador": "UR", "Valor (R$)": "688,24", "Regra de Cálculo": "Fatias: 2% (Até 12,06 UR) | 7,25% (Acima)"},
        {"Plano": "PREVISC", "Indexador": "UR", "Valor (R$)": "710,76", "Regra de Cálculo": "Fatias: 3% (Até 7 UR) | 14% (Acima)"},
        {"Plano": "UNIVALIPrevidencia", "Indexador": "UR", "Valor (R$)": "623,33", "Regra de Cálculo": "Fatia Fixa: 3% (Até 8 UR) | Excedente: 14% a 17% variando por Categoria e Idade"},
        {"Plano": "SESI-PIPREV", "Indexador": "SP", "Valor (R$)": "6.812,53", "Regra de Cálculo": "Fatias: 2% (Até 1 SP) | 14% (Acima)"},
        {"Plano": "SESC SC (SESCPREV)", "Indexador": "UR", "Valor (R$)": "878,70", "Regra de Cálculo": "Fatias Dedutíveis: 1,39% (Até 10) | 5,58% (10 a 11,42) | 13,66% (Acima) com abatimentos fixos"},
        {"Plano": "LUNELLIPREV", "Indexador": "UP", "Valor (R$)": "535,87", "Regra de Cálculo": "Livre Escolha (% Fixo sem Teto sobre a base inteira)"},
        {"Plano": "PREVIFIEA", "Indexador": "UP", "Valor (R$)": "5.998,34", "Regra de Cálculo": "Fatias Cascata (SRC): 3% (Até 0,5 UP) | 5% (0,5 a 1) | 12% (1 a 3) | 15% (Acima)"},
        {"Plano": "UNERJPREV", "Indexador": "INSS", "Valor (R$)": "8.475,55", "Regra de Cálculo": "Base Inteira Única: 0,25% (Até 1 Teto). Acima de 1 Teto aplica 3% a 6% retroativo conforme a idade"},
        {"Plano": "PREVITÊ", "Indexador": "-", "Valor (R$)": "-", "Regra de Cálculo": "Contribuição Fixa / Regulamento Fechado"}
    ]
    
    st.dataframe(pd.DataFrame(dados_tabela), use_container_width=True, hide_index=True)
