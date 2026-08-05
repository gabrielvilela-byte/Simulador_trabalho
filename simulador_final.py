import streamlit as st
import pandas as pd

# ==========================================
# CONFIGURAÇÃO DA PÁGINA
# ==========================================
st.set_page_config(page_title="Simulador Previsc", page_icon="📊", layout="centered")

st.title("📊 Simulador Previsc - Autopatrocínio")
st.write("Insira os dados abaixo para calcular a contribuição estimada.")

# ==========================================
# INTERFACE DE ENTRADA (INPUTS)
# ==========================================
patrocinadora = st.selectbox(
    "Selecione a Patrocinadora:", 
    ["FIEPA", "FIEMTPREV", "SESI-PI", "Outras"]
)

salario_participacao = st.number_input(
    "Salário de Participação (R$):", 
    min_value=0.0, 
    value=10000.00, 
    step=100.0,
    format="%.2f"
)

# ==========================================
# LÓGICA DE CÁLCULO E REGRAS DE NEGÓCIO
# ==========================================
if st.button("Calcular Contribuição"):
    faixa_base = 0.0
    faixas_intermediarias = 0.0
    contribuicao_total = 0.0
    
    # --------------------------------------
    # REGRA: FIEPA (ATIVOS)
    # --------------------------------------
    if patrocinadora == 'FIEPA':
        ur = 3674.66 # Unidade de Referência (UR)
        
        if salario_participacao <= ur:
            faixa_3 = salario_participacao * 0.03
            faixa_5 = 0.0
            faixa_12 = 0.0
        elif salario_participacao <= (ur * 2):
            faixa_3 = ur * 0.03
            faixa_5 = (salario_participacao - ur) * 0.05
            faixa_12 = 0.0
        else:
            faixa_3 = ur * 0.03
            faixa_5 = ur * 0.05
            faixa_12 = (salario_participacao - (ur * 2)) * 0.12
            
        faixa_base = faixa_3
        faixas_intermediarias = faixa_5 + faixa_12
        contribuicao_total = faixa_base + faixas_intermediarias

    # --------------------------------------
    # REGRA: FIEMTPREV
    # --------------------------------------
    elif patrocinadora == 'FIEMTPREV':
        # Cole a matemática do FIEMTPREV aqui
        pass

    # --------------------------------------
    # REGRA: SESI-PI
    # --------------------------------------
    elif patrocinadora == 'SESI-PI':
        # Cole a matemática do SESI-PI aqui
        pass
        
    else:
        st.warning("A regra de cálculo para esta patrocinadora ainda não foi configurada no sistema.")

    # ==========================================
    # EXIBIÇÃO DOS RESULTADOS (OUTPUTS)
    # ==========================================
    if patrocinadora in ['FIEPA', 'FIEMTPREV', 'SESI-PI']:
        st.markdown("---")
        st.subheader("Resultado da Simulação")
        
        # Função para formatar os valores no padrão R$ brasileiro
        def formata_br(valor):
            return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        
        # Exibição em colunas
        col1, col2, col3 = st.columns(3)
        col1.metric("Faixa Base", formata_br(faixa_base))
        col2.metric("Faixas Intermediárias", formata_br(faixas_intermediarias))
        col3.metric("Contribuição Total", formata_br(contribuicao_total))
        
        st.success(f"A contribuição total estimada é de **{formata_br(contribuicao_total)}**")
