import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

# Configuração da página
st.set_page_config(
    page_title="Dashboard de Obras",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Título principal
st.title("🏗️ Dashboard de Obras")

# Upload da planilha
st.subheader("📁 Upload da Planilha")
uploaded_file = st.file_uploader("Escolha o arquivo Excel com os dados das obras:", type=['xlsx', 'xls'])

if uploaded_file is not None:
    try:
        # Carregar todas as abas do Excel
        excel_file = pd.ExcelFile(uploaded_file)
        sheet_names = excel_file.sheet_names
        
        # Selectbox para escolher a aba
        selected_sheet = st.selectbox("Escolha a obra (aba da planilha):", sheet_names)
        
        # Carregar dados da aba selecionada
        df = pd.read_excel(uploaded_file, sheet_name=selected_sheet)
        
        # Verificar se tem pelo menos 2 colunas
        if df.shape[1] < 2:
            st.error("A planilha precisa ter pelo menos 2 colunas (A: Métricas, B: Valores)")
            st.stop()
        
        # Assumir que coluna 0 são as métricas e coluna 1 são os valores
        df_clean = df.iloc[:, [0, 1]].dropna()
        df_clean.columns = ['Metrica', 'Valor']
        
        # Criar dicionário com os dados
        dados = {}
        for _, row in df_clean.iterrows():
            dados[str(row['Metrica']).strip()] = row['Valor']
        
        st.success(f"✅ Dados carregados da aba: **{selected_sheet}**")
        
        # Função para buscar valor no dicionário
        def get_value(key, default="N/A"):
            return dados.get(key, default)
        
        # Função para formatar valores monetários
        def format_money(value):
            if isinstance(value, (int, float)):
                return f"R$ {value:,.0f}".replace(',', '.')
            elif isinstance(value, str) and 'R$' in value:
                return value
            return str(value)
        
        # Função para formatar percentuais
        def format_percent(value):
            if isinstance(value, (int, float)) and value <= 1:
                return f"{value*100:.1f}%"
            elif isinstance(value, str) and '%' in value:
                return value
            return str(value)
        
        # Primeira seção - Métricas Principais em linha
        st.subheader("📊 Métricas Principais")
        
        col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
        
        with col1:
            total_unidades = get_value("Total Unidades")
            st.metric("Total Unidades", str(total_unidades))
        
        with col2:
            ac = get_value("AC(m²)")
            st.metric("AC(m²)", f"{ac:,.0f}" if isinstance(ac, (int, float)) else str(ac))
        
        with col3:
            ap = get_value("AP(m²)")
            st.metric("AP(m²)", f"{ap:,.0f}" if isinstance(ap, (int, float)) else str(ap))
        
        with col4:
            rentab_viab = get_value("Rentab. Viabilidade")
            st.metric("Rentab. Viabilidade", format_percent(rentab_viab))
        
        with col5:
            rentab_proj = get_value("Rentab. Projetada")
            st.metric("Rentab. Projetada", format_percent(rentab_proj))
        
        with col6:
            custo_ac = get_value("Custo Atual AC")
            st.metric("Custo AC", format_money(custo_ac))
        
        with col7:
            custo_ap = get_value("Custo Atual AP")
            st.metric("Custo AP", format_money(custo_ap))
        
        # Segunda seção - Análise Financeira
        st.subheader("💰 Análise Financeira")
        
        col8, col9, col10, col11, col12, col13, col14 = st.columns(7)
        
        with col8:
            orc_base = get_value("Orçamento Base")
            st.metric("Orçamento Base", format_money(orc_base))
        
        with col9:
            orc_reaj = get_value("Orçamento Reajustado")
            st.metric("Orç. Reajustado", format_money(orc_reaj))
        
        with col10:
            custo_final = get_value("Custo Final")
            st.metric("Custo Final", format_money(custo_final))
        
        with col11:
            desvio = get_value("Desvio")
            st.metric("Desvio", str(desvio))
        
        with col12:
            desembolso = get_value("Desembolso")
            st.metric("Desembolso", format_money(desembolso))
        
        with col13:
            saldo = get_value("Saldo")
            st.metric("Saldo", format_money(saldo))
        
        with col14:
            indice_econ = get_value("Índice Econômico")
            st.metric("Índice Econômico", str(indice_econ))
        
        # Terceira seção - Prazos e Avanço
        st.subheader("📅 Prazos e Avanço Físico")
        
        col15, col16, col17, col18, col19, col20, col21 = st.columns(7)
        
        with col15:
            av_plan = get_value("Avanço Físico Planejado")
            st.metric("Avanço Planejado", format_percent(av_plan))
        
        with col16:
            av_real = get_value("Avanço Físico Real")
            st.metric("Avanço Real", format_percent(av_real))
        
        with col17:
            aderencia = get_value("Aderência Física")
            st.metric("Aderência Física", format_percent(aderencia))
        
        with col18:
            inicio = get_value("Início")
            st.metric("Início", str(inicio))
        
        with col19:
            tend = get_value("Tend")
            st.metric("Tendência", str(tend))
        
        with col20:
            prazo_concl = get_value("Prazo Concl.")
            st.metric("Prazo Conclusão", str(prazo_concl))
        
        with col21:
            prazo_cliente = get_value("Prazo Cliente")
            st.metric("Prazo Cliente", str(prazo_cliente))
        
        # Velocímetro de Avanço Físico
        st.subheader("⚡ Velocímetro de Avanço")
        
        col_vel, col_space = st.columns([3, 1])
        
        with col_vel:
            # Converter avanço real para número
            av_real_num = get_value("Avanço Físico Real", 0)
            av_plan_num = get_value("Avanço Físico Planejado", 1)
            
            if isinstance(av_real_num, str):
                try:
                    av_real_num = float(av_real_num.replace('%', '').replace(',', '.'))
                except:
                    av_real_num = 0
            
            if isinstance(av_plan_num, str):
                try:
                    av_plan_num = float(av_plan_num.replace('%', '').replace(',', '.'))
                except:
                    av_plan_num = 100
            
            # Se os valores estão entre 0-1, converter para 0-100
            if av_real_num <= 1:
                av_real_num *= 100
            if av_plan_num <= 1:
                av_plan_num *= 100
            
            fig_velocimetro = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = av_real_num,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Avanço Físico Real (%)"},
                delta = {'reference': av_plan_num, 'suffix': "% da meta"},
                gauge = {
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "#2E86C1"},
                    'steps': [
                        {'range': [0, 50], 'color': "#E74C3C"},
                        {'range': [50, 80], 'color': "#F39C12"},
                        {'range': [80, 100], 'color': "#27AE60"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': av_plan_num
                    }
                }
            ))
            fig_velocimetro.update_layout(height=400)
            st.plotly_chart(fig_velocimetro, use_container_width=True)
        
        # Mostrar dados carregados (debug)
        with st.expander("🔍 Visualizar dados carregados"):
            st.dataframe(df_clean, use_container_width=True)
            
    except Exception as e:
        st.error(f"Erro ao carregar a planilha: {str(e)}")
        st.info("Certifique-se de que a planilha tem o formato correto: Coluna A (Métricas), Coluna B (Valores)")

else:
    st.warning("⚠️ Por favor, faça upload da planilha Excel para visualizar os dados das obras.")
    st.info("**Formato esperado:** Coluna A com nomes das métricas, Coluna B com os valores correspondentes")

# Footer
st.markdown("---")
st.markdown("Dashboard atualizado em tempo real | Dados da obra selecionada")
