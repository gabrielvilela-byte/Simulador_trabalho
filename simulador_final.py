import streamlit as st
import previsc_theme as pv
import pandas as pd
import io
from decimal import Decimal, ROUND_HALF_UP
from datetime import date

# =================================================================
# 1. CONFIGURAÇÃO DA PÁGINA E CORES
# =================================================================
st.set_page_config(page_title="Simulador Previsc", page_icon="🏢",
                   layout="wide", initial_sidebar_state="expanded")

if 'menu_selecionado' not in st.session_state:
    st.session_state['menu_selecionado'] = 'home'
menu_selecionado = st.session_state['menu_selecionado']

pv.aplicar("capa" if menu_selecionado in ('home', 'menu') else "interna")


# =================================================================
# 2. BANCO DE DADOS DOS PLANOS E ALIASES
# =================================================================
planos = {
    "FIESCPREV": {"ur": 716.84, "teto_urs": 7.0, "aliq_1": 0.030, "aliq_2": 0.1400, "tx_adm": 0.0218, "tx_risco": 0.0034, "tipo": "faixas", "base_adm_com_risco": True},
    "FIEP": {"ur": 742.37, "teto_urs": 8.5, "aliq_1": 0.030, "aliq_2": 0.0750, "tx_adm": 0.0218, "tx_risco": 0.0, "tipo": "faixas"},
    "SENACPREV": {"ur": 734.75, "teto_urs": 8.0, "aliq_1": 0.023, "aliq_2": 0.0740, "tx_adm": 0.0218, "tx_risco": 0.0012, "tx_risco_auto": 0.0024, "tipo": "faixas"},
    "SENAI-PIPREV": {"ur": 7376.89, "teto1_urs": 0.5, "teto2_urs": 1.0, "aliq_1": 0.01, "aliq_2": 0.04, "aliq_3": 0.08, "superavit": 0.0728, "tx_adm": 0.0218, "tx_risco": 0.0, "tipo": "faixas_triplas_senai"},
    "PREVISC SENAI-MA": {"teto1_rs": 2907.14, "teto2_rs": 5000.00, "tx_adm": 0.0235, "tx_risco": 0.0, "tipo": "faixas_triplas_fiema"},
    "PREVFIEPA": {"up": 7740.09, "tx_adm": 0.04, "tx_risco": 0.0235, "tipo": "faixas_quadruplas_fiepa"},
    "FECOMERCIO": {"ur": 845.22, "teto_urs": 8.0, "aliq_1": 0.023, "aliq_2": 0.074, "tx_adm": 0.0, "tx_risco": 0.0, "tipo": "faixas"},
    "FIEMTPREV": {"ur": 715.77, "teto_urs": 12.06, "aliq_1": 0.020, "aliq_2": 0.0725, "tx_adm": 0.0218, "tx_risco": 0.0, "tipo": "faixas"},
    "UNIVALIPrevidencia": {"ur": 627.19, "teto_urs": 8.0, "aliq_1": 0.030, "tx_adm": 0.0218, "tx_risco": 0.0, "tipo": "faixas_univali"},
    "SESI-PIPREV": {"ur": 6812.53, "tx_adm": 0.0218, "tx_risco": 0.0, "tipo": "sesi_piprev_deducao"},
    "SESC SC (SESCPREV)": {"ur": 922.63, "teto1_urs": 10.0, "teto2_urs": 11.4288, "aliq_1": 0.0139, "aliq_2": 0.0558, "aliq_3": 0.1366, "tx_adm": 0.0218, "tx_risco": 0.0012, "tipo": "sesc_triplo_ur"},
    "LUNELLIPREV": {"aliq_1": 0.01, "tx_adm": 0.0, "tx_risco": 0.0, "tipo": "lunelliprev"},
    "PREVIFIEA": {"up": 8258.59, "tx_adm": 0.04, "tx_risco": 0.0235, "tipo": "faixas_quadruplas_fiepa"},
    "PREVITÊ": {"ur": 682.87, "teto_urs": 0, "aliq_1": 0, "aliq_2": 0, "tx_adm": 0.0, "tx_risco": 0.0, "tipo": "fixo"},
    "UNERJPREV": {"ur": 8475.55, "teto_urs": 1.0, "aliq_1": 0.0025, "tx_adm": 0.0, "tx_risco": 0.0, "tipo": "unerjprev_idade"} 
}

apelidos_planilha = {
    "SESCPREV": "SESC SC (SESCPREV)",
    "SESC SC": "SESC SC (SESCPREV)",
    "SENAI-PI": "SENAI-PIPREV",
    "SENAI-MA": "PREVISC SENAI-MA",
    "FIEMA": "PREVISC SENAI-MA",
    "PREVSENAI": "PREVISC SENAI-MA",
    "FIEPA": "PREVFIEPA",
    "SESI-PI": "SESI-PIPREV",
    "FIEA": "PREVIFIEA"
}

planos_com_risco = ["FIESCPREV", "SESC SC (SESCPREV)", "PREVISC SENAI-MA", "SENACPREV", "PREVFIEPA", "PREVIFIEA"]

# =================================================================
# 3. MOTORES MATEMÁTICOS E FORMATAÇÃO
# =================================================================

def arredondar(valor):
    """Aplica o arredondamento financeiro oficial de 2 casas decimais (Round Half Up)."""
    return float(Decimal(f"{valor:.5f}").quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))

def formatar_br(valor):
    if isinstance(valor, (int, float)):
        return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return valor

def converter_br(valor_str):
    """Lê entradas com vírgula no padrão brasileiro e converte para float."""
    if isinstance(valor_str, (int, float)):
        return float(valor_str)
    if not valor_str:
        return 0.0
    valor_str = str(valor_str).replace("R$", "").replace("%", "").strip()
    if valor_str == "":
        return 0.0
    if "." in valor_str and "," in valor_str:
        valor_str = valor_str.replace(".", "")
    valor_str = valor_str.replace(",", ".")
    try:
        return float(valor_str)
    except:
        return 0.0

def refinar_centro_arredondamento(salario_base, valor_alvo, funcao_teste):
    s_cents = int(round(salario_base * 100))
    alvo_arredondado = round(valor_alvo, 2)
    
    if round(funcao_teste(s_cents / 100.0), 2) != alvo_arredondado:
        encontrou = False
        for offset in range(-10, 11):
            if round(funcao_teste((s_cents + offset) / 100.0), 2) == alvo_arredondado:
                s_cents += offset
                encontrou = True
                break
        if not encontrou:
            return round(salario_base, 2)
            
    s_min = s_cents
    for _ in range(1000): 
        if round(funcao_teste((s_min - 1) / 100.0), 2) == alvo_arredondado:
            s_min -= 1
        else:
            break
            
    s_max = s_cents
    for _ in range(1000): 
        if round(funcao_teste((s_max + 1) / 100.0), 2) == alvo_arredondado:
            s_max += 1
        else:
            break
            
    return (s_min + s_max) / 200.0


def calcular_contribuicao(plano_nome, salario, aliq_escolhida=None, univali_migrante="Migrante", univali_tipo="Normal", idade_ou_tempo=30, faixa_opcao="Faixa 1", is_autopatrocinio=False):
    plano = planos.get(plano_nome)
    if not plano:
        return 0.0, 0.0, 0.0, 0.0, 0.0
        
    tipo = plano.get("tipo", "faixas")
    taxa_superavit = plano.get("superavit", 0.0)
    
    if is_autopatrocinio:
        taxa_superavit = 0.0
        
    if tipo == "sesi_piprev_deducao":
        ur = plano["ur"]
        if salario > ur:
            contrib_pura = arredondar((salario * 0.137741) - (ur * 0.122124))
        else:
            contrib_pura = arredondar(salario * 0.017218)
            
        tx_adm = plano.get("tx_adm", 0.0)
        valor_adm = arredondar(contrib_pura * tx_adm)
        contrib_liquida = arredondar(contrib_pura - valor_adm)
        
        if is_autopatrocinio:
            return contrib_pura, contrib_pura, valor_adm, 0.0, 0.0
            
        # Retorna o Líquido no índice 0 (Total), Pura no 1 (f1) e Valor_Adm no 2 (f2)
        return contrib_liquida, contrib_pura, valor_adm, 0.0, 0.0
    
    if tipo == "fixo":
        return 0.0, 0.0, 0.0, 0.0, 0.0
        
    if tipo == "up_sem_teto":
        aliq_aplicar = aliq_escolhida if aliq_escolhida is not None else plano["aliq_1"]
        total_bruto = arredondar(salario * aliq_aplicar)
        superavit = arredondar(total_bruto * taxa_superavit)
        return arredondar(total_bruto - superavit), total_bruto, 0.0, 0.0, superavit

    if tipo == "lunelliprev":
        aliq_aplicar = aliq_escolhida if aliq_escolhida is not None else plano["aliq_1"]
        aliq_aplicar = max(aliq_aplicar, 0.01)
        total_bruto = arredondar(salario * aliq_aplicar)
        return total_bruto, total_bruto, 0.0, 0.0, 0.0
        
    if tipo == "unerjprev_idade":
        teto_inss = plano["ur"] 
        if salario <= teto_inss:
            aliq = plano["aliq_1"]
        else:
            if idade_ou_tempo <= 44:
                aliq = 0.03
            elif 45 <= idade_ou_tempo <= 49:
                aliq = 0.04
            elif 50 <= idade_ou_tempo <= 54:
                aliq = 0.05
            else: 
                aliq = 0.06
                
        total_bruto = arredondar(salario * aliq)
        superavit = arredondar(total_bruto * taxa_superavit)
        return arredondar(total_bruto - superavit), total_bruto, 0.0, 0.0, superavit

    if tipo == "faixas_quadruplas_fiepa":
        up = plano["up"]
        teto1 = up * 0.5
        teto2 = up * 1.0
        teto3 = up * 3.0
        
        if faixa_opcao == "Faixa 2":
            a1, a2, a3, a4 = 0.0270, 0.0450, 0.1080, 0.1350
        elif faixa_opcao == "Faixa 3":
            a1, a2, a3, a4 = 0.0240, 0.0400, 0.0960, 0.1200
        elif faixa_opcao == "Faixa 4":
            a1, a2, a3, a4 = 0.0210, 0.0350, 0.0840, 0.1050
        elif faixa_opcao == "Faixa 5":
            a1, a2, a3, a4 = 0.0180, 0.0300, 0.0720, 0.0900
        elif faixa_opcao == "Faixa 6":
            a1, a2, a3, a4 = 0.0150, 0.0250, 0.0600, 0.0750
        else: 
            a1, a2, a3, a4 = 0.0300, 0.0500, 0.1200, 0.1500
            
        f1 = f2 = f3 = f4 = 0.0
        
        if salario <= teto1:
            f1 = arredondar(salario * a1)
        elif salario <= teto2:
            f1 = arredondar(teto1 * a1)
            f2 = arredondar((salario - teto1) * a2)
        elif salario <= teto3:
            f1 = arredondar(teto1 * a1)
            f2 = arredondar((teto2 - teto1) * a2)
            f3 = arredondar((salario - teto2) * a3)
        else:
            f1 = arredondar(teto1 * a1)
            f2 = arredondar((teto2 - teto1) * a2)
            f3 = arredondar((teto3 - teto2) * a3)
            f4 = arredondar((salario - teto3) * a4)
            
        total_bruto = arredondar(f1 + f2 + f3 + f4)
        return total_bruto, f1, arredondar(f2 + f3), f4, 0.0

    if tipo == "faixas_univali":
        teto_rs = plano["ur"] * plano["teto_urs"]
        if univali_migrante == "Migrante":
            aliq_2 = 0.14
        else: 
            if univali_tipo == "Reduzida":
                aliq_2 = 0.14
            else: 
                aliq_2 = 0.17
                    
        if salario <= teto_rs:
            f1 = arredondar(salario * plano["aliq_1"])
            f2 = 0.0
        else:
            f1 = arredondar(teto_rs * plano["aliq_1"])
            f2 = arredondar((salario - teto_rs) * aliq_2)
            
        total_bruto = arredondar(f1 + f2)
        superavit = arredondar(total_bruto * taxa_superavit)
        return arredondar(total_bruto - superavit), f1, f2, 0.0, superavit

    if tipo == "sesc_triplo_ur":
        ur = plano["ur"]
        teto1_rs = ur * plano["teto1_urs"]
        teto2_rs = ur * plano["teto2_urs"]
        
        if salario <= teto1_rs:
            total_bruto = arredondar(salario * plano["aliq_1"])
            f1 = total_bruto
            f2 = f3 = 0.0
        elif salario <= teto2_rs:
            total_bruto = arredondar((salario * plano["aliq_2"]) - (0.4190 * ur))
            f1 = arredondar(teto1_rs * plano["aliq_1"])
            f2 = arredondar(total_bruto - f1)
            f3 = 0.0
        else:
            total_bruto = arredondar((salario * plano["aliq_3"]) - (1.3424 * ur))
            f1 = arredondar(teto1_rs * plano["aliq_1"])
            f2 = arredondar(((teto2_rs * plano["aliq_2"]) - (0.4190 * ur)) - f1)
            f3 = arredondar(total_bruto - f1 - f2)
            
        superavit = arredondar(total_bruto * taxa_superavit)
        return arredondar(total_bruto - superavit), f1, f2, f3, superavit

    if tipo == "faixas_triplas_senai":
        ur = plano["ur"]
        teto1_rs = ur * plano["teto1_urs"]
        teto2_rs = ur * plano["teto2_urs"]
        
        if salario <= teto1_rs:
            f1 = arredondar(salario * plano["aliq_1"])
            f2 = f3 = 0.0
        elif salario <= teto2_rs:
            f1 = arredondar(teto1_rs * plano["aliq_1"])
            f2 = arredondar((salario - teto1_rs) * plano["aliq_2"])
            f3 = 0.0
        else:
            f1 = arredondar(teto1_rs * plano["aliq_1"])
            f2 = arredondar((teto2_rs - teto1_rs) * plano["aliq_2"])
            f3 = arredondar((salario - teto2_rs) * plano["aliq_3"])
            
        total_bruto = arredondar(f1 + f2 + f3)
        superavit = arredondar(total_bruto * taxa_superavit)
        return arredondar(total_bruto - superavit), f1, f2, f3, superavit
        
    if tipo == "faixas_triplas_fiema":
        teto1_rs = plano["teto1_rs"]
        teto2_rs = plano["teto2_rs"]
        
        if faixa_opcao == "Faixa 2":
            a1, a2, a3 = 0.0180, 0.0300, 0.1380
        elif faixa_opcao == "Faixa 3":
            a1, a2, a3 = 0.0150, 0.0250, 0.1150
        else: 
            a1, a2, a3 = 0.0210, 0.0350, 0.1610
            
        if salario <= teto1_rs:
            f1 = arredondar(salario * a1)
            f2 = f3 = 0.0
        elif salario <= teto2_rs:
            f1 = arredondar(teto1_rs * a1)
            f2 = arredondar((salario - teto1_rs) * a2)
            f3 = 0.0
        else:
            f1 = arredondar(teto1_rs * a1)
            f2 = arredondar((teto2_rs - teto1_rs) * a2)
            f3 = arredondar((salario - teto2_rs) * a3)
            
        total_bruto = arredondar(f1 + f2 + f3)
        return total_bruto, f1, f2, f3, 0.0

    teto_rs = plano["ur"] * plano["teto_urs"]
    if salario <= teto_rs:
        f1 = arredondar(salario * plano["aliq_1"])
        f2 = 0.0
    else:
        f1 = arredondar(teto_rs * plano["aliq_1"])
        f2 = arredondar((salario - teto_rs) * plano["aliq_2"])
        
    total_bruto = arredondar(f1 + f2)
    superavit = arredondar(total_bruto * taxa_superavit)
    return arredondar(total_bruto - superavit), f1, f2, 0.0, superavit


def _calcular_salario_reverso_matematico(plano_nome, contribuicao_liquida, aliq_escolhida=None, univali_migrante="Migrante", univali_tipo="Normal", idade_ou_tempo=30, faixa_opcao="Faixa 1", is_autopatrocinio=False):
    plano = planos.get(plano_nome)
    if not plano:
        return 0.0
        
    tipo = plano.get("tipo", "faixas")
    taxa_superavit = plano.get("superavit", 0.0)
    
    if is_autopatrocinio:
        taxa_superavit = 0.0
        
    if tipo == "sesi_piprev_deducao":
        ur = plano["ur"]
        tx_adm = plano.get("tx_adm", 0.0)
        
        if is_autopatrocinio:
            contrib_pura = contribuicao_liquida
        else:
            contrib_pura = contribuicao_liquida / (1 - tx_adm)
            
        limite_f1 = ur * 0.017218
        if contrib_pura <= limite_f1:
            return contrib_pura / 0.017218
        else:
            return (contrib_pura + (ur * 0.122124)) / 0.137741
            
    contribuicao = contribuicao_liquida / (1 - taxa_superavit)
    
    if tipo in ["fixo"]:
        return 0.0 
        
    if tipo == "up_sem_teto":
        aliq_aplicar = aliq_escolhida if aliq_escolhida is not None else plano["aliq_1"]
        return contribuicao / aliq_aplicar

    if tipo == "lunelliprev":
        aliq_aplicar = aliq_escolhida if aliq_escolhida is not None else plano["aliq_1"]
        aliq_aplicar = max(aliq_aplicar, 0.01)
        return contribuicao / aliq_aplicar
        
    if tipo == "unerjprev_idade":
        teto_inss = plano["ur"]
        max_025 = arredondar(teto_inss * plano["aliq_1"])
        
        if contribuicao <= max_025:
            return contribuicao / plano["aliq_1"]
        else:
            if idade_ou_tempo <= 44:
                aliq_exc = 0.03
            elif 45 <= idade_ou_tempo <= 49:
                aliq_exc = 0.04
            elif 50 <= idade_ou_tempo <= 54:
                aliq_exc = 0.05
            else: 
                aliq_exc = 0.06
            return contribuicao / aliq_exc

    if tipo == "faixas_quadruplas_fiepa":
        up = plano["up"]
        teto1 = up * 0.5
        teto2 = up * 1.0
        teto3 = up * 3.0
        
        if faixa_opcao == "Faixa 2":
            a1, a2, a3, a4 = 0.0270, 0.0450, 0.1080, 0.1350
        elif faixa_opcao == "Faixa 3":
            a1, a2, a3, a4 = 0.0240, 0.0400, 0.0960, 0.1200
        elif faixa_opcao == "Faixa 4":
            a1, a2, a3, a4 = 0.0210, 0.0350, 0.0840, 0.1050
        elif faixa_opcao == "Faixa 5":
            a1, a2, a3, a4 = 0.0180, 0.0300, 0.0720, 0.0900
        elif faixa_opcao == "Faixa 6":
            a1, a2, a3, a4 = 0.0150, 0.0250, 0.0600, 0.0750
        else: 
            a1, a2, a3, a4 = 0.0300, 0.0500, 0.1200, 0.1500
            
        max_f1 = teto1 * a1
        max_f2 = (teto2 - teto1) * a2
        max_f3 = (teto3 - teto2) * a3
        
        if contribuicao <= max_f1:
            return contribuicao / a1
        elif contribuicao <= (max_f1 + max_f2):
            return teto1 + ((contribuicao - max_f1) / a2)
        elif contribuicao <= (max_f1 + max_f2 + max_f3):
            return teto2 + ((contribuicao - max_f1 - max_f2) / a3)
        else:
            return teto3 + ((contribuicao - max_f1 - max_f2 - max_f3) / a4)

    if tipo == "faixas_univali":
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

    if tipo == "sesc_triplo_ur":
        ur = plano["ur"]
        teto1_rs = ur * plano["teto1_urs"]
        teto2_rs = ur * plano["teto2_urs"]
        
        max_c1 = teto1_rs * plano["aliq_1"]
        max_c2 = (teto2_rs * plano["aliq_2"]) - (0.4190 * ur)
        
        if contribuicao <= max_c1:
            return contribuicao / plano["aliq_1"]
        elif contribuicao <= max_c2:
            return (contribuicao + (0.4190 * ur)) / plano["aliq_2"]
        else:
            return (contribuicao + (1.3424 * ur)) / plano["aliq_3"]

    if tipo == "faixas_triplas_senai":
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
            
    if tipo == "faixas_triplas_fiema":
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
            return contribuicao / a1
        elif contribuicao <= max_f1 + max_f2:
            return teto1_rs + ((contribuicao - max_f1) / a2)
        else:
            return teto2_rs + ((contribuicao - max_f1 - max_f2) / a3)

    teto_rs = plano["ur"] * plano["teto_urs"]
    max_f1 = teto_rs * plano["aliq_1"]
    if contribuicao <= max_f1:
        return contribuicao / plano["aliq_1"]
    else:
        return teto_rs + ((contribuicao - max_f1) / plano["aliq_2"])


def calcular_salario_reverso(plano_nome, contribuicao_liquida, aliq_escolhida=None, univali_migrante="Migrante", univali_tipo="Normal", idade_ou_tempo=30, faixa_opcao="Faixa 1", is_autopatrocinio=False):
    salario_base = _calcular_salario_reverso_matematico(plano_nome, contribuicao_liquida, aliq_escolhida, univali_migrante, univali_tipo, idade_ou_tempo, faixa_opcao, is_autopatrocinio)
    if salario_base == 0.0:
        return 0.0
        
    funcao_teste = lambda s: calcular_contribuicao(plano_nome, s, aliq_escolhida, univali_migrante, univali_tipo, idade_ou_tempo, faixa_opcao, is_autopatrocinio)[0]
    return refinar_centro_arredondamento(salario_base, contribuicao_liquida, funcao_teste)


# --- MOTORES DE CÁLCULO AUTOPATROCÍNIO ---
def simular_cobranca_autopatrocinio(plano_nome, salario, aliq_escolhida=None, univali_migrante="Migrante", univali_tipo="Normal", idade_ou_tempo=30, faixa_opcao="Faixa 1", categoria_participante="Migrante"):
    contrib_pura = calcular_contribuicao(plano_nome, salario, aliq_escolhida, univali_migrante, univali_tipo, idade_ou_tempo, faixa_opcao, is_autopatrocinio=True)[0]
    
    plano = planos.get(plano_nome, {})
    tx_adm = plano.get("tx_adm", 0.0)
    tx_risco = plano.get("tx_risco_auto", plano.get("tx_risco", 0.0))
    tem_risco = plano_nome in planos_com_risco
    
    if "Sem Risco" in categoria_participante:
        tem_risco = False
        tx_risco = 0.0

    valor_risco = arredondar(salario * tx_risco) if tem_risco else 0.0
    
    if plano_nome == "UNIVALIPrevidencia":
        teto_rs = plano["ur"] * plano["teto_urs"]
        sug_f1 = arredondar(salario * plano["aliq_1"]) if salario <= teto_rs else arredondar(teto_rs * plano["aliq_1"])
        sug_f2 = 0.0
        if salario > teto_rs:
            sug_f2 = arredondar((salario - teto_rs) * 0.17)
        sugerida_total = arredondar(sug_f1 + sug_f2)
        
        contrib_patr = sugerida_total
        taxa_adm_total = arredondar((contrib_pura + contrib_patr) * tx_adm)
        return arredondar(contrib_pura + contrib_patr + taxa_adm_total)

    elif plano_nome in ["FIEMTPREV", "SENAI-PIPREV", "SESI-PIPREV"]:
        taxa_adm = arredondar((contrib_pura * 2) * tx_adm)
        contrib_patr = arredondar(contrib_pura - taxa_adm)
        return arredondar(contrib_pura + contrib_patr + taxa_adm)
        
    elif plano_nome == "UNERJPREV":
        return arredondar(contrib_pura * 2)

    elif plano_nome == "LUNELLIPREV":
        contrib_patr = arredondar(contrib_pura * 0.10)
        return arredondar(contrib_pura + contrib_patr)
        
    elif plano_nome == "SESC SC (SESCPREV)":
        taxa_adm_total = arredondar(contrib_pura * tx_adm)
        contrib_patr = 0.0
        return arredondar(contrib_pura + contrib_patr + taxa_adm_total + valor_risco)
        
    elif plano_nome == "FIEP":
        contrib_patr = contrib_pura
        if "Abaixo" in categoria_participante:
            contrib_patr = arredondar(contrib_pura * 0.50)
        taxa_adm_part = arredondar(contrib_pura * tx_adm)
        taxa_adm_patroc = arredondar(contrib_patr * tx_adm)
        taxa_adm_total = arredondar(taxa_adm_part + taxa_adm_patroc)
        return arredondar(contrib_pura + contrib_patr + taxa_adm_total + valor_risco)

    elif plano_nome in ["PREVFIEPA", "PREVIFIEA"]:
        taxa_adm_total = arredondar(contrib_pura * tx_adm)
        valor_risco = arredondar((contrib_pura - taxa_adm_total) * tx_risco) if tem_risco else 0.0
        contrib_patr = arredondar(contrib_pura - taxa_adm_total - valor_risco)
        return arredondar(contrib_pura + contrib_patr + taxa_adm_total + valor_risco)

    # Default Fallback (FIESCPREV, SENACPREV, FECOMERCIO, etc.)
    contrib_patr = contrib_pura
    taxa_adm_part = arredondar(contrib_pura * tx_adm)
    taxa_adm_patroc = arredondar(contrib_patr * tx_adm)
    taxa_adm_total = arredondar(taxa_adm_part + taxa_adm_patroc)
    
    return arredondar(contrib_pura + contrib_patr + taxa_adm_total + valor_risco)

def descobrir_salario_autopatrocinio(plano_nome, cobranca_alvo, aliq_escolhida=None, univali_migrante="Migrante", univali_tipo="Normal", idade_ou_tempo=30, faixa_opcao="Faixa 1", categoria_participante="Migrante"):
    low, high = 0.0, 1000000.0
    for _ in range(80): 
        mid = (low + high) / 2
        calc = simular_cobranca_autopatrocinio(plano_nome, mid, aliq_escolhida, univali_migrante, univali_tipo, idade_ou_tempo, faixa_opcao, categoria_participante)
        if calc < cobranca_alvo:
            low = mid
        else:
            high = mid
            
    salario_base = mid
    funcao_teste = lambda s: simular_cobranca_autopatrocinio(plano_nome, s, aliq_escolhida, univali_migrante, univali_tipo, idade_ou_tempo, faixa_opcao, categoria_participante)
    return refinar_centro_arredondamento(salario_base, cobranca_alvo, funcao_teste)


# =================================================================
# 4. NAVEGAÇÃO CENTRAL E TELA HOME
# =================================================================
PAGINAS = [
    ("Simulador Individual", "Simulador individual"),
    ("Simulador de Autopatrocínio", "Simulador de autopatrocínio"),
    ("Cálculo de Contribuição em Lote", "Cálculo de contribuição em lote"),
    ("Cálculo de Salário em Lote", "Cálculo de salário em lote"),
    ("Regras e Bases de Cálculo", "Regras e bases de cálculo"),
]


def _ir(destino):
    st.session_state['menu_selecionado'] = destino
    st.rerun()


if menu_selecionado == 'home':
    if pv.capa():
        _ir('menu')

elif menu_selecionado == 'menu':
    pv.fundo_menu()
    esq, centro, dir_ = st.columns([1, 1.6, 1.4])
    with centro:
      with st.container(key="pv_menu_card"):
        pv.logo_sidebar()
        for chave, rotulo in PAGINAS:
            if st.button(rotulo, key=f"menu_{chave}", use_container_width=True):
                _ir(chave)
        pv.rodape_sidebar()

else:
    with st.sidebar:
        pv.logo_sidebar()
        for chave, rotulo in PAGINAS:
            if st.button(rotulo, key=f"nav_{chave}", use_container_width=True):
                _ir(chave)
        if st.button("Voltar ao menu principal", key="nav_home",
                     use_container_width=True):
            _ir('menu')
        pv.rodape_sidebar()


# =================================================================
# 5. TELAS INDIVIDUAIS: ATIVO E AUTOPATROCÍNIO
# =================================================================

# -----------------------------------------------------------------
# 5.1 TELA: SIMULADOR INDIVIDUAL (ATIVO)
# -----------------------------------------------------------------
if menu_selecionado == "Simulador Individual":
    pv.titulo_pagina("Simulador Previsc")
    st.write("Selecione o plano abaixo para calcular a contribuição sugerida ou calcular o salário a partir da contribuição.")

    plano_selecionado = st.selectbox("Selecione o Plano de Previdência:", options=list(planos.keys()))
    plano_dados = planos[plano_selecionado]

    univali_migrante = "Migrante"
    univali_tipo = "Normal"
    idade_ou_tempo_input = 30
    faixa_opcao_selecionada = "Faixa 1"
    
    if plano_selecionado == "UNIVALIPrevidencia":
        col_u1, col_u2, col_u3 = st.columns(3)
        with col_u1:
            univali_migrante = st.radio("Categoria:", ["Migrante", "Não Migrante"], key="uni_cat_ativo")
            categoria_participante = univali_migrante
        with col_u2:
            univali_tipo = st.radio("Contribuição:", ["Normal", "Reduzida"], key="uni_tip_ativo")
        with col_u3:
            idade_ou_tempo_input = st.number_input("Tempo de Empresa (Anos):", min_value=0, max_value=60, value=0, step=1, key="uni_temp_ativo")
    elif plano_selecionado == "FIEP":
        st.markdown("**Selecione a Faixa Etária:**")
        categoria_participante = st.radio("Idade:", ["Abaixo de 40 anos", "Acima de 40 anos"], horizontal=True, label_visibility="collapsed")
    elif plano_selecionado == "FIEMTPREV":
        categoria_participante = "Não Migrante"
        st.info("Para o FIEMT, o cálculo adota a regra padrão de 'Não Migrante'.")
    elif plano_selecionado in ["PREVFIEPA", "PREVIFIEA"]:
        st.markdown("**Selecione a Categoria de Participação:**")
        categoria_participante = st.radio("Categoria:", ["Migrante (Com Risco)", "Sem Risco"], horizontal=True, label_visibility="collapsed", key="cat_ativo_fiepa")
    else:
        st.markdown("**Selecione a Categoria de Participação:**")
        if plano_selecionado in planos_com_risco:
            opcoes_cat = ["Migrante (Sem Risco)", "Migrante (Com Risco)", "Não Migrante (Sem Risco)", "Não Migrante (Com Risco)"]
        else:
            opcoes_cat = ["Migrante", "Não Migrante"]
            
        categoria_participante = st.radio("Categoria:", opcoes_cat, horizontal=True, label_visibility="collapsed")
            
    if plano_dados.get("tipo") == "unerjprev_idade":
        st.markdown("**Forma de preenchimento da Idade:**")
        modo_idade = st.radio("Selecione:", ["Digitar a Idade", "Data de Nascimento"], horizontal=True, label_visibility="collapsed", key="modo_idade_ativo")
        
        if modo_idade == "Digitar a Idade":
            idade_ou_tempo_input = st.number_input("Idade do Participante:", min_value=16, max_value=100, value=30, step=1, key="idade_dig_ativo")
        else:
            data_nasc = st.date_input("Data de Nascimento:", value=date(1996, 1, 1), min_value=date(1920, 1, 1), max_value=date.today(), format="DD/MM/YYYY", key="data_nasc_ativo")
            hoje = date.today()
            idade_calc = hoje.year - data_nasc.year - ((hoje.month, hoje.day) < (data_nasc.month, data_nasc.day))
            st.info(f"Idade calculada: **{idade_calc} anos**")
            idade_ou_tempo_input = idade_calc
        
    elif plano_selecionado == "PREVISC SENAI-MA":
        st.markdown("""
        **Escolha a faixa de contribuição desejada:**
        | Faixa | Salários até R$ 2.907,14 | Salários entre R$2.907,14 e R$5.000,00 | Salários acima de R$ 5.000,00 |
        |:---:|:---:|:---:|:---:|
        | **1** | 2,10% | 3,50% | 16,10% |
        | **2** | 1,80% | 3,00% | 13,80% |
        | **3** | 1,50% | 2,50% | 11,50% |
        """)
        faixa_opcao_selecionada = st.radio("Selecione a Faixa:", ["Faixa 1", "Faixa 2", "Faixa 3"], horizontal=True, key="faixa_fiema")
        
    elif plano_selecionado in ["PREVFIEPA", "PREVIFIEA"]:
        st.markdown("""
        **Escolha a faixa de contribuição desejada:**
        | FAIXA | ATÉ 1/2 UP | ENTRE 1/2 E 1 UP | ENTRE 1 E 3 UP | EXCEDENTE A 3 UP |
        |:---:|:---:|:---:|:---:|:---:|
        | **1** | 3,00% | 5,00% | 12,00% | 15,00% |
        | **2** | 2,70% | 4,50% | 10,80% | 13,50% |
        | **3** | 2,40% | 4,00% | 9,60% | 12,00% |
        | **4** | 2,10% | 3,50% | 8,40% | 10,50% |
        | **5** | 1,80% | 3,00% | 7,20% | 9,00% |
        | **6** | 1,50% | 2,50% | 6,00% | 7,50% |
        """)
        faixa_opcao_selecionada = st.radio("Selecione a Faixa:", ["Faixa 1", "Faixa 2", "Faixa 3", "Faixa 4", "Faixa 5", "Faixa 6"], horizontal=True, key=f"faixa_{plano_selecionado}_ativo")

    st.divider()
    aba_normal, aba_reversa = st.tabs(["Cálculo de Contribuição", "Cálculo de salário"])

    with aba_normal:
        
        salario_input_str = st.text_input("Digite o Salário Atual (R$):", value="0,00", key="sal_normal")
        salario_input = converter_br(salario_input_str)
        
        aliq_escolhida = None
        if plano_dados.get("tipo") in ["up_sem_teto", "lunelliprev"]:
            if plano_dados.get("tipo") == "up_sem_teto":
                st.info(f"A UP atual deste plano é de R$ {formatar_br(plano_dados['ur'])}")
                if salario_input > 0:
                    qtd_ups = salario_input / plano_dados["ur"]
                    st.write(f"O seu salário equivale a **{formatar_br(qtd_ups)} UPs**.")
            elif plano_dados.get("tipo") == "lunelliprev":
                st.info("A Contribuição Básica é de livre escolha do participante, respeitando o mínimo obrigatório de 1% sobre o Salário.")
            
            aliq_padrao = formatar_br(plano_dados["aliq_1"] * 100)
            aliq_input_str = st.text_input("Alíquota de Contribuição (%):", value=aliq_padrao, key="aliq_normal")
            aliq_escolhida = converter_br(aliq_input_str) / 100
            
        if plano_dados.get("tipo") == "unerjprev_idade":
            st.info(f"O Teto do INSS (1 UR) utilizado é de R$ {formatar_br(plano_dados['ur'])}")
        if plano_selecionado == "SENAI-PIPREV":
            st.info(f"A UR atual adotada para o plano SENAI-PI é de R$ {formatar_br(plano_dados['ur'])}")
        if plano_selecionado == "UNIVALIPrevidencia":
            st.info(f"A UR atual adotada para o plano UNIVALIPrevidencia é de R$ {formatar_br(plano_dados['ur'])}")
        if plano_selecionado == "SESI-PIPREV":
            st.info(f"A SP atual adotada para o plano SESI-PI é de R$ {formatar_br(plano_dados['ur'])}")
        if plano_selecionado in ["PREVFIEPA", "PREVIFIEA"]:
            st.info(f"A UP atual adotada para o plano {plano_selecionado} é de R$ {formatar_br(plano_dados['up'])}")
        
        if st.button("Gerar cálculo", type="primary"):
            if salario_input > 0:
                total, f1, f2, f3, superavit = calcular_contribuicao(plano_selecionado, salario_input, aliq_escolhida, univali_migrante, univali_tipo, idade_ou_tempo_input, faixa_opcao_selecionada)
                
                if total == 0:
                    st.info("Este plano utiliza uma regra de Mínimo Fixo. Consulte o regulamento.")
                
                elif plano_dados.get("tipo") == "unerjprev_idade":
                    st.success(f"### Contribuição Sugerida (Participante): R$ {formatar_br(total)}")
                    col_f1, col_f2 = st.columns(2)
                    teto_inss = plano_dados["ur"]
                    if salario_input <= teto_inss:
                        aliq_show = plano_dados["aliq_1"] * 100
                    else:
                        if idade_ou_tempo_input <= 44: aliq_show = 3.0
                        elif 45 <= idade_ou_tempo_input <= 49: aliq_show = 4.0
                        elif 50 <= idade_ou_tempo_input <= 54: aliq_show = 5.0
                        else: aliq_show = 6.0
                    col_f1.metric("Alíquota Aplicada (Base Inteira)", f"{formatar_br(aliq_show)}%")
                    col_f2.metric("Valor Contribuição", f"R$ {formatar_br(total)}")
                elif plano_dados.get("tipo") == "up_sem_teto":
                    st.success(f"### Contribuição Sugerida (Participante): R$ {formatar_br(total)}")
                elif plano_dados.get("tipo") == "lunelliprev":
                    st.success(f"### Contribuição Sugerida (Participante): R$ {formatar_br(total)}")
                    col_f1, col_f2 = st.columns(2)
                    col_f1.metric("Alíquota Aplicada", f"{formatar_br(max(aliq_escolhida if aliq_escolhida else 0.01, 0.01) * 100)}%")
                    col_f2.metric("Valor Base", f"R$ {formatar_br(total)}")
                elif plano_selecionado == "UNIVALIPrevidencia":
                    st.success(f"### Contribuição Sugerida (Participante): R$ {formatar_br(total)}")
                    col_f1, col_f2, col_f3 = st.columns(3)
                    col_f1.metric(f"Faixa Base (Até R$ {formatar_br(plano_dados['ur'] * 8)})", f"R$ {formatar_br(f1)}")
                    col_f2.metric("Faixa Excedente", f"R$ {formatar_br(f2)}")
                    col_f3.metric("Contribuição Pura", f"R$ {formatar_br(total)}")
                elif plano_selecionado in ["PREVFIEPA", "PREVIFIEA"]:
                    st.success(f"### Contribuição Sugerida (Participante): R$ {formatar_br(total)}")
                    col_f1, col_f2, col_f3 = st.columns(3)
                    col_f1.metric("Faixa Base (Até 0,5 UP)", f"R$ {formatar_br(f1)}")
                    col_f2.metric("Faixas Intermédias (0,5 a 3 UPs)", f"R$ {formatar_br(f2)}")
                    col_f3.metric("Faixa Topo (> 3 UPs)", f"R$ {formatar_br(f3)}")
                elif plano_selecionado == "PREVISC SENAI-MA":
                    st.success(f"### Contribuição Sugerida (Participante): R$ {formatar_br(total)}")
                    col_f1, col_f2, col_f3 = st.columns(3)
                    col_f1.metric("Faixa Base (Até R$ 2.907,14)", f"R$ {formatar_br(f1)}")
                    col_f2.metric("Faixa Intermediária (Até R$ 5.000,00)", f"R$ {formatar_br(f2)}")
                    col_f3.metric("Faixa Topo (Excedente)", f"R$ {formatar_br(f3)}")
                elif plano_selecionado == "SESC SC (SESCPREV)":
                    st.success(f"### Contribuição Sugerida (Participante): R$ {formatar_br(total)}")
                    st.info("Cálculo realizado via fator de Parcela a Deduzir.")
                    if f3 > 0:
                        col_f1, col_f2, col_f3 = st.columns(3)
                        col_f1.metric("Valor Base", f"R$ {formatar_br(f1)}")
                        col_f2.metric("Diferença Faixa 2", f"R$ {formatar_br(f2)}")
                        col_f3.metric("Diferença Faixa 3", f"R$ {formatar_br(f3)}")
                    elif f2 > 0:
                        col_f1, col_f2 = st.columns(2)
                        col_f1.metric("Valor Base", f"R$ {formatar_br(f1)}")
                        col_f2.metric("Diferença Faixa 2", f"R$ {formatar_br(f2)}")
                elif plano_dados.get("tipo") == "sesi_piprev_deducao":
                    st.success(f"### Contribuição Sugerida (Líquida): R$ {formatar_br(total)}")
                    st.info("Cálculo realizado via Fórmula Direta de Dedução do SESI.")
                    col_f1, col_f2 = st.columns(2)
                    col_f1.metric("Contribuição Pura", f"R$ {formatar_br(f1)}")
                    col_f2.metric("Desconto Taxa Adm (2,18%)", f"- R$ {formatar_br(f2)}")
                else:
                    st.success(f"### Contribuição Sugerida (Participante): R$ {formatar_br(total)}")
                    if superavit > 0:
                        st.info(f"Desconto de Superávit Participante ({formatar_br(plano_dados.get('superavit', 0)*100)}%): **- R$ {formatar_br(superavit)}**")
                    if f3 > 0:
                        col_f1, col_f2, col_f3 = st.columns(3)
                        col_f1.metric("Faixa 1", f"R$ {formatar_br(f1)}")
                        col_f2.metric("Faixa 2", f"R$ {formatar_br(f2)}")
                        col_f3.metric("Faixa 3 (Excedente)", f"R$ {formatar_br(f3)}")
                    elif f2 > 0:
                        col_f1, col_f2 = st.columns(2)
                        col_f1.metric("Faixa 1 (Até Teto)", f"R$ {formatar_br(f1)}")
                        col_f2.metric("Faixa 2 (Excedente)", f"R$ {formatar_br(f2)}")
                        
                tx_adm_plano = plano_dados.get("tx_adm", 0.0)
                tx_risco_plano = plano_dados.get("tx_risco", 0.0)
                
                tem_risco_escolhido = "(Com Risco)" in categoria_participante
                
                if plano_selecionado in ["PREVFIEPA", "PREVIFIEA"] and "Sem Risco" in categoria_participante:
                    tem_risco_escolhido = False

                valor_risco = arredondar(salario_input * tx_risco_plano) if tem_risco_escolhido else 0.0
                
                if plano_selecionado == "UNIVALIPrevidencia":
                    if (univali_migrante == "Não Migrante" and idade_ou_tempo_input >= 35) or \
                       (univali_migrante == "Migrante" and idade_ou_tempo_input >= 30):
                        c_patr_bruta = 0.0
                        taxa_adm_total = arredondar(total * tx_adm_plano)
                        taxa_adm_patroc = 0.0
                        c_patr_exibir = 0.0
                    else:
                        teto_rs = plano_dados["ur"] * plano_dados["teto_urs"]
                        sug_f1 = arredondar(salario_input * plano_dados["aliq_1"]) if salario_input <= teto_rs else arredondar(teto_rs * plano_dados["aliq_1"])
                        sug_f2 = 0.0
                        if salario_input > teto_rs:
                            sug_f2 = arredondar((salario_input - teto_rs) * 0.17) if univali_migrante == "Não Migrante" else arredondar((salario_input - teto_rs) * 0.14)
                        sugerida_total = arredondar(sug_f1 + sug_f2)
                        
                        fator_tempo = 1.0 if idade_ou_tempo_input >= 10 else 0.5
                        c_patr_bruta = arredondar(sugerida_total * fator_tempo)
                        
                        taxa_adm_part = arredondar(total * tx_adm_plano)
                        taxa_adm_patroc = 0.0 if univali_migrante == "Migrante" else arredondar(c_patr_bruta * tx_adm_plano)
                        taxa_adm_total = arredondar(taxa_adm_part + taxa_adm_patroc)
                        
                        c_patr_exibir = arredondar(c_patr_bruta - taxa_adm_patroc)
                
                elif plano_selecionado == "SENAI-PIPREV":
                    c_patr_bruta = arredondar(total + superavit)
                    taxa_adm_total = arredondar((c_patr_bruta * 2) * tx_adm_plano)
                    c_patr_exibir = arredondar(total - taxa_adm_total)

                elif plano_selecionado in ["PREVFIEPA", "PREVIFIEA"]:
                    c_patr_bruta = arredondar(total + superavit)
                    taxa_adm_total = arredondar(c_patr_bruta * tx_adm_plano)
                    
                    valor_risco = arredondar((c_patr_bruta - taxa_adm_total) * tx_risco_plano) if tem_risco_escolhido else 0.0
                    
                    c_patr_exibir = arredondar(c_patr_bruta - taxa_adm_total - valor_risco)

                else:
                    if plano_dados.get("tipo") == "sesi_piprev_deducao":
                        c_patr_bruta = f1
                    else:
                        c_patr_bruta = arredondar(total + superavit)
                    
                    if plano_selecionado == "FIEP":
                        if "Abaixo" in categoria_participante:
                            c_patr_bruta = arredondar(c_patr_bruta * 0.50)

                    taxa_adm_part = arredondar(total * tx_adm_plano)
                    taxa_adm_patroc = arredondar(c_patr_bruta * tx_adm_plano)
                    taxa_adm_total = arredondar(taxa_adm_part + taxa_adm_patroc)
                    
                    if plano_selecionado == "LUNELLIPREV":
                        c_patr_exibir = arredondar(c_patr_bruta * 0.10)
                    elif plano_selecionado == "UNERJPREV":
                        c_patr_exibir = c_patr_bruta
                    elif plano_selecionado == "SESI-PIPREV":
                        c_patr_exibir = arredondar(c_patr_bruta - taxa_adm_patroc)
                    else:
                        if "Não Migrante" in categoria_participante:
                            c_patr_exibir = arredondar(c_patr_bruta - taxa_adm_total - valor_risco)
                        else:
                            c_patr_exibir = c_patr_bruta
                    
                st.divider()
                st.markdown("#### 🏢 Contrapartida da Patrocinadora e Taxas")
                
                if plano_selecionado == "LUNELLIPREV":
                    st.caption("⚠️ *A patrocinadora (Lunelli) aporta 10% fixo sobre a contribuição do participante, acrescido de um rateio anual variável que depende do fundo global da empresa. O simulador projeta apenas a cota fixa garantida.*")
                
                col_p1, col_p2, col_p3 = st.columns(3)
                
                col_p1.metric("Contrib. Patrocinadora (Líquida)", f"R$ {formatar_br(c_patr_exibir)}")
                
                if plano_selecionado in ["LUNELLIPREV", "UNERJPREV"]:
                    col_p2.metric("Taxa Adm Total", "0% (Cobrado do saldo)")
                elif plano_selecionado == "UNIVALIPrevidencia":
                    col_p2.metric("Taxa Adm Total", f"R$ {formatar_br(taxa_adm_total)}")
                elif tx_adm_plano > 0:
                    if plano_selecionado == "FIEP" and "Abaixo" in categoria_participante:
                        col_p2.metric("Taxa Adm Total (Proporcional)", f"R$ {formatar_br(taxa_adm_total)}")
                    elif plano_selecionado == "SENAI-PIPREV":
                        col_p2.metric(f"Taxa Adm Total ({formatar_br(tx_adm_plano*100)}% x 2)", f"R$ {formatar_br(taxa_adm_total)}")
                    elif plano_selecionado in ["PREVFIEPA", "PREVIFIEA"]:
                        col_p2.metric(f"Taxa Adm Total ({formatar_br(tx_adm_plano*100)}%)", f"R$ {formatar_br(taxa_adm_total)}")
                    else:
                        col_p2.metric(f"Taxa Adm Total ({formatar_br(tx_adm_plano*100)}% x 2)", f"R$ {formatar_br(taxa_adm_total)}")
                else:
                    col_p2.metric("Taxa Adm Total", "0% (Não configurada)")
                    
                if tem_risco_escolhido:
                    if tx_risco_plano > 0:
                        col_p3.metric(f"Taxa Risco ({formatar_br(tx_risco_plano*100)}%)", f"R$ {formatar_br(valor_risco)}")
                    else:
                        col_p3.metric("Taxa Risco", "Sem Risco")
                else:
                    col_p3.metric("Taxa Risco", "Sem Risco")

            else:
                st.warning("Insira um salário válido.")

    with aba_reversa:
        
        contrib_input_str = st.text_input("Digite a Contribuição Alvo (R$):", value="0,00", key="contrib_reversa")
        contrib_input = converter_br(contrib_input_str)
        
        aliq_escolhida_rev = None
        if plano_dados.get("tipo") in ["up_sem_teto", "lunelliprev"]:
            aliq_padrao_rev = formatar_br(plano_dados["aliq_1"] * 100)
            aliq_input_rev_str = st.text_input("Alíquota Utilizada (%):", value=aliq_padrao_rev, key="aliq_rev")
            aliq_escolhida_rev = converter_br(aliq_input_rev_str) / 100
            
        if st.button("Descobrir Salário", type="primary"):
            if contrib_input > 0:
                salario_descob = calcular_salario_reverso(plano_selecionado, contrib_input, aliq_escolhida_rev, categoria_participante, univali_tipo, idade_ou_tempo_input, faixa_opcao_selecionada)
                if salario_descob == 0:
                    st.info("O cálculo de salário para este plano requer alinhamento de variáveis complexas.")
                else:
                    st.success(f"### Salário Exato Necessário: R$ {formatar_br(salario_descob)}")
            else:
                st.warning("Insira uma contribuição válida.")

# -----------------------------------------------------------------
# 5.2 TELA: SIMULADOR AUTOPATROCÍNIO
# -----------------------------------------------------------------
elif menu_selecionado == "Simulador de Autopatrocínio":
    pv.titulo_pagina("👤 Simulador de Autopatrocínio")
    st.write("Verifique a cobrança a partir do salário ou faça o cálculo reverso (Gross-up) a partir do valor desejado da cobrança mensal.")

    plano_selecionado = st.selectbox("Selecione o Plano de Previdência:", options=list(planos.keys()), key="sel_plano_auto")
    plano_dados = planos[plano_selecionado]

    univali_migrante = "Migrante"
    univali_tipo = "Normal"
    idade_ou_tempo_input = 30
    faixa_opcao_selecionada = "Faixa 1"
    
    # As opções originais do Autopatrocínio
    st.markdown("**Selecione a Categoria de Participação:**")
    if plano_selecionado in planos_com_risco:
        opcoes_cat = ["Migrante (Sem Risco)", "Migrante (Com Risco)", "Não Migrante (Sem Risco)", "Não Migrante (Com Risco)"]
    else:
        opcoes_cat = ["Migrante", "Não Migrante"]
        
    categoria_participante = st.radio("Categoria:", opcoes_cat, horizontal=True, label_visibility="collapsed", key="cat_auto_geral")

    if plano_selecionado == "UNIVALIPrevidencia":
        univali_migrante = "Não Migrante"
        univali_tipo = "Normal"
        idade_ou_tempo_input = 10
        st.info("Para o Autopatrocínio, o plano UNIVALI utiliza a regra fixa de categoria 'Não Migrante - Normal' com contrapartida integral (100%).")
        
    elif plano_dados.get("tipo") == "unerjprev_idade":
        st.markdown("**Forma de preenchimento da Idade:**")
        modo_idade = st.radio("Selecione:", ["Digitar a Idade", "Data de Nascimento"], horizontal=True, label_visibility="collapsed", key="modo_idade_auto")
        
        if modo_idade == "Digitar a Idade":
            idade_ou_tempo_input = st.number_input("Idade do Participante:", min_value=16, max_value=100, value=30, step=1, key="idade_dig_auto")
        else:
            data_nasc = st.date_input("Data de Nascimento:", value=date(1996, 1, 1), min_value=date(1920, 1, 1), max_value=date.today(), format="DD/MM/YYYY", key="data_nasc_auto")
            hoje = date.today()
            idade_calc = hoje.year - data_nasc.year - ((hoje.month, hoje.day) < (data_nasc.month, data_nasc.day))
            st.info(f"Idade calculada: **{idade_calc} anos**")
            idade_ou_tempo_input = idade_calc
        
    if plano_selecionado == "PREVISC SENAI-MA":
        st.markdown("""
        **Escolha a faixa de contribuição desejada:**
        | Faixa | Salários até R$ 2.907,14 | Salários entre R$ 2.907,14 e R$ 5.000,00 | Salários acima de R$ 5.000,00 |
        |:---:|:---:|:---:|:---:|
        | **1** | 2,10% | 3,50% | 16,10% |
        | **2** | 1,80% | 3,00% | 13,80% |
        | **3** | 1,50% | 2,50% | 11,50% |
        """)
        faixa_opcao_selecionada = st.radio("Selecione a Faixa:", ["Faixa 1", "Faixa 2", "Faixa 3"], horizontal=True, key="faixa_fiema_auto")
        
    elif plano_selecionado in ["PREVFIEPA", "PREVIFIEA"]:
        st.markdown("""
        **Escolha a faixa de contribuição desejada:**
        | FAIXA | ATÉ 1/2 UP | ENTRE 1/2 E 1 UP | ENTRE 1 E 3 UP | EXCEDENTE A 3 UP |
        |:---:|:---:|:---:|:---:|:---:|
        | **1** | 3,00% | 5,00% | 12,00% | 15,00% |
        | **2** | 2,70% | 4,50% | 10,80% | 13,50% |
        | **3** | 2,40% | 4,00% | 9,60% | 12,00% |
        | **4** | 2,10% | 3,50% | 8,40% | 10,50% |
        | **5** | 1,80% | 3,00% | 7,20% | 9,00% |
        | **6** | 1,50% | 2,50% | 6,00% | 7,50% |
        """)
        faixa_opcao_selecionada = st.radio("Selecione a Faixa:", ["Faixa 1", "Faixa 2", "Faixa 3", "Faixa 4", "Faixa 5", "Faixa 6"], horizontal=True, key=f"faixa_{plano_selecionado}_auto")

    st.divider()

    aba_normal_auto, aba_reversa_auto = st.tabs(["Cálculo de Contribuição", "Cálculo de salário"])

    with aba_normal_auto:
        
        salario_input_str = st.text_input("Digite o Salário Atual (R$):", value="0,00", key="sal_auto")
        salario_input = converter_br(salario_input_str)
        
        aliq_escolhida_auto = None
        if plano_dados.get("tipo") in ["up_sem_teto", "lunelliprev"]:
            if plano_dados.get("tipo") == "up_sem_teto":
                st.info(f"A UP atual deste plano é de R$ {formatar_br(plano_dados['ur'])}")
            elif plano_dados.get("tipo") == "lunelliprev":
                st.info("A Contribuição Básica é de livre escolha do participante, respeitando o mínimo obrigatório de 1% sobre o Salário.")
                
            aliq_padrao_auto = formatar_br(plano_dados["aliq_1"] * 100)
            aliq_input_auto_str = st.text_input("Alíquota de Contribuição (%):", value=aliq_padrao_auto, key="aliq_auto_norm")
            aliq_escolhida_auto = converter_br(aliq_input_auto_str) / 100
            
        if plano_dados.get("tipo") == "unerjprev_idade":
            st.info(f"O Teto do INSS (1 UR) utilizado é de R$ {formatar_br(plano_dados['ur'])}")
        if plano_selecionado in ["PREVFIEPA", "PREVIFIEA"]:
            st.info(f"A UP atual adotada para o plano {plano_selecionado} é de R$ {formatar_br(plano_dados['up'])}")
            
        if st.button("Gerar cálculo", type="primary"):
            if salario_input > 0:
                tx_adm_plano = plano_dados.get("tx_adm", 0.0)
                tx_risco_plano = plano_dados.get("tx_risco_auto", plano_dados.get("tx_risco", 0.0))
                tem_risco = "(Com Risco)" in categoria_participante
                
                contrib_pura, f1, f2, f3, superavit = calcular_contribuicao(plano_selecionado, salario_input, aliq_escolhida_auto, univali_migrante, univali_tipo, idade_ou_tempo_input, faixa_opcao_selecionada, is_autopatrocinio=True)
                
                if plano_selecionado == "UNIVALIPrevidencia":
                    teto_rs = plano_dados["ur"] * plano_dados["teto_urs"]
                    sug_f1 = arredondar(salario_input * plano_dados["aliq_1"]) if salario_input <= teto_rs else arredondar(teto_rs * plano_dados["aliq_1"])
                    sug_f2 = 0.0
                    if salario_input > teto_rs:
                        sug_f2 = arredondar((salario_input - teto_rs) * 0.17)
                    sugerida_total = arredondar(sug_f1 + sug_f2)
                    
                    contrib_patr = sugerida_total
                    taxa_adm_total = arredondar((contrib_pura + contrib_patr) * tx_adm_plano)
                    total_cobranca = arredondar(contrib_pura + contrib_patr + taxa_adm_total)
                    
                    st.success(f"### Cobrança Mensal Total (Boleto): R$ {formatar_br(total_cobranca)}")
                    st.markdown("### Composição do Boleto")
                    col_b1, col_b2, col_b3 = st.columns(3)
                    col_b1.metric("Contrib. Participante", f"R$ {formatar_br(contrib_pura)}")
                    col_b2.metric("Contrib. Patrocinadora", f"R$ {formatar_br(contrib_patr)}")
                    col_b3.metric("Taxa Adm Total", f"R$ {formatar_br(taxa_adm_total)}")

                elif plano_selecionado in ["FIEMTPREV", "SENAI-PIPREV", "SESI-PIPREV"]:
                    taxa_adm_total = arredondar((contrib_pura * 2) * tx_adm_plano)
                    contrib_patr = arredondar(contrib_pura - taxa_adm_total)
                    total_cobranca = arredondar(contrib_pura + contrib_patr + taxa_adm_total)
                    
                    st.success(f"### Cobrança Mensal Total (Boleto): R$ {formatar_br(total_cobranca)}")
                    st.markdown("### Composição do Boleto")
                    col_b1, col_b2, col_b3 = st.columns(3)
                    col_b1.metric("Contrib. Participante", f"R$ {formatar_br(contrib_pura)}")
                    col_b2.metric("Contrib. Patrocinadora", f"R$ {formatar_br(contrib_patr)}")
                    col_b3.metric(f"Taxa Adm ({formatar_br(tx_adm_plano * 100)}% x 2)", f"R$ {formatar_br(taxa_adm_total)}")

                elif plano_selecionado in ["PREVFIEPA", "PREVIFIEA"]:
                    taxa_adm_total = arredondar(contrib_pura * tx_adm_plano)
                    valor_risco = arredondar((contrib_pura - taxa_adm_total) * tx_risco_plano) if tem_risco else 0.0
                    contrib_patr = arredondar(contrib_pura - taxa_adm_total - valor_risco)
                    total_cobranca = arredondar(contrib_pura + contrib_patr + taxa_adm_total + valor_risco)
                    
                    st.success(f"### Cobrança Mensal Total (Boleto): R$ {formatar_br(total_cobranca)}")
                    
                    st.markdown("#### Detalhamento da Contribuição Equivalente (Participante)")
                    col_f1, col_f2, col_f3 = st.columns(3)
                    col_f1.metric("Faixa Base (Até 0,5 UP)", f"R$ {formatar_br(f1)}")
                    col_f2.metric("Faixas Intermédias", f"R$ {formatar_br(f2)}")
                    col_f3.metric("Faixa Topo (> 3 UPs)", f"R$ {formatar_br(f3)}")
                    
                    st.markdown("### Composição do Boleto")
                    col_b1, col_b2, col_b3, col_b4 = st.columns(4)
                    col_b1.metric("Contrib. Participante", f"R$ {formatar_br(contrib_pura)}")
                    col_b2.metric("Contrib. Patrocinadora", f"R$ {formatar_br(contrib_patr)}")
                    
                    if tx_adm_plano > 0:
                        col_b3.metric(f"Taxa Adm ({formatar_br(tx_adm_plano * 100)}%)", f"R$ {formatar_br(taxa_adm_total)}")
                    else:
                        col_b3.metric("Taxa Adm", "0% (Não config.)")
                        
                    if tem_risco:
                        col_b4.metric(f"Taxa Risco ({formatar_br(tx_risco_plano * 100)}%)", f"R$ {formatar_br(valor_risco)}")
                    else:
                        col_b4.metric("Taxa Risco", "Sem Risco")

                elif plano_selecionado == "UNERJPREV":
                    contrib_patr = contrib_pura
                    total_cobranca = arredondar(contrib_pura + contrib_patr)
                    
                    st.success(f"### Cobrança Mensal Total (Boleto): R$ {formatar_br(total_cobranca)}")
                    
                    st.markdown("#### Detalhamento da Contribuição Equivalente (Participante)")
                    col_f1, col_f2 = st.columns(2)
                    teto_inss = plano_dados["ur"]
                    if salario_input <= teto_inss:
                        aliq_show = plano_dados["aliq_1"] * 100
                    else:
                        if idade_ou_tempo_input <= 44: aliq_show = 3.0
                        elif 45 <= idade_ou_tempo_input <= 49: aliq_show = 4.0
                        elif 50 <= idade_ou_tempo_input <= 54: aliq_show = 5.0
                        else: aliq_show = 6.0
                    col_f1.metric("Alíquota Aplicada (Base Inteira)", f"{formatar_br(aliq_show)}%")
                    col_f2.metric("Contribuição Pura (Participante)", f"R$ {formatar_br(contrib_pura)}")
                    
                    st.markdown("### Composição do Boleto")
                    col_b1, col_b2, col_b3 = st.columns(3)
                    col_b1.metric("Contrib. Participante", f"R$ {formatar_br(contrib_pura)}")
                    col_b2.metric("Contrib. Patrocinadora", f"R$ {formatar_br(contrib_patr)}")
                    col_b3.metric("Taxas (Adm/Risco)", "Isento no Boleto*")
                    st.caption("*A taxa administrativa é cobrada diretamente do saldo/patrimônio (0,85% a.a.).")

                elif plano_selecionado == "LUNELLIPREV":
                    contrib_patr = arredondar(contrib_pura * 0.10)
                    total_cobranca = arredondar(contrib_pura + contrib_patr)
                    
                    st.success(f"### Cobrança Mensal Total (Boleto): R$ {formatar_br(total_cobranca)}")
                    st.caption("⚠️ *O Autopatrocinado assume a sua parte e a contrapartida fixa de 10% da patrocinadora. Demais rateios globais não se aplicam.*")
                    
                    st.markdown("### Composição do Boleto")
                    col_b1, col_b2, col_b3 = st.columns(3)
                    col_b1.metric("Contrib. Participante", f"R$ {formatar_br(contrib_pura)}")
                    col_b2.metric("Contrib. Patrocinadora (10%)", f"R$ {formatar_br(contrib_patr)}")
                    col_b3.metric("Taxas (Adm)", "Isento no Boleto*")
                    st.caption("*As taxas administrativas (0,50%) são debitadas diretamente do saldo do fundo (recursos garantidores) anualmente.")
                    
                else:
                    valor_risco = arredondar(salario_input * tx_risco_plano) if tem_risco else 0.0
                    
                    if plano_dados.get("base_adm_com_risco", False):
                        valor_adm = arredondar((contrib_pura + valor_risco) * tx_adm_plano)
                    else:
                        valor_adm = arredondar(contrib_pura * tx_adm_plano)
                    
                    total_cobranca = arredondar(contrib_pura + valor_adm + valor_risco)
                    
                    st.success(f"### Cobrança Mensal Total (Boleto): R$ {formatar_br(total_cobranca)}")
                    
                    st.markdown("### Composição do Boleto")
                    col_b1, col_b2, col_b3 = st.columns(3)
                    col_b1.metric("Contribuição Pura", f"R$ {formatar_br(contrib_pura)}")
                    
                    if tx_adm_plano > 0:
                        col_b2.metric(f"Taxa Administração ({formatar_br(tx_adm_plano * 100)}%)", f"R$ {formatar_br(valor_adm)}")
                    else:
                        col_b2.metric("Taxa Administração", "0% (Não config.)")
                        
                    if tem_risco:
                        col_b3.metric(f"Taxa Risco ({formatar_br(tx_risco_plano * 100)}%)", f"R$ {formatar_br(valor_risco)}")
                    else:
                        col_b3.metric("Taxa Risco", "Sem Risco")
                
            else:
                st.warning("Insira um salário válido.")

    with aba_reversa_auto:
        st.subheader("Descobrir Salário a partir do Boleto Desejado")
        
        cobranca_input_str = st.text_input("Digite o Valor do Boleto Mensal (R$):", value="0,00", key="cobranca_auto_rev")
        cobranca_input = converter_br(cobranca_input_str)
            
        aliq_escolhida_auto_rev = None
        if plano_dados.get("tipo") in ["up_sem_teto", "lunelliprev"]:
            aliq_padrao_auto_rev = formatar_br(plano_dados["aliq_1"] * 100)
            aliq_input_auto_rev_str = st.text_input("Alíquota Utilizada (%):", value=aliq_padrao_auto_rev, key="aliq_auto_rev")
            aliq_escolhida_auto_rev = converter_br(aliq_input_auto_rev_str) / 100
            
        if st.button("Calcular Reversão", type="primary"):
            if cobranca_input > 0:
                tx_adm_plano = plano_dados.get("tx_adm", 0.0)
                tx_risco_plano = plano_dados.get("tx_risco_auto", plano_dados.get("tx_risco", 0.0))
                tem_risco = "(Com Risco)" in categoria_participante
                
                if tx_adm_plano == 0.0 and tx_risco_plano == 0.0 and plano_selecionado not in ["FIEMTPREV", "PREVFIEPA", "PREVIFIEA", "LUNELLIPREV", "UNERJPREV"]:
                    st.warning("⚠️ Atenção: As taxas de administração e risco deste plano não estão cadastradas no sistema.")
                
                salario_encontrado = descobrir_salario_autopatrocinio(plano_selecionado, cobranca_input, aliq_escolhida_auto_rev, univali_migrante, univali_tipo, idade_ou_tempo_input, faixa_opcao_selecionada)
                
                if salario_encontrado > 0:
                    contrib_pura, f1, f2, f3, superavit = calcular_contribuicao(plano_selecionado, salario_encontrado, aliq_escolhida_auto_rev, univali_migrante, univali_tipo, idade_ou_tempo_input, faixa_opcao_selecionada, is_autopatrocinio=True)
                    
                    if plano_selecionado == "UNIVALIPrevidencia":
                        teto_rs = plano_dados["ur"] * plano_dados["teto_urs"]
                        sug_f1 = arredondar(salario_encontrado * plano_dados["aliq_1"]) if salario_encontrado <= teto_rs else arredondar(teto_rs * plano_dados["aliq_1"])
                        sug_f2 = 0.0
                        if salario_encontrado > teto_rs:
                            sug_f2 = arredondar((salario_encontrado - teto_rs) * 0.17)
                        sugerida_total = arredondar(sug_f1 + sug_f2)
                        
                        contrib_patr = sugerida_total
                        taxa_adm_total = arredondar((contrib_pura + contrib_patr) * tx_adm_plano)
                        
                        st.success(f"### Salário Correspondente Necessário: R$ {formatar_br(salario_encontrado)}")
                        st.markdown("### Composição do Boleto")
                        col_b1, col_b2, col_b3 = st.columns(3)
                        col_b1.metric("Contrib. Participante", f"R$ {formatar_br(contrib_pura)}")
                        col_b2.metric("Contrib. Patrocinadora", f"R$ {formatar_br(contrib_patr)}")
                        col_b3.metric("Taxa Adm Total", f"R$ {formatar_br(taxa_adm_total)}")

                    elif plano_selecionado in ["FIEMTPREV", "SENAI-PIPREV", "SESI-PIPREV"]:
                        taxa_adm_total = arredondar((contrib_pura * 2) * tx_adm_plano)
                        contrib_patr = arredondar(contrib_pura - taxa_adm_total)
                        
                        st.success(f"### Salário Correspondente Necessário: R$ {formatar_br(salario_encontrado)}")
                        st.markdown("### Composição do Boleto")
                        col_b1, col_b2, col_b3 = st.columns(3)
                        col_b1.metric("Contrib. Participante", f"R$ {formatar_br(contrib_pura)}")
                        col_b2.metric("Contrib. Patrocinadora", f"R$ {formatar_br(contrib_patr)}")
                        col_b3.metric(f"Taxa Adm ({formatar_br(tx_adm_plano * 100)}% x 2)", f"R$ {formatar_br(taxa_adm_total)}")

                    elif plano_selecionado in ["PREVFIEPA", "PREVIFIEA"]:
                        taxa_adm_total = arredondar(contrib_pura * tx_adm_plano)
                        valor_risco = arredondar((contrib_pura - taxa_adm_total) * tx_risco_plano) if tem_risco else 0.0
                        contrib_patr = arredondar(contrib_pura - taxa_adm_total - valor_risco)
                        
                        st.success(f"### Salário Correspondente Necessário: R$ {formatar_br(salario_encontrado)}")
                        
                        st.markdown("#### Detalhamento da Contribuição Equivalente (Participante)")
                        col_f1, col_f2, col_f3 = st.columns(3)
                        col_f1.metric("Faixa Base (Até 0,5 UP)", f"R$ {formatar_br(f1)}")
                        col_f2.metric("Faixas Intermédias", f"R$ {formatar_br(f2)}")
                        col_f3.metric("Faixa Topo (> 3 UPs)", f"R$ {formatar_br(f3)}")
                        
                        st.markdown("### Composição do Boleto")
                        col_b1, col_b2, col_b3, col_b4 = st.columns(4)
                        col_b1.metric("Contrib. Participante", f"R$ {formatar_br(contrib_pura)}")
                        col_b2.metric("Contrib. Patrocinadora", f"R$ {formatar_br(contrib_patr)}")
                        
                        if tx_adm_plano > 0:
                            col_b3.metric(f"Taxa Adm ({formatar_br(tx_adm_plano * 100)}%)", f"R$ {formatar_br(taxa_adm_total)}")
                        else:
                            col_b3.metric("Taxa Adm", "0% (Não config.)")
                            
                        if tem_risco:
                            col_b4.metric(f"Taxa Risco ({formatar_br(tx_risco_plano * 100)}%)", f"R$ {formatar_br(valor_risco)}")
                        else:
                            col_b4.metric("Taxa Risco", "Sem Risco")

                    elif plano_selecionado == "UNERJPREV":
                        contrib_patr = contrib_pura
                        
                        st.success(f"### Salário Correspondente Necessário: R$ {formatar_br(salario_encontrado)}")
                        
                        st.markdown("#### Detalhamento da Contribuição Equivalente (Participante)")
                        col_f1, col_f2 = st.columns(2)
                        teto_inss = plano_dados["ur"]
                        if salario_encontrado <= teto_inss:
                            aliq_show = plano_dados["aliq_1"] * 100
                        else:
                            if idade_ou_tempo_input <= 44: aliq_show = 3.0
                            elif 45 <= idade_ou_tempo_input <= 49: aliq_show = 4.0
                            elif 50 <= idade_ou_tempo_input <= 54: aliq_show = 5.0
                            else: aliq_show = 6.0
                        col_f1.metric("Alíquota Aplicada (Base Inteira)", f"{formatar_br(aliq_show)}%")
                        col_f2.metric("Contribuição Pura (Participante)", f"R$ {formatar_br(contrib_pura)}")
                        
                        st.markdown("### Composição do Boleto")
                        col_b1, col_b2, col_b3 = st.columns(3)
                        col_b1.metric("Contrib. Participante", f"R$ {formatar_br(contrib_pura)}")
                        col_b2.metric("Contrib. Patrocinadora", f"R$ {formatar_br(contrib_patr)}")
                        col_b3.metric("Taxas (Adm/Risco)", "Isento no Boleto*")

                    elif plano_selecionado == "LUNELLIPREV":
                        contrib_patr = arredondar(contrib_pura * 0.10)
                        
                        st.success(f"### Salário Correspondente Necessário: R$ {formatar_br(salario_encontrado)}")
                        st.caption("⚠️ *O Autopatrocinado assume a sua parte e a contrapartida fixa de 10% da patrocinadora. Demais rateios globais não se aplicam.*")
                        
                        st.markdown("### Composição do Boleto")
                        col_b1, col_b2, col_b3 = st.columns(3)
                        col_b1.metric("Contrib. Participante", f"R$ {formatar_br(contrib_pura)}")
                        col_b2.metric("Contrib. Patrocinadora (10%)", f"R$ {formatar_br(contrib_patr)}")
                        col_b3.metric("Taxas (Adm)", "Isento no Boleto*")
                        
                    else:
                        valor_risco = arredondar(salario_encontrado * tx_risco_plano) if tem_risco else 0.0
                        if plano_dados.get("base_adm_com_risco", False):
                            valor_adm = arredondar((contrib_pura + valor_risco) * tx_adm_plano)
                        else:
                            valor_adm = arredondar(contrib_pura * tx_adm_plano)
                        
                        st.success(f"### Salário Correspondente Necessário: R$ {formatar_br(salario_encontrado)}")
                        
                        st.markdown("### Composição do Boleto")
                        col_b1, col_b2, col_b3 = st.columns(3)
                        col_b1.metric("Contribuição Pura", f"R$ {formatar_br(contrib_pura)}")
                        
                        if tx_adm_plano > 0:
                            col_b2.metric(f"Taxa Administração ({formatar_br(tx_adm_plano * 100)}%)", f"R$ {formatar_br(valor_adm)}")
                        else:
                            col_b2.metric("Taxa Administração", "0% (Não config.)")
                            
                        if tem_risco:
                            col_b3.metric(f"Taxa Risco ({formatar_br(tx_risco_plano * 100)}%)", f"R$ {formatar_br(valor_risco)}")
                        else:
                            col_b3.metric("Taxa Risco", "Sem Risco")
                else:
                    st.info("O cálculo de salário para este plano requer alinhamento de variáveis complexas.")
            else:
                st.warning("Insira um valor de cobrança válido.")


# =================================================================
# 6. TELA 2: CÁLCULO DE CONTRIBUIÇÃO EM LOTE
# =================================================================
elif menu_selecionado == "Cálculo de Contribuição em Lote":
    pv.titulo_pagina("📂 Cálculo de Contribuição em Lote")
    st.write("Baixe a planilha modelo, preencha as informações dos participantes (Salário) e faça o upload para processar múltiplos cálculos de uma só vez.")
    
    df_modelo = pd.DataFrame({
        "Plano": ["FIESCPREV", "PREVISC SENAI-MA", "PREVFIEPA", "PREVIFIEA"],
        "Salário Bruto": [4500.00, 8000.00, 6000.00, 9200.00],
        "Idade / Tempo Contrib. (Opcional)": [30, 45, 28, 48],
        "Faixa FIEMA (1 a 3) (Opcional)": [1, 2, 1, 1],
        "Faixa Opção (1 a 6) (Opcional)": [1, 1, 4, 2],
        "Aliquota Opcional % (Opcional)": [0.0, 0.0, 0.0, 0.0],
        "Categoria (Opcional)": ["-", "-", "-", "-"],
        "Univali Tipo (Opcional)": ["-", "-", "-", "-"]
    })
    
    buffer_modelo = io.BytesIO()
    with pd.ExcelWriter(buffer_modelo, engine='openpyxl') as writer:
        df_modelo.to_excel(writer, index=False, sheet_name="Modelo_Contribuicao")
    
    st.download_button(
        label="📥 Baixar Planilha Modelo (Contribuição)", 
        data=buffer_modelo.getvalue(), 
        file_name="modelo_contribuicao_lote.xlsx", 
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    
    st.divider()
    
    st.subheader("Processar Base de Dados")
    arquivo_upload = st.file_uploader("Faça o upload da planilha preenchida (.xlsx)", type=["xlsx"], key="up_contrib")
    
    if arquivo_upload is not None:
        try:
            df_lote = pd.read_excel(arquivo_upload)
            
            resultados = []
            for idx, row in df_lote.iterrows():
                plano_excel = str(row.get("Plano", "")).strip().upper()
                plano_oficial = apelidos_planilha.get(plano_excel, str(row.get("Plano", "")).strip())
                
                if plano_oficial in planos:
                    salario = float(row.get("Salário Bruto", 0.0)) if pd.notna(row.get("Salário Bruto")) else 0.0
                    idade = int(row.get("Idade / Tempo Contrib. (Opcional)", 30)) if "Idade / Tempo Contrib. (Opcional)" in df_lote.columns and pd.notna(row.get("Idade / Tempo Contrib. (Opcional)")) else 30
                    aliq_bruta = row.get("Aliquota Opcional % (Opcional)", 0.0) if "Aliquota Opcional % (Opcional)" in df_lote.columns else 0.0
                    aliq = float(aliq_bruta) / 100 if pd.notna(aliq_bruta) and float(aliq_bruta) > 0 else None
                    
                    univ_cat = str(row.get("Categoria (Opcional)", "Migrante")).strip() if "Categoria (Opcional)" in df_lote.columns else "Migrante"
                    # Compatibilidade com planilhas antigas
                    if "Univali Categoria (Opcional)" in df_lote.columns:
                        univ_cat = str(row.get("Univali Categoria (Opcional)", "Migrante")).strip()
                        
                    univ_tipo = str(row.get("Univali Tipo (Opcional)", "Normal")).strip() if "Univali Tipo (Opcional)" in df_lote.columns else "Normal"
                    
                    faixa_val = "1"
                    if "Faixa FIEMA (1 a 3) (Opcional)" in df_lote.columns and pd.notna(row.get("Faixa FIEMA (1 a 3) (Opcional)")) and plano_oficial == "PREVISC SENAI-MA":
                        faixa_val = str(row.get("Faixa FIEMA (1 a 3) (Opcional)")).split('.')[0].strip()
                    elif plano_oficial in ["PREVFIEPA", "PREVIFIEA"]:
                        if "Faixa Opção (1 a 6) (Opcional)" in df_lote.columns and pd.notna(row.get("Faixa Opção (1 a 6) (Opcional)")):
                            faixa_val = str(row.get("Faixa Opção (1 a 6) (Opcional)")).split('.')[0].strip()
                        elif "Faixa FIEPA (1 a 6) (Opcional)" in df_lote.columns and pd.notna(row.get("Faixa FIEPA (1 a 6) (Opcional)")):
                            faixa_val = str(row.get("Faixa FIEPA (1 a 6) (Opcional)")).split('.')[0].strip()
                    
                    faixa_opcao_planilha = f"Faixa {faixa_val}" if faixa_val in ["1", "2", "3", "4", "5", "6"] else "Faixa 1"
                    
                    total_pagar = calcular_contribuicao(plano_oficial, salario, aliq, univ_cat, univ_tipo, idade, faixa_opcao_planilha)[0]
                    resultados.append(total_pagar)
                else:
                    resultados.append("Plano Não Encontrado")
            
            df_lote["Contribuição Sugerida (R$)"] = [formatar_br(v) for v in resultados]
            
            st.success("Cálculo em lote finalizado com sucesso!")
            st.dataframe(df_lote, use_container_width=True)
            
            buffer_resultado = io.BytesIO()
            with pd.ExcelWriter(buffer_resultado, engine='openpyxl') as writer:
                df_lote.to_excel(writer, index=False, sheet_name="Resultados_Previsc")
                
            st.download_button(
                label="📤 Baixar Resultados Processados", 
                data=buffer_resultado.getvalue(), 
                file_name="resultado_contribuicao_lote.xlsx", 
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except Exception as e:
            st.error(f"Erro ao ler a planilha. Detalhe: {e}")


# =================================================================
# 7. TELA 3: CÁLCULO DE SALÁRIO EM LOTE
# =================================================================
elif menu_selecionado == "Cálculo de Salário em Lote":
    pv.titulo_pagina("📂 Cálculo de Salário em Lote")
    st.write("Baixe a planilha modelo, preencha a Cobrança Alvo de cada participante e faça o upload para descobrir os salários correspondentes.")
    
    df_modelo_rev = pd.DataFrame({
        "Plano": ["FIESCPREV", "PREVISC SENAI-MA", "PREVFIEPA", "PREVIFIEA"],
        "Cobrança Alvo": [450.00, 300.00, 200.00, 520.00],
        "Idade / Tempo Contrib. (Opcional)": [30, 45, 28, 48],
        "Faixa FIEMA (1 a 3) (Opcional)": [1, 2, 1, 1],
        "Faixa Opção (1 a 6) (Opcional)": [1, 1, 4, 2],
        "Aliquota Opcional % (Opcional)": [0.0, 0.0, 0.0, 0.0],
        "Categoria (Opcional)": ["-", "-", "-", "-"],
        "Univali Tipo (Opcional)": ["-", "-", "-", "Normal"]
    })
    
    buffer_modelo_rev = io.BytesIO()
    with pd.ExcelWriter(buffer_modelo_rev, engine='openpyxl') as writer:
        df_modelo_rev.to_excel(writer, index=False, sheet_name="Modelo_Salario")
    
    st.download_button(
        label="📥 Baixar Planilha Modelo (Salário)", 
        data=buffer_modelo_rev.getvalue(), 
        file_name="modelo_salario_lote.xlsx", 
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    
    st.divider()
    
    st.subheader("Processar Base de Dados")
    arquivo_upload_rev = st.file_uploader("Faça o upload da planilha preenchida (.xlsx)", type=["xlsx"], key="up_salario")
    
    if arquivo_upload_rev is not None:
        try:
            df_lote_rev = pd.read_excel(arquivo_upload_rev)
            
            resultados_rev = []
            for idx, row in df_lote_rev.iterrows():
                plano_excel = str(row.get("Plano", "")).strip().upper()
                plano_oficial = apelidos_planilha.get(plano_excel, str(row.get("Plano", "")).strip())
                
                if plano_oficial in planos:
                    contribuicao_alvo = float(row.get("Cobrança Alvo", 0.0)) if "Cobrança Alvo" in df_lote_rev.columns and pd.notna(row.get("Cobrança Alvo")) else 0.0
                    idade = int(row.get("Idade / Tempo Contrib. (Opcional)", 30)) if "Idade / Tempo Contrib. (Opcional)" in df_lote_rev.columns and pd.notna(row.get("Idade / Tempo Contrib. (Opcional)")) else 30
                    aliq_bruta = row.get("Aliquota Opcional % (Opcional)", 0.0) if "Aliquota Opcional % (Opcional)" in df_lote_rev.columns else 0.0
                    aliq = float(aliq_bruta) / 100 if pd.notna(aliq_bruta) and float(aliq_bruta) > 0 else None
                    
                    univ_cat = str(row.get("Categoria (Opcional)", "Migrante")).strip() if "Categoria (Opcional)" in df_lote_rev.columns else "Migrante"
                    if "Univali Categoria (Opcional)" in df_lote_rev.columns:
                        univ_cat = str(row.get("Univali Categoria (Opcional)", "Migrante")).strip()
                        
                    univ_tipo = str(row.get("Univali Tipo (Opcional)", "Normal")).strip() if "Univali Tipo (Opcional)" in df_lote_rev.columns else "Normal"
                    
                    faixa_val = "1"
                    if "Faixa FIEMA (1 a 3) (Opcional)" in df_lote_rev.columns and pd.notna(row.get("Faixa FIEMA (1 a 3) (Opcional)")) and plano_oficial == "PREVISC SENAI-MA":
                        faixa_val = str(row.get("Faixa FIEMA (1 a 3) (Opcional)")).split('.')[0].strip()
                    elif plano_oficial in ["PREVFIEPA", "PREVIFIEA"]:
                        if "Faixa Opção (1 a 6) (Opcional)" in df_lote_rev.columns and pd.notna(row.get("Faixa Opção (1 a 6) (Opcional)")):
                            faixa_val = str(row.get("Faixa Opção (1 a 6) (Opcional)")).split('.')[0].strip()
                        elif "Faixa FIEPA (1 a 6) (Opcional)" in df_lote_rev.columns and pd.notna(row.get("Faixa FIEPA (1 a 6) (Opcional)")):
                            faixa_val = str(row.get("Faixa FIEPA (1 a 6) (Opcional)")).split('.')[0].strip()
                    
                    faixa_opcao_planilha = f"Faixa {faixa_val}" if faixa_val in ["1", "2", "3", "4", "5", "6"] else "Faixa 1"
                    
                    salario_descob = calcular_salario_reverso(plano_oficial, contribuicao_alvo, aliq, univ_cat, univ_tipo, idade, faixa_opcao_planilha)
                    
                    if salario_descob == 0:
                        resultados_rev.append("Cálculo Incompatível")
                    else:
                        resultados_rev.append(salario_descob)
                else:
                    resultados_rev.append("Plano Não Encontrado")
            
            df_lote_rev["Salário Exato Necessário (R$)"] = [formatar_br(v) for v in resultados_rev]
            
            st.success("Cálculo em lote finalizado com sucesso!")
            st.dataframe(df_lote_rev, use_container_width=True)
            
            buffer_resultado_rev = io.BytesIO()
            with pd.ExcelWriter(buffer_resultado_rev, engine='openpyxl') as writer:
                df_lote_rev.to_excel(writer, index=False, sheet_name="Resultados_Previsc")
                
            st.download_button(
                label="📤 Baixar Resultados Processados", 
                data=buffer_resultado_rev.getvalue(), 
                file_name="resultado_salario_lote.xlsx", 
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except Exception as e:
            st.error(f"Erro ao processar. Detalhe: {e}")


# =================================================================
# 8. TELA 4: REGRAS E BASES DE CÁLCULO
# =================================================================
elif menu_selecionado == "Regras e Bases de Cálculo":
    pv.titulo_pagina("📖 Regras e Bases de Cálculo")
    st.write("Consulte abaixo os indexadores atuais e a estrutura de cálculo configurada para cada plano de previdência no sistema.")
    
    dados_tabela = [
        {"Plano": "FIESCPREV", "Indexador": "UR", "Valor (R$)": "716,84", "Regra de Cálculo": "Faixas: 3% (Até 7 UR) | 14% (Acima) - Taxa Adm total = (Participante + Patrocinadora) * 2,18%. Risco não gera taxa adm."},
        {"Plano": "FIEP", "Indexador": "UR", "Valor (R$)": "742,37", "Regra de Cálculo": "Faixas: 3% (Até 8,5 UR) | 7,5% (Acima). Patrocinadora aporta 50% (< 40 anos) ou 100% (>= 40 anos)."},
        {"Plano": "SENACPREV", "Indexador": "UR", "Valor (R$)": "734,75", "Regra de Cálculo": "Faixas: 2,3% (Até 8 UR) | 7,4% (Acima)"},
        {"Plano": "SENAI-PIPREV", "Indexador": "UR", "Valor (R$)": "7.376,89", "Regra de Cálculo": "Faixas Cascata: 1% (Até 0,5) | 4% (0,5 a 1) | 8% (Acima) - Desconto Superávit (7,28%). Taxa Adm = 2,18% sobre o dobro da cota pura. Aporte da Patrocinadora deduz a taxa adm."},
        {"Plano": "PREVISC SENAI-MA", "Indexador": "Valores Fixos", "Valor (R$)": "-", "Regra de Cálculo": "Cascata de Múltiplas Faixas: De 1,50% a 16,10% dependendo da opção escolhida pelo participante (Faixas: R$ 2.907,14 e R$ 5.000,00)"},
        {"Plano": "PREVFIEPA", "Indexador": "UP", "Valor (R$)": "7.740,09", "Regra de Cálculo": "Cascata de Múltiplas Faixas (6 Faixas). Taxa Adm (4%) aplicada sobre a Patrocinadora. Risco (2,35%) aplicado sobre (Patrocinadora - Adm)."},
        {"Plano": "FECOMERCIO", "Indexador": "UR", "Valor (R$)": "845,22", "Regra de Cálculo": "Faixas: 2,3% (Até 8 UR) | 7,4% (Acima)"},
        {"Plano": "FIEMTPREV", "Indexador": "UR", "Valor (R$)": "715,77", "Regra de Cálculo": "Faixas: 2% (Até 12,06 UR) | 7,25% (Acima) - Taxa Adm: 2,18%. O participante assume a regra integral como Não Migrante."},
        {"Plano": "UNIVALIPrevidencia", "Indexador": "UR", "Valor (R$)": "627,19", "Regra de Cálculo": "Faixa Fixa: 3% (Até 8 UR) | Excedente: 14% ou 17% variando por Categoria - Taxa Adm: 2,18% - Contrapartida: 50% (< 10 anos) ou 100% (>= 10 anos) da sugerida, zera se Tempo >= 35 (Não Migrante) ou >= 30 (Migrante)."},
        {"Plano": "SESI-PIPREV", "Indexador": "SP", "Valor (R$)": "6.812,53", "Regra de Cálculo": "Fórmula Direta c/ Parcela a Deduzir: (Salário * 13,7741%) - (SP * 12,2124%). Taxa Adm: 2,18% (Descontada do aporte da Patrocinadora)."},
        {"Plano": "SESC SC (SESCPREV)", "Indexador": "UR", "Valor (R$)": "922,63", "Regra de Cálculo": "Faixas de Dedução dinâmicas (Até 10 URs | 10 a 11.4288 URs | Acima). Taxa Adm: 2,18%. Risco opcional: 0,12%."},
        {"Plano": "LUNELLIPREV", "Indexador": "Salário", "Valor (R$)": "-", "Regra de Cálculo": "Livre Escolha (Mín. 1%). Patrocinadora: 10% da contrib. do participante. Taxa Adm: Isento no boleto (cobrado do saldo)."},
        {"Plano": "PREVIFIEA", "Indexador": "UP", "Valor (R$)": "8.258,59", "Regra de Cálculo": "Cascata de Múltiplas Faixas (6 Faixas). Taxa Adm (4%) aplicada sobre a Patrocinadora. Risco (2,35%) aplicado sobre (Patrocinadora - Adm)."},
        {"Plano": "UNERJPREV", "Indexador": "INSS", "Valor (R$)": "8.475,55", "Regra de Cálculo": "Base Inteira Única: 0,25% (Até 1 Teto). Acima de 1 Teto aplica 3% a 6% retroativo sobre a Base Total conforme a idade."},
        {"Plano": "PREVITÊ", "Indexador": "-", "Valor (R$)": "-", "Regra de Cálculo": "Contribuição Fixa / Regulamento Fechado"}
    ]
    
    st.dataframe(pd.DataFrame(dados_tabela), use_container_width=True, hide_index=True)
