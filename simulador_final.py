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
                aliq_padrao = formatar_br(plano_dados["aliq_1"] * 100)
                aliq_input_str = st.text_input("Alíquota de Contribuição (%):", value=aliq_padrao, key="aliq_normal")
                aliq_escolhida = converter_br(aliq_input_str) / 100
            elif plano_dados.get("tipo") == "lunelliprev":
                st.info("A Contribuição Básica é fixa em 10% sobre o Salário.")
                aliq_escolhida = 0.10
            
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
                    col_f1.metric("Alíquota Aplicada", "10,00%")
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
                    col_f1.metric("Faixa Base (Até R$ 2.521,45)", f"R$ {formatar_br(f1)}")
                    col_f2.metric("Faixa Intermediária (Até R$ 5.042,89)", f"R$ {formatar_br(f2)}")
                    col_f3.metric("Faixa Topo (Excedente)", f"R$ {formatar_br(f3)}")
                elif plano_selecionado == "SESC SC (SESCPREV)":
                    st.success(f"### Contribuição Sugerida (Participante): R$ {formatar_br(total)}")
                    st.info("Cálculo realizado via fator de Parcela a Deduzir.")
                    col_f1, col_f2 = st.columns(2)
                    col_f1.metric("Valor Bruto (Alíquota Cheia)", f"R$ {formatar_br(f1)}")
                    if f2 > 0:
                        col_f2.metric("Parcela a Deduzir", f"- R$ {formatar_br(f2)}")
                    else:
                        col_f2.metric("Parcela a Deduzir", "Isento")
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
                        if univali_migrante == "Não Migrante":
                            c_patr_bruta = total
                            taxa_adm_part = arredondar(total * tx_adm_plano)
                            taxa_adm_patroc = arredondar(c_patr_bruta * tx_adm_plano)
                            taxa_adm_total = arredondar(taxa_adm_part + taxa_adm_patroc)
                            c_patr_exibir = arredondar(c_patr_bruta - taxa_adm_total)
                        else:
                            teto_rs = plano_dados["ur"] * plano_dados["teto_urs"]
                            sug_f1 = arredondar(salario_input * plano_dados["aliq_1"]) if salario_input <= teto_rs else arredondar(teto_rs * plano_dados["aliq_1"])
                            sug_f2 = 0.0
                            if salario_input > teto_rs:
                                sug_f2 = arredondar((salario_input - teto_rs) * 0.14)
                            sugerida_total = arredondar(sug_f1 + sug_f2)
                            
                            fator_tempo = 1.0 if idade_ou_tempo_input >= 10 else 0.5
                            c_patr_bruta = arredondar(sugerida_total * fator_tempo)
                            
                            taxa_adm_part = arredondar(total * tx_adm_plano)
                            taxa_adm_patroc = 0.0
                            taxa_adm_total = arredondar(taxa_adm_part + taxa_adm_patroc)
                            
                            c_patr_exibir = arredondar(c_patr_bruta - taxa_adm_patroc)
                
                elif plano_selecionado == "SENAI-PIPREV":
                    c_patr_bruta = arredondar(total + superavit)
                    taxa_adm_total = arredondar((c_patr_bruta * 2) * tx_adm_plano)
                    c_patr_exibir = arredondar(total - taxa_adm_total)

                elif plano_selecionado == "SESI-PIPREV":
                    c_patr_bruta = f1
                    taxa_adm_part = arredondar(c_patr_bruta * tx_adm_plano)
                    taxa_adm_total = arredondar(taxa_adm_part * 2)
                    c_patr_exibir = total

                elif plano_selecionado in ["PREVFIEPA", "PREVIFIEA"]:
                    c_patr_bruta = arredondar(total + superavit)
                    taxa_adm_total = arredondar(c_patr_bruta * tx_adm_plano)
                    valor_risco = arredondar((c_patr_bruta - taxa_adm_total) * tx_risco_plano) if tem_risco_escolhido else 0.0
                    c_patr_exibir = arredondar(c_patr_bruta - taxa_adm_total - valor_risco)

                else:
                    c_patr_bruta = arredondar(total + superavit)
                    
                    if plano_selecionado == "FIEP":
                        if "Abaixo" in categoria_participante:
                            c_patr_bruta = arredondar(c_patr_bruta * 0.50)

                    if plano_dados.get("base_adm_com_risco", False):
                        taxa_adm_patr = arredondar((c_patr_bruta + valor_risco) * tx_adm_plano)
                        taxa_adm_total = arredondar(taxa_adm_patr * 2)
                    else:
                        taxa_adm_part = arredondar(total * tx_adm_plano)
                        taxa_adm_patroc = arredondar(c_patr_bruta * tx_adm_plano)
                        taxa_adm_total = arredondar(taxa_adm_part + taxa_adm_patroc)
                    
                    if plano_selecionado == "LUNELLIPREV":
                        c_patr_exibir = arredondar(c_patr_bruta * 0.10)
                    elif plano_selecionado == "UNERJPREV":
                        c_patr_exibir = c_patr_bruta
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

    planos_auto = [p for p in list(planos.keys()) if p not in ["PREVISC SENAI-MA", "FECOMERCIO", "PREVITÊ"]]
    plano_selecionado = st.selectbox("Selecione o Plano de Previdência:", options=planos_auto, key="sel_plano_auto")
    plano_dados = planos[plano_selecionado]

    univali_migrante = "Migrante"
    univali_tipo = "Normal"
    idade_ou_tempo_input = 30
    faixa_opcao_selecionada = "Faixa 1"
    categoria_participante = "Não Migrante" 

    planos_unificados_auto = ["SENACPREV", "FIEMTPREV", "PREVFIEPA", "PREVIFIEA", "SESI-PIPREV", "LUNELLIPREV", "UNERJPREV", "SENAI-PIPREV", "SESC SC (SESCPREV)", "FIESCPREV", "FIEP"]

    if plano_selecionado in planos_unificados_auto:
        if plano_selecionado == "SENACPREV":
            categoria_participante = "Migrante (Com Risco)"
        elif plano_selecionado in ["SESC SC (SESCPREV)", "FIESCPREV"]:
            categoria_participante = "Não Migrante (Com Risco)"
        else:
            categoria_participante = "Não Migrante"

    if plano_selecionado == "UNIVALIPrevidencia":
        univali_migrante = "Não Migrante"
        univali_tipo = "Normal"
        idade_ou_tempo_input = 10
        categoria_participante = "Não Migrante"
        st.info("Para o Autopatrocínio, o plano UNIVALI utiliza a regra fixa de categoria 'Não Migrante - Normal' (Sem Risco).")
    elif plano_selecionado not in planos_unificados_auto:
        st.markdown("**Selecione a Categoria de Participação:**")
        if plano_selecionado in planos_com_risco:
            opcoes_cat = ["Migrante (Sem Risco)", "Migrante (Com Risco)", "Não Migrante (Sem Risco)", "Não Migrante (Com Risco)"]
        else:
            opcoes_cat = ["Migrante", "Não Migrante"]
            
        categoria_participante = st.radio("Categoria:", opcoes_cat, horizontal=True, label_visibility="collapsed", key="cat_auto_geral")
        
    if plano_dados.get("tipo") == "unerjprev_idade":
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
        
    if plano_selecionado in ["PREVFIEPA", "PREVIFIEA"]:
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
                aliq_padrao_auto = formatar_br(plano_dados["aliq_1"] * 100)
                aliq_input_auto_str = st.text_input("Alíquota de Contribuição (%):", value=aliq_padrao_auto, key="aliq_auto_norm")
                aliq_escolhida_auto = converter_br(aliq_input_auto_str) / 100
            elif plano_dados.get("tipo") == "lunelliprev":
                st.info("A Contribuição Básica é fixa em 10% sobre o Salário para Autopatrocinados.")
                aliq_escolhida_auto = 0.10
            
        if plano_dados.get("tipo") == "unerjprev_idade":
            st.info(f"O Teto do INSS (1 UR) utilizado é de R$ {formatar_br(plano_dados['ur'])}")
        if plano_selecionado in ["PREVFIEPA", "PREVIFIEA"]:
            st.info(f"A UP atual adotada para o plano {plano_selecionado} é de R$ {formatar_br(plano_dados['up'])}")
            
        if st.button("Gerar cálculo", type="primary"):
            if salario_input > 0:
                tx_adm_plano = plano_dados.get("tx_adm", 0.0)
                tx_risco_plano = plano_dados.get("tx_risco_auto", plano_dados.get("tx_risco", 0.0))
                tem_risco = "(Com Risco)" in categoria_participante
                
                if plano_selecionado in ["PREVFIEPA", "PREVIFIEA"] and "Sem Risco" in categoria_participante:
                    tem_risco = False
                    tx_risco_plano = 0.0
                
                valor_risco = arredondar(salario_input * tx_risco_plano) if tem_risco else 0.0
                
                contrib_pura, f1, f2, f3, superavit = calcular_contribuicao(plano_selecionado, salario_input, aliq_escolhida_auto, univali_migrante, univali_tipo, idade_ou_tempo_input, faixa_opcao_selecionada, is_autopatrocinio=True)
                
                if plano_selecionado == "FIESCPREV":
                    contrib_patr = 0.0
                    taxa_adm_total = arredondar((contrib_pura + valor_risco) * tx_adm_plano)
                    total_cobranca = arredondar(contrib_pura + contrib_patr + taxa_adm_total + valor_risco)
                    
                    st.success(f"### Cobrança Mensal Total (Boleto): R$ {formatar_br(total_cobranca)}")
                    st.markdown("### Composição do Boleto")
                    col_b1, col_b2, col_b3, col_b4 = st.columns(4)
                    col_b1.metric("Contrib. Participante", f"R$ {formatar_br(contrib_pura)}")
                    col_b2.metric("Contrib. Patrocinadora", "R$ 0,00")
                    col_b3.metric(f"Taxa Adm ({formatar_br(tx_adm_plano * 100)}%)", f"R$ {formatar_br(taxa_adm_total)}")
                    
                    if tem_risco:
                        col_b4.metric(f"Taxa Risco ({formatar_br(tx_risco_plano * 100)}%)", f"R$ {formatar_br(valor_risco)}")
                    else:
                        col_b4.metric("Taxa Risco", "Sem Risco")

                elif plano_selecionado == "UNIVALIPrevidencia":
                    contrib_patr = 0.0
                    taxa_adm_total = arredondar(contrib_pura * tx_adm_plano)
                    total_cobranca = arredondar(contrib_pura + contrib_patr + taxa_adm_total + valor_risco)
                    
                    st.success(f"### Cobrança Mensal Total (Boleto): R$ {formatar_br(total_cobranca)}")
                    st.markdown("### Composição do Boleto")
                    col_b1, col_b2, col_b3, col_b4 = st.columns(4)
                    col_b1.metric("Contrib. Participante", f"R$ {formatar_br(contrib_pura)}")
                    col_b2.metric("Contrib. Patrocinadora", "R$ 0,00")
                    col_b3.metric("Taxa Adm Total", f"R$ {formatar_br(taxa_adm_total)}")
                    col_b4.metric(f"Taxa Risco", "Isento")

                elif plano_selecionado in ["FIEMTPREV", "SENAI-PIPREV", "SESI-PIPREV"]:
                    taxa_adm_total = arredondar((contrib_pura * 2) * tx_adm_plano)
                    contrib_patr = arredondar(contrib_pura - taxa_adm_total)
                    total_cobranca = arredondar(contrib_pura + contrib_patr + taxa_adm_total)
                    
                    st.success(f"### Cobrança Mensal Total (Boleto): R$ {formatar_br(total_cobranca)}")
                    st.markdown("### Composição do Boleto")
                    col_b1, col_b2, col_b3, col_b4 = st.columns(4)
                    col_b1.metric("Contrib. Participante", f"R$ {formatar_br(contrib_pura)}")
                    col_b2.metric("Contrib. Patrocinadora", f"R$ {formatar_br(contrib_patr)}")
                    col_b3.metric(f"Taxa Adm ({formatar_br(tx_adm_plano * 100)}% x 2)", f"R$ {formatar_br(taxa_adm_total)}")
                    if tem_risco and tx_risco_plano > 0:
                        col_b4.metric(f"Taxa Risco ({formatar_br(tx_risco_plano * 100)}%)", f"R$ {formatar_br(valor_risco)}")
                    else:
                        col_b4.metric("Taxa Risco", "Sem Risco")

                elif plano_selecionado in ["PREVFIEPA", "PREVIFIEA"]:
                    taxa_adm_total = arredondar(contrib_pura * tx_adm_plano)
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
                    st.caption("⚠️ *O Autopatrocinado assume a sua parte (10% do salário) e a contrapartida da patrocinadora (10% da sua cota).*")
                    
                    st.markdown("### Composição do Boleto")
                    col_b1, col_b2, col_b3 = st.columns(3)
                    col_b1.metric("Contrib. Participante", f"R$ {formatar_br(contrib_pura)}")
                    col_b2.metric("Contrib. Patrocinadora (10%)", f"R$ {formatar_br(contrib_patr)}")
                    col_b3.metric("Taxas (Adm)", "Isento no Boleto*")
                    
                elif plano_selecionado == "PREVISC SENAI-MA":
                    if plano_dados.get("base_adm_com_risco", False):
                        taxa_adm_total = arredondar((contrib_pura + valor_risco) * tx_adm_plano)
                    else:
                        taxa_adm_total = arredondar(contrib_pura * tx_adm_plano)
                    
                    st.success(f"### Cobrança Mensal Total (Boleto): R$ {formatar_br(total_cobranca)}")
                    
                    st.markdown("#### Detalhamento da Contribuição Equivalente (Participante)")
                    col_f1, col_f2, col_f3 = st.columns(3)
                    col_f1.metric("Faixa Base (Até R$ 2.521,45)", f"R$ {formatar_br(f1)}")
                    col_f2.metric("Faixa Intermediária (Até R$ 5.042,89)", f"R$ {formatar_br(f2)}")
                    col_f3.metric("Faixa Topo (Excedente)", f"R$ {formatar_br(f3)}")
                    
                    st.markdown("### Composição do Boleto")
                    col_b1, col_b2, col_b3, col_b4 = st.columns(4)
                    col_b1.metric("Contribuição Pura", f"R$ {formatar_br(contrib_pura)}")
                    col_b2.metric("Contrib. Patrocinadora", "R$ 0,00")
                    
                    if tx_adm_plano > 0:
                        col_b3.metric(f"Taxa Administração ({formatar_br(tx_adm_plano * 100)}%)", f"R$ {formatar_br(taxa_adm_total)}")
                    else:
                        col_b3.metric("Taxa Administração", "0% (Não config.)")
                        
                    if tem_risco:
                        col_b4.metric(f"Taxa Risco ({formatar_br(tx_risco_plano * 100)}%)", f"R$ {formatar_br(valor_risco)}")
                    else:
                        col_b4.metric("Taxa Risco", "Sem Risco")
                        
                elif plano_selecionado == "SESC SC (SESCPREV)":
                    contrib_patr = 0.0
                    taxa_adm_total = arredondar(contrib_pura * tx_adm_plano)
                    total_cobranca = arredondar(contrib_pura + contrib_patr + taxa_adm_total + valor_risco)
                    
                    st.success(f"### Cobrança Mensal Total (Boleto): R$ {formatar_br(total_cobranca)}")
                    
                    st.markdown("#### Detalhamento da Contribuição Equivalente (Participante)")
                    st.info("Cálculo realizado via fator de Parcela a Deduzir (como INSS).")
                    col_f1, col_f2 = st.columns(2)
                    col_f1.metric("Valor Bruto (Alíquota Cheia)", f"R$ {formatar_br(f1)}")
                    if f2 > 0:
                        col_f2.metric("Parcela a Deduzir", f"- R$ {formatar_br(f2)}")
                    else:
                        col_f2.metric("Parcela a Deduzir", "Isento")
                        
                    st.markdown("### Composição do Boleto")
                    col_b1, col_b2, col_b3, col_b4 = st.columns(4)
                    col_b1.metric("Contrib. Participante", f"R$ {formatar_br(contrib_pura)}")
                    col_b2.metric("Contrib. Patrocinadora", "R$ 0,00")
                    col_b3.metric(f"Taxa Adm ({formatar_br(tx_adm_plano * 100)}%)", f"R$ {formatar_br(taxa_adm_total)}")
                    col_b4.metric(f"Taxa Risco", f"R$ {formatar_br(valor_risco)}")

                elif plano_selecionado == "FIEP":
                    contrib_patr = 0.0
                    taxa_adm_total = arredondar(contrib_pura * tx_adm_plano)
                    
                    total_cobranca = arredondar(contrib_pura + contrib_patr + taxa_adm_total + valor_risco)
                    
                    st.success(f"### Cobrança Mensal Total (Boleto): R$ {formatar_br(total_cobranca)}")
                    
                    st.markdown("### Composição do Boleto")
                    col_b1, col_b2, col_b3, col_b4 = st.columns(4)
                    col_b1.metric("Contrib. Participante", f"R$ {formatar_br(contrib_pura)}")
                    col_b2.metric("Contrib. Patrocinadora", "R$ 0,00")
                    
                    if tx_adm_plano > 0:
                        col_b3.metric(f"Taxa Administração ({formatar_br(tx_adm_plano * 100)}%)", f"R$ {formatar_br(taxa_adm_total)}")
                    else:
                        col_b3.metric("Taxa Administração", "0% (Não config.)")
                        
                    if tem_risco and tx_risco_plano > 0:
                        col_b4.metric(f"Taxa Risco ({formatar_br(tx_risco_plano * 100)}%)", f"R$ {formatar_br(valor_risco)}")
                    else:
                        col_b4.metric("Taxa Risco", "Sem Risco")

                else:
                    contrib_patr = 0.0
                    if plano_dados.get("base_adm_com_risco", False):
                        taxa_adm_total = arredondar((contrib_pura + valor_risco) * tx_adm_plano)
                    else:
                        taxa_adm_total = arredondar(contrib_pura * tx_adm_plano)
                    
                    total_cobranca = arredondar(contrib_pura + contrib_patr + taxa_adm_total + valor_risco)
                    
                    st.success(f"### Cobrança Mensal Total (Boleto): R$ {formatar_br(total_cobranca)}")
                    
                    st.markdown("### Composição do Boleto")
                    col_b1, col_b2, col_b3, col_b4 = st.columns(4)
                    col_b1.metric("Contrib. Participante", f"R$ {formatar_br(contrib_pura)}")
                    col_b2.metric("Contrib. Patrocinadora", "R$ 0,00")
                    
                    if tx_adm_plano > 0:
                        col_b3.metric(f"Taxa Administração ({formatar_br(tx_adm_plano * 100)}%)", f"R$ {formatar_br(taxa_adm_total)}")
                    else:
                        col_b3.metric("Taxa Administração", "0% (Não config.)")
                        
                    if tem_risco:
                        col_b4.metric(f"Taxa Risco ({formatar_br(tx_risco_plano * 100)}%)", f"R$ {formatar_br(valor_risco)}")
                    else:
                        col_b4.metric("Taxa Risco", "Sem Risco")
            else:
                st.warning("Insira um salário válido.")

    with aba_reversa_auto:
        contrib_input_str = st.text_input("Digite o Valor do Boleto Mensal (R$):", value="0,00", key="contrib_reversa_auto")
        contrib_input = converter_br(contrib_input_str)
        
        aliq_escolhida_auto_rev = None
        if plano_dados.get("tipo") in ["up_sem_teto", "lunelliprev"]:
            if plano_dados.get("tipo") == "up_sem_teto":
                aliq_padrao_auto_rev = formatar_br(plano_dados["aliq_1"] * 100)
                aliq_input_auto_rev_str = st.text_input("Alíquota Utilizada (%):", value=aliq_padrao_auto_rev, key="aliq_rev_auto")
                aliq_escolhida_auto_rev = converter_br(aliq_input_auto_rev_str) / 100
            elif plano_dados.get("tipo") == "lunelliprev":
                aliq_escolhida_auto_rev = 0.10
            
        if st.button("Descobrir Salário", type="primary"):
            if contrib_input > 0:
                tx_adm_plano = plano_dados.get("tx_adm", 0.0)
                tx_risco_plano = plano_dados.get("tx_risco_auto", plano_dados.get("tx_risco", 0.0))
                tem_risco = "(Com Risco)" in categoria_participante
                
                if plano_selecionado in ["PREVFIEPA", "PREVIFIEA"] and "Sem Risco" in categoria_participante:
                    tem_risco = False
                    tx_risco_plano = 0.0
                
                if tx_adm_plano == 0.0 and tx_risco_plano == 0.0 and plano_selecionado not in ["FIEMTPREV", "PREVFIEPA", "PREVIFIEA", "LUNELLIPREV", "UNERJPREV"]:
                    st.warning("⚠️ Atenção: As taxas de administração e risco deste plano não estão cadastradas no sistema.")
                
                salario_encontrado = descobrir_salario_autopatrocinio(plano_selecionado, contrib_input, aliq_escolhida_auto_rev, univali_migrante, univali_tipo, idade_ou_tempo_input, faixa_opcao_selecionada, categoria_participante)
                
                if salario_encontrado > 0:
                    contrib_pura, f1, f2, f3, superavit = calcular_contribuicao(plano_selecionado, salario_encontrado, aliq_escolhida_auto_rev, univali_migrante, univali_tipo, idade_ou_tempo_input, faixa_opcao_selecionada, is_autopatrocinio=True)
                    
                    valor_risco = arredondar(salario_encontrado * tx_risco_plano) if tem_risco else 0.0
                    
                    if plano_selecionado == "FIESCPREV":
                        contrib_patr = 0.0
                        taxa_adm_total = arredondar((contrib_pura + valor_risco) * tx_adm_plano)
                        
                        st.success(f"### Salário Correspondente Necessário: R$ {formatar_br(salario_encontrado)}")
                        st.markdown("### Composição do Boleto")
                        col_b1, col_b2, col_b3, col_b4 = st.columns(4)
                        col_b1.metric("Contrib. Participante", f"R$ {formatar_br(contrib_pura)}")
                        col_b2.metric("Contrib. Patrocinadora", "R$ 0,00")
                        col_b3.metric(f"Taxa Adm ({formatar_br(tx_adm_plano * 100)}%)", f"R$ {formatar_br(taxa_adm_total)}")
                        
                        if tem_risco:
                            col_b4.metric(f"Taxa Risco ({formatar_br(tx_risco_plano * 100)}%)", f"R$ {formatar_br(valor_risco)}")
                        else:
                            col_b4.metric("Taxa Risco", "Sem Risco")

                    elif plano_selecionado == "UNIVALIPrevidencia":
                        contrib_patr = 0.0
                        taxa_adm_total = arredondar(contrib_pura * tx_adm_plano)
                        
                        st.success(f"### Salário Correspondente Necessário: R$ {formatar_br(salario_encontrado)}")
                        st.markdown("### Composição do Boleto")
                        col_b1, col_b2, col_b3, col_b4 = st.columns(4)
                        col_b1.metric("Contrib. Participante", f"R$ {formatar_br(contrib_pura)}")
                        col_b2.metric("Contrib. Patrocinadora", "R$ 0,00")
                        col_b3.metric("Taxa Adm Total", f"R$ {formatar_br(taxa_adm_total)}")
                        col_b4.metric(f"Taxa Risco", "Isento")

                    elif plano_selecionado in ["FIEMTPREV", "SENAI-PIPREV", "SESI-PIPREV"]:
                        taxa_adm_total = arredondar((contrib_pura * 2) * tx_adm_plano)
                        contrib_patr = arredondar(contrib_pura - taxa_adm_total)
                        
                        st.success(f"### Salário Correspondente Necessário: R$ {formatar_br(salario_encontrado)}")
                        st.markdown("### Composição do Boleto")
                        col_b1, col_b2, col_b3, col_b4 = st.columns(4)
                        col_b1.metric("Contrib. Participante", f"R$ {formatar_br(contrib_pura)}")
                        col_b2.metric("Contrib. Patrocinadora", f"R$ {formatar_br(contrib_patr)}")
                        col_b3.metric(f"Taxa Adm ({formatar_br(tx_adm_plano * 100)}% x 2)", f"R$ {formatar_br(taxa_adm_total)}")
                        if tem_risco and tx_risco_plano > 0:
                            col_b4.metric(f"Taxa Risco ({formatar_br(tx_risco_plano * 100)}%)", f"R$ {formatar_br(valor_risco)}")
                        else:
                            col_b4.metric("Taxa Risco", "Sem Risco")

                    elif plano_selecionado in ["PREVFIEPA", "PREVIFIEA"]:
                        taxa_adm_total = arredondar(contrib_pura * tx_adm_plano)
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
                        st.caption("⚠️ *O Autopatrocinado assume a sua parte (10% do salário) e a contrapartida da patrocinadora (10% da sua cota).*")
                        
                        st.markdown("### Composição do Boleto")
                        col_b1, col_b2, col_b3 = st.columns(3)
                        col_b1.metric("Contrib. Participante", f"R$ {formatar_br(contrib_pura)}")
                        col_b2.metric("Contrib. Patrocinadora (10%)", f"R$ {formatar_br(contrib_patr)}")
                        col_b3.metric("Taxas (Adm)", "Isento no Boleto*")
                        
                    elif plano_selecionado == "PREVISC SENAI-MA":
                        if plano_dados.get("base_adm_com_risco", False):
                            taxa_adm_total = arredondar((contrib_pura + valor_risco) * tx_adm_plano)
                        else:
                            taxa_adm_total = arredondar(contrib_pura * tx_adm_plano)
                        
                        st.success(f"### Salário Correspondente Necessário: R$ {formatar_br(salario_encontrado)}")
                        
                        st.markdown("#### Detalhamento da Contribuição Equivalente (Participante)")
                        col_f1, col_f2, col_f3 = st.columns(3)
                        col_f1.metric("Faixa Base (Até R$ 2.521,45)", f"R$ {formatar_br(f1)}")
                        col_f2.metric("Faixa Intermediária (Até R$ 5.042,89)", f"R$ {formatar_br(f2)}")
                        col_f3.metric("Faixa Topo (Excedente)", f"R$ {formatar_br(f3)}")
                        
                        st.markdown("### Composição do Boleto")
                        col_b1, col_b2, col_b3, col_b4 = st.columns(4)
                        col_b1.metric("Contribuição Pura", f"R$ {formatar_br(contrib_pura)}")
                        col_b2.metric("Contrib. Patrocinadora", "R$ 0,00")
                        
                        if tx_adm_plano > 0:
                            col_b3.metric(f"Taxa Administração ({formatar_br(tx_adm_plano * 100)}%)", f"R$ {formatar_br(taxa_adm_total)}")
                        else:
                            col_b3.metric("Taxa Administração", "0% (Não config.)")
                            
                        if tem_risco:
                            col_b4.metric(f"Taxa Risco ({formatar_br(tx_risco_plano * 100)}%)", f"R$ {formatar_br(valor_risco)}")
                        else:
                            col_b4.metric("Taxa Risco", "Sem Risco")
                            
                    elif plano_selecionado == "SESC SC (SESCPREV)":
                        contrib_patr = 0.0
                        taxa_adm_total = arredondar(contrib_pura * tx_adm_plano)
                        
                        st.success(f"### Salário Correspondente Necessário: R$ {formatar_br(salario_encontrado)}")
                        
                        st.markdown("#### Detalhamento da Contribuição Equivalente (Participante)")
                        st.info("Cálculo realizado via fator de Parcela a Deduzir (como INSS).")
                        col_f1, col_f2 = st.columns(2)
                        col_f1.metric("Valor Bruto (Alíquota Cheia)", f"R$ {formatar_br(f1)}")
                        if f2 > 0:
                            col_f2.metric("Parcela a Deduzir", f"- R$ {formatar_br(f2)}")
                        else:
                            col_f2.metric("Parcela a Deduzir", "Isento")
                            
                        st.markdown("### Composição do Boleto")
                        col_b1, col_b2, col_b3, col_b4 = st.columns(4)
                        col_b1.metric("Contrib. Participante", f"R$ {formatar_br(contrib_pura)}")
                        col_b2.metric("Contrib. Patrocinadora", "R$ 0,00")
                        col_b3.metric(f"Taxa Adm ({formatar_br(tx_adm_plano * 100)}%)", f"R$ {formatar_br(taxa_adm_total)}")
                        col_b4.metric(f"Taxa Risco", f"R$ {formatar_br(valor_risco)}")

                    elif plano_selecionado == "FIEP":
                        contrib_patr = 0.0
                        taxa_adm_total = arredondar(contrib_pura * tx_adm_plano)
                        
                        st.success(f"### Salário Correspondente Necessário: R$ {formatar_br(salario_encontrado)}")
                        
                        st.markdown("### Composição do Boleto")
                        col_b1, col_b2, col_b3, col_b4 = st.columns(4)
                        col_b1.metric("Contrib. Participante", f"R$ {formatar_br(contrib_pura)}")
                        col_b2.metric("Contrib. Patrocinadora", "R$ 0,00")
                        
                        if tx_adm_plano > 0:
                            col_b3.metric(f"Taxa Administração ({formatar_br(tx_adm_plano * 100)}%)", f"R$ {formatar_br(taxa_adm_total)}")
                        else:
                            col_b3.metric("Taxa Administração", "0% (Não config.)")
                            
                        if tem_risco and tx_risco_plano > 0:
                            col_b4.metric(f"Taxa Risco ({formatar_br(tx_risco_plano * 100)}%)", f"R$ {formatar_br(valor_risco)}")
                        else:
                            col_b4.metric("Taxa Risco", "Sem Risco")

                    else:
                        contrib_patr = 0.0
                        if plano_dados.get("base_adm_com_risco", False):
                            taxa_adm_total = arredondar((contrib_pura + valor_risco) * tx_adm_plano)
                        else:
                            taxa_adm_total = arredondar(contrib_pura * tx_adm_plano)
                        
                        st.success(f"### Salário Correspondente Necessário: R$ {formatar_br(salario_encontrado)}")
                        
                        st.markdown("### Composição do Boleto")
                        col_b1, col_b2, col_b3, col_b4 = st.columns(4)
                        col_b1.metric("Contrib. Participante", f"R$ {formatar_br(contrib_pura)}")
                        col_b2.metric("Contrib. Patrocinadora", "R$ 0,00")
                        
                        if tx_adm_plano > 0:
                            col_b3.metric(f"Taxa Administração ({formatar_br(tx_adm_plano * 100)}%)", f"R$ {formatar_br(taxa_adm_total)}")
                        else:
                            col_b3.metric("Taxa Administração", "0% (Não config.)")
                            
                        if tem_risco:
                            col_b4.metric(f"Taxa Risco ({formatar_br(tx_risco_plano * 100)}%)", f"R$ {formatar_br(valor_risco)}")
                        else:
                            col_b4.metric("Taxa Risco", "Sem Risco")
                else:
                    st.info("O cálculo de salário para este plano requer alinhamento de variáveis complexas.")
            else:
                st.warning("Insira um valor de cobrança válido.")


# =================================================================
# 6. TELA 2: CÁLCULO DE CONTRIBUIÇÃO EM LOTE
# =================================================================
elif menu_selecionado == "Cálculo de Contribuição em Lote":
    pv.titulo_pagina("📂 Cálculo de Contribuição em Lote")
    st.write("Selecione a modalidade e o plano para baixar a planilha modelo personalizada. Preencha os dados dos participantes e faça o upload para processar a contribuição sugerida.")

    col_m1, col_m2 = st.columns(2)
    with col_m1:
        modalidade_lote = st.selectbox("Selecione a Modalidade:", ["Ativo (Patrocinado)", "Autopatrocínio"], key="mod_lote_contrib")
    
    planos_lote_opcoes = [p for p in list(planos.keys()) if p not in ["FECOMERCIO", "PREVITÊ"]]
    if modalidade_lote == "Autopatrocínio":
        planos_lote_opcoes = [p for p in planos_lote_opcoes if p != "PREVISC SENAI-MA"]
        
    with col_m2:
        plano_lote_sel = st.selectbox("Selecione o Plano de Previdência:", options=planos_lote_opcoes, key="plano_lote_contrib")

    # Estruturar modelo específico para o plano selecionado
    def gerar_modelo_contribuicao(plano_nome, modalidade):
        cols = {"Matrícula / ID": ["1001", "1002"], "Nome Participante": ["João Silva", "Maria Santos"], "Salário Bruto": [5000.00, 8500.00]}
        
        if modalidade == "Ativo (Patrocinado)":
            if plano_nome == "FIEP":
                cols["Categoria Idade"] = ["Abaixo de 40 anos", "Acima de 40 anos"]
            elif plano_nome in ["PREVFIEPA", "PREVIFIEA"]:
                cols["Faixa Opção (1 a 6)"] = [1, 2]
            elif plano_nome == "PREVISC SENAI-MA":
                cols["Faixa FIEMA (1 a 3)"] = [1, 2]
            elif plano_nome == "UNIVALIPrevidencia":
                cols["Categoria"] = ["Migrante", "Não Migrante"]
                cols["Tipo Contribuição"] = ["Normal", "Reduzida"]
                cols["Tempo Empresa (Anos)"] = [5, 12]
            elif plano_nome == "UNERJPREV":
                cols["Idade"] = [35, 48]
            elif plano_nome == "LUNELLIPREV":
                cols["Alíquota %"] = [10.0, 12.0]
        else: # Autopatrocínio
            if plano_nome in ["PREVFIEPA", "PREVIFIEA"]:
                cols["Faixa Opção (1 a 6)"] = [1, 2]
            elif plano_nome == "UNERJPREV":
                cols["Idade"] = [35, 48]

        return pd.DataFrame(cols)

    df_modelo = gerar_modelo_contribuicao(plano_lote_sel, modalidade_lote)
    
    buffer_modelo = io.BytesIO()
    with pd.ExcelWriter(buffer_modelo, engine='openpyxl') as writer:
        df_modelo.to_excel(writer, index=False, sheet_name="Modelo_Contribuicao")
    
    st.download_button(
        label=f"📥 Baixar Planilha Modelo ({plano_lote_sel} - {modalidade_lote})", 
        data=buffer_modelo.getvalue(), 
        file_name=f"modelo_contrib_{plano_lote_sel.replace(' ', '_')}_{modalidade_lote.split()[0]}.xlsx", 
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    
    st.divider()
    
    st.subheader(f"Processar Base de Dados - {plano_lote_sel} ({modalidade_lote})")
    arquivo_upload = st.file_uploader(f"Faça o upload da planilha preenchida do plano {plano_lote_sel} (.xlsx)", type=["xlsx"], key="up_contrib")
    
    if arquivo_upload is not None:
        try:
            df_lote = pd.read_excel(arquivo_upload)
            
            res_contrib_sugerida = []
            
            for idx, row in df_lote.iterrows():
                salario = float(row.get("Salário Bruto", 0.0)) if pd.notna(row.get("Salário Bruto")) else 0.0
                
                idade_ou_tempo = 30
                if "Idade" in df_lote.columns and pd.notna(row.get("Idade")):
                    idade_ou_tempo = int(row.get("Idade"))
                elif "Tempo Empresa (Anos)" in df_lote.columns and pd.notna(row.get("Tempo Empresa (Anos)")):
                    idade_ou_tempo = int(row.get("Tempo Empresa (Anos)"))
                    
                faixa_opt = "Faixa 1"
                if "Faixa Opção (1 a 6)" in df_lote.columns and pd.notna(row.get("Faixa Opção (1 a 6)")):
                    faixa_opt = f"Faixa {str(row.get('Faixa Opção (1 a 6)')).split('.')[0].strip()}"
                elif "Faixa FIEMA (1 a 3)" in df_lote.columns and pd.notna(row.get("Faixa FIEMA (1 a 3)")):
                    faixa_opt = f"Faixa {str(row.get('Faixa FIEMA (1 a 3)')).split('.')[0].strip()}"

                aliq_escolhida = None
                if "Alíquota %" in df_lote.columns and pd.notna(row.get("Alíquota %")):
                    aliq_escolhida = float(row.get("Alíquota %")) / 100.0

                univali_migrante = str(row.get("Categoria", "Migrante")).strip() if "Categoria" in df_lote.columns and pd.notna(row.get("Categoria")) else "Migrante"
                univali_tipo = str(row.get("Tipo Contribuição", "Normal")).strip() if "Tipo Contribuição" in df_lote.columns and pd.notna(row.get("Tipo Contribuição")) else "Normal"
                
                if modalidade_lote == "Autopatrocínio" and plano_lote_sel == "UNIVALIPrevidencia":
                    categoria_part = "Não Migrante"
                    univali_migrante = "Não Migrante"
                    univali_tipo = "Normal"
                    idade_ou_tempo = 10

                is_auto = (modalidade_lote == "Autopatrocínio")
                total_sugerida = calcular_contribuicao(plano_lote_sel, salario, aliq_escolhida, univali_migrante, univali_tipo, idade_ou_tempo, faixa_opt, is_autopatrocinio=is_auto)[0]
                
                res_contrib_sugerida.append(formatar_br(total_sugerida))

            df_lote["Contribuição Sugerida (R$)"] = res_contrib_sugerida
            
            st.success("Cálculo em lote finalizado com sucesso!")
            st.dataframe(df_lote, use_container_width=True)
            
            buffer_resultado = io.BytesIO()
            with pd.ExcelWriter(buffer_resultado, engine='openpyxl') as writer:
                df_lote.to_excel(writer, index=False, sheet_name="Resultados_Previsc")
                
            st.download_button(
                label="📤 Baixar Resultados Processados", 
                data=buffer_resultado.getvalue(), 
                file_name=f"resultado_contrib_{plano_lote_sel.replace(' ', '_')}.xlsx", 
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except Exception as e:
            st.error(f"Erro ao processar a planilha. Detalhe: {e}")


# =================================================================
# 7. TELA 3: CÁLCULO DE SALÁRIO EM LOTE
# =================================================================
elif menu_selecionado == "Cálculo de Salário em Lote":
    pv.titulo_pagina("📂 Cálculo de Salário em Lote")
    st.write("Selecione a modalidade e o plano para baixar a planilha modelo de cálculo reverso. Preencha a contribuição alvo dos participantes para descobrir o salário exato necessário.")

    col_sm1, col_sm2 = st.columns(2)
    with col_sm1:
        modalidade_sal_lote = st.selectbox("Selecione a Modalidade:", ["Ativo (Patrocinado)", "Autopatrocínio"], key="mod_lote_sal")
    
    planos_sal_lote_opcoes = [p for p in list(planos.keys()) if p not in ["FECOMERCIO", "PREVITÊ"]]
    if modalidade_sal_lote == "Autopatrocínio":
        planos_sal_lote_opcoes = [p for p in planos_sal_lote_opcoes if p != "PREVISC SENAI-MA"]

    with col_sm2:
        plano_sal_lote_sel = st.selectbox("Selecione o Plano de Previdência:", options=planos_sal_lote_opcoes, key="plano_lote_sal")

    def gerar_modelo_salario(plano_nome, modalidade):
        label_alvo = "Contribuição Alvo"
        cols = {"Matrícula / ID": ["1001", "1002"], "Nome Participante": ["João Silva", "Maria Santos"], label_alvo: [250.00, 480.00]}
        
        if modalidade == "Ativo (Patrocinado)":
            if plano_nome == "FIEP":
                cols["Categoria Idade"] = ["Abaixo de 40 anos", "Acima de 40 anos"]
            elif plano_nome in ["PREVFIEPA", "PREVIFIEA"]:
                cols["Faixa Opção (1 a 6)"] = [1, 2]
            elif plano_nome == "PREVISC SENAI-MA":
                cols["Faixa FIEMA (1 a 3)"] = [1, 2]
            elif plano_nome == "UNIVALIPrevidencia":
                cols["Categoria"] = ["Migrante", "Não Migrante"]
                cols["Tipo Contribuição"] = ["Normal", "Reduzida"]
                cols["Tempo Empresa (Anos)"] = [5, 12]
            elif plano_nome == "UNERJPREV":
                cols["Idade"] = [35, 48]
            elif plano_nome == "LUNELLIPREV":
                cols["Alíquota %"] = [10.0, 12.0]
        else: # Autopatrocínio
            if plano_nome in ["PREVFIEPA", "PREVIFIEA"]:
                cols["Faixa Opção (1 a 6)"] = [1, 2]
            elif plano_nome == "UNERJPREV":
                cols["Idade"] = [35, 48]

        return pd.DataFrame(cols)

    df_modelo_rev = gerar_modelo_salario(plano_sal_lote_sel, modalidade_sal_lote)
    
    buffer_modelo_rev = io.BytesIO()
    with pd.ExcelWriter(buffer_modelo_rev, engine='openpyxl') as writer:
        df_modelo_rev.to_excel(writer, index=False, sheet_name="Modelo_Salario")
    
    st.download_button(
        label=f"📥 Baixar Planilha Modelo Salário ({plano_sal_lote_sel} - {modalidade_sal_lote})", 
        data=buffer_modelo_rev.getvalue(), 
        file_name=f"modelo_salario_{plano_sal_lote_sel.replace(' ', '_')}_{modalidade_sal_lote.split()[0]}.xlsx", 
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    
    st.divider()
    
    st.subheader(f"Processar Base de Dados - {plano_sal_lote_sel} ({modalidade_sal_lote})")
    arquivo_upload_rev = st.file_uploader(f"Faça o upload da planilha preenchida do plano {plano_sal_lote_sel} (.xlsx)", type=["xlsx"], key="up_salario")
    
    if arquivo_upload_rev is not None:
        try:
            df_lote_rev = pd.read_excel(arquivo_upload_rev)
            
            resultados_sal = []
            col_alvo_nome = "Contribuição Alvo"
            
            for idx, row in df_lote_rev.iterrows():
                alvo = float(row.get(col_alvo_nome, 0.0)) if pd.notna(row.get(col_alvo_nome)) else 0.0
                
                idade_ou_tempo = 30
                if "Idade" in df_lote_rev.columns and pd.notna(row.get("Idade")):
                    idade_ou_tempo = int(row.get("Idade"))
                elif "Tempo Empresa (Anos)" in df_lote_rev.columns and pd.notna(row.get("Tempo Empresa (Anos)")):
                    idade_ou_tempo = int(row.get("Tempo Empresa (Anos)"))
                    
                faixa_opt = "Faixa 1"
                if "Faixa Opção (1 a 6)" in df_lote_rev.columns and pd.notna(row.get("Faixa Opção (1 a 6)")):
                    faixa_opt = f"Faixa {str(row.get('Faixa Opção (1 a 6)')).split('.')[0].strip()}"
                elif "Faixa FIEMA (1 a 3)" in df_lote_rev.columns and pd.notna(row.get("Faixa FIEMA (1 a 3)")):
                    faixa_opt = f"Faixa {str(row.get('Faixa FIEMA (1 a 3)')).split('.')[0].strip()}"

                aliq_escolhida = None
                if "Alíquota %" in df_lote_rev.columns and pd.notna(row.get("Alíquota %")):
                    aliq_escolhida = float(row.get("Alíquota %")) / 100.0

                univali_migrante = str(row.get("Categoria", "Migrante")).strip() if "Categoria" in df_lote_rev.columns and pd.notna(row.get("Categoria")) else "Migrante"
                univali_tipo = str(row.get("Tipo Contribuição", "Normal")).strip() if "Tipo Contribuição" in df_lote_rev.columns and pd.notna(row.get("Tipo Contribuição")) else "Normal"
                
                is_auto = (modalidade_sal_lote == "Autopatrocínio")
                
                if is_auto:
                    if plano_sal_lote_sel == "UNIVALIPrevidencia":
                        categoria_part = "Não Migrante"
                        univali_migrante = "Não Migrante"
                        univali_tipo = "Normal"
                        idade_ou_tempo = 10
                    else:
                        categoria_part = "Não Migrante"
                        
                    salario_calc = descobrir_salario_autopatrocinio(plano_sal_lote_sel, alvo, aliq_escolhida, univali_migrante, univali_tipo, idade_ou_tempo, faixa_opt, categoria_part)
                else:
                    salario_calc = calcular_salario_reverso(plano_sal_lote_sel, alvo, aliq_escolhida, univali_migrante, univali_tipo, idade_ou_tempo, faixa_opt)

                if salario_calc == 0.0:
                    resultados_sal.append("Cálculo Incompatível")
                else:
                    resultados_sal.append(formatar_br(salario_calc))

            df_lote_rev["Salário Exato Necessário (R$)"] = resultados_sal
            
            st.success("Cálculo em lote finalizado com sucesso!")
            st.dataframe(df_lote_rev, use_container_width=True)
            
            buffer_resultado_rev = io.BytesIO()
            with pd.ExcelWriter(buffer_resultado_rev, engine='openpyxl') as writer:
                df_lote_rev.to_excel(writer, index=False, sheet_name="Resultados_Previsc")
                
            st.download_button(
                label="📤 Baixar Resultados Processados", 
                data=buffer_resultado_rev.getvalue(), 
                file_name=f"resultado_salario_{plano_sal_lote_sel.replace(' ', '_')}.xlsx", 
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except Exception as e:
            st.error(f"Erro ao processar a planilha. Detalhe: {e}")


# =================================================================
# 8. TELA 4: REGRAS E BASES DE CÁLCULO
# =================================================================
elif menu_selecionado == "Regras e Bases de Cálculo":
    pv.titulo_pagina("📖 Regras e Bases de Cálculo")
    st.write("Consulte abaixo os indexadores atuais e a estrutura de cálculo configurada para cada plano de previdência no sistema.")
    
    dados_tabela = [
        {"Plano": "FIESCPREV", "Indexador": "UR", "Valor (R$)": "716,84", "Regra de Cálculo": "Faixas: 3% (Até 7 UR) | 14% (Acima) - Taxa Adm total = (Participante + Patrocinadora) * 2,18%. Risco não gera taxa adm."},
        {"Plano": "FIEP", "Indexador": "UR", "Valor (R$)": "781,42", "Regra de Cálculo": "Faixas: 3% (Até 8,5 UR) | 7,5% (Acima). Patrocinadora aporta 50% (< 40 anos) ou 100% (>= 40 anos)."},
        {"Plano": "SENACPREV", "Indexador": "UR", "Valor (R$)": "734,75", "Regra de Cálculo": "Faixas: 2,3% (Até 8 UR) | 7,4% (Acima)"},
        {"Plano": "SENAI-PIPREV", "Indexador": "UR", "Valor (R$)": "7.376,89", "Regra de Cálculo": "Faixas Cascata: 1% (Até 0,5) | 4% (0,5 a 1) | 8% (Acima) - Desconto Superávit (7,28%). Taxa Adm = 2,18% sobre o dobro da cota pura. Aporte da Patrocinadora deduz a taxa adm."},
        {"Plano": "PREVISC SENAI-MA", "Indexador": "Valores Fixos", "Valor (R$)": "-", "Regra de Cálculo": "Cascata de Múltiplas Faixas: De 1,50% a 16,10% dependendo da opção escolhida pelo participante (Faixas: R$ 2.521,45 e R$ 5.042,89)"},
        {"Plano": "PREVFIEPA", "Indexador": "UP", "Valor (R$)": "7.740,09", "Regra de Cálculo": "Cascata de Múltiplas Faixas (6 Faixas). Taxa Adm (4%) aplicada sobre a Patrocinadora. Risco (2,35%) aplicado sobre (Patrocinadora - Adm)."},
        {"Plano": "FECOMERCIO", "Indexador": "UR", "Valor (R$)": "845,22", "Regra de Cálculo": "Faixas: 2,3% (Até 8 UR) | 7,4% (Acima)"},
        {"Plano": "FIEMTPREV", "Indexador": "UR", "Valor (R$)": "715,77", "Regra de Cálculo": "Faixas: 2% (Até 12,06 UR) | 7,25% (Acima) - Taxa Adm: 2,18%. O participante assume a regra integral como Não Migrante."},
        {"Plano": "UNIVALIPrevidencia", "Indexador": "UR", "Valor (R$)": "627,19", "Regra de Cálculo": "Faixa Fixa: 3% (Até 8 UR) | Excedente: 14% ou 17% variando por Categoria - Taxa Adm: 2,18% - Risco Autopatrocínio: Isento - Contrapartida: 50% (< 10 anos) ou 100% (>= 10 anos) da sugerida, zera se Tempo >= 35 (Não Migrante) ou >= 30 (Migrante)."},
        {"Plano": "SESI-PIPREV", "Indexador": "SP", "Valor (R$)": "6.812,53", "Regra de Cálculo": "Fórmula Direta c/ Parcela a Deduzir: (Salário * 13,7741%) - (SP * 12,2124%). Taxa Adm: 2,18% (Descontada do aporte da Patrocinadora)."},
        {"Plano": "SESC SC (SESCPREV)", "Indexador": "UR", "Valor (R$)": "922,63", "Regra de Cálculo": "Faixas de Dedução dinâmicas (Até 10 URs | 10 a 11.4288 URs | Acima). Taxa Adm: 2,18%. Risco opcional: 0,12%. Autopatrocínio exige cota do Risco."},
        {"Plano": "LUNELLIPREV", "Indexador": "Salário", "Valor (R$)": "-", "Regra de Cálculo": "Ativo: Livre Escolha (Mín. 1%). Autopatrocinado: Fixo 10% do salário. Patrocinadora: 10% da contrib. do participante. Taxa Adm: Isento no boleto (cobrado do saldo)."},
        {"Plano": "PREVIFIEA", "Indexador": "UP", "Valor (R$)": "8.258,59", "Regra de Cálculo": "Cascata de Múltiplas Faixas (6 Faixas). Taxa Adm (4%) aplicada sobre a Patrocinadora. Risco (2,35%) aplicado sobre (Patrocinadora - Adm)."},
        {"Plano": "UNERJPREV", "Indexador": "INSS", "Valor (R$)": "8.475,55", "Regra de Cálculo": "Base Inteira Única: 0,25% (Até 1 Teto). Acima de 1 Teto aplica 3% a 6% retroativo sobre a Base Total conforme a idade."},
        {"Plano": "PREVITÊ", "Indexador": "-", "Valor (R$)": "-", "Regra de Cálculo": "Contribuição Fixa / Regulamento Fechado"}
    ]
    
    st.dataframe(pd.DataFrame(dados_tabela), use_container_width=True, hide_index=True)
