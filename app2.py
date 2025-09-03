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

# Estilos CSS personalizados
st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem;
        color: #1E3A8A;
        font-weight: 800;
        margin-bottom: 2rem;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #3B82F6;
    }
    .sub-header {
        font-size: 1.8rem;
        color: #374151;
        font-weight: 700;
        margin: 2rem 0 1.5rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #E5E7EB;
    }
    .metric-card {
        background-color: #1E293B;
        border-radius: 0.75rem;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        height: 100%;
        border-left: 5px solid #3B82F6;
        margin-bottom: 1.5rem;
    }
    .metric-title {
        font-size: 1rem;
        color: #93C5FD;
        font-weight: 600;
        margin-bottom: 0.75rem;
    }
    .metric-value {
        font-size: 1.8rem;
        color: #FFFFFF;
        font-weight: 800;
    }
    .positive-value {
        color: #10B981;
    }
    .negative-value {
        color: #EF4444;
    }
    .section-container {
        background-color: #0F172A;
        border-radius: 1rem;
        padding: 1.5rem;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.4);
    }
    .timeline-container {
        background-color: #1E293B;
        border-radius: 1rem;
        padding: 1.5rem;
        margin-top: 2rem;
    }
    .stSelectbox > div > div {
        background-color: #1E293B;
        color: white;
    }
    .stSelectbox label {
        color: #93C5FD !important;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Título principal
st.markdown('<p class="main-header">🏗️ Dashboard de Obras</p>', unsafe_allow_html=True)

# Upload da planilha
st.markdown('<p class="sub-header">📁 Upload da Planilha</p>', unsafe_allow_html=True)
uploaded_file = st.file_uploader("Escolha o arquivo Excel com os dados das obras:", type=['xlsx', 'xls'], label_visibility="collapsed")

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
            elif isinstance(value, (int, float)) and value > 1:
                return f"{value:.1f}%"
            elif isinstance(value, str) and '%' in value:
                return value
            return str(value)
        
        # Primeira seção - Métricas Principais
        st.markdown('<p class="sub-header">📊 Métricas Principais</p>', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown('<div class="metric-card"><p class="metric-title">Total Unidades</p><p class="metric-value">' + str(get_value("Total Unidades")) + '</p></div>', unsafe_allow_html=True)
        
        with col2:
            ac = get_value("AC(m²)")
            ac_value = f"{ac:,.0f}" if isinstance(ac, (int, float)) else str(ac)
            st.markdown(f'<div class="metric-card"><p class="metric-title">AC(m²)</p><p class="metric-value">{ac_value}</p></div>', unsafe_allow_html=True)
        
        with col3:
            ap = get_value("AP(m²)")
            ap_value = f"{ap:,.0f}" if isinstance(ap, (int, float)) else str(ap)
            st.markdown(f'<div class="metric-card"><p class="metric-title">AP(m²)</p><p class="metric-value">{ap_value}</p></div>', unsafe_allow_html=True)
        
        with col4:
            rentab_viab = get_value("Rentab. Viabilidade")
            st.markdown(f'<div class="metric-card"><p class="metric-title">Rentab. Viabilidade</p><p class="metric-value">{format_percent(rentab_viab)}</p></div>', unsafe_allow_html=True)
        
        col5, col6, col7, col8 = st.columns(4)
        
        with col5:
            rentab_proj = get_value("Rentab. Projetada")
            st.markdown(f'<div class="metric-card"><p class="metric-title">Rentab. Projetada</p><p class="metric-value">{format_percent(rentab_proj)}</p></div>', unsafe_allow_html=True)
        
        with col6:
            custo_ac = get_value("Custo Atual AC")
            st.markdown(f'<div class="metric-card"><p class="metric-title">Custo AC</p><p class="metric-value">{format_money(custo_ac)}</p></div>', unsafe_allow_html=True)
        
        with col7:
            custo_ap = get_value("Custo Atual AP")
            st.markdown(f'<div class="metric-card"><p class="metric-title">Custo AP</p><p class="metric-value">{format_money(custo_ap)}</p></div>', unsafe_allow_html=True)
        
        # Segunda seção - Análise Financeira com gráfico
        st.markdown('<p class="sub-header">💰 Análise Financeira</p>', unsafe_allow_html=True)
        
        # Dados para o gráfico de orçamento
        orc_base = get_value("Orçamento Base", 0)
        orc_reaj = get_value("Orçamento Reajustado", 0)
        custo_final = get_value("Custo Final", 0)
        
        if isinstance(orc_base, str):
            try:
                orc_base = float(orc_base.replace('R$', '').replace('.', '').replace(',', '.'))
            except:
                orc_base = 0
                
        if isinstance(orc_reaj, str):
            try:
                orc_reaj = float(orc_reaj.replace('R$', '').replace('.', '').replace(',', '.'))
            except:
                orc_reaj = 0
                
        if isinstance(custo_final, str):
            try:
                custo_final = float(custo_final.replace('R$', '').replace('.', '').replace(',', '.'))
            except:
                custo_final = 0
        
        # Criar gráfico de barras para orçamento
        fig_orcamento = go.Figure()
        
        fig_orcamento.add_trace(go.Bar(
            x=['Orçamento Base', 'Orçamento Reajustado', 'Custo Final'],
            y=[orc_base, orc_reaj, custo_final],
            marker_color=['#3B82F6', '#60A5FA', '#10B981'],
            text=[format_money(orc_base), format_money(orc_reaj), format_money(custo_final)],
            textposition='auto',
        ))
        
        fig_orcamento.update_layout(
            title='Comparativo de Orçamento',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            height=400,
            showlegend=False
        )
        
        st.plotly_chart(fig_orcamento, use_container_width=True)
        
        # Terceira seção - Prazos e Avanço com velocímetro aprimorado
        st.markdown('<p class="sub-header">📅 Prazos e Avanço Físico</p>', unsafe_allow_html=True)
        
        col9, col10, col11 = st.columns([2, 1, 1])
        
        with col9:
            # Converter avanço real para número
            av_real_num = get_value("Avanço Físico Real", 0)
            av_plan_num = get_value("Avanço Físico Planejado", 1)
            aderencia = get_value("Aderência Física", 0)
            
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
            
            if isinstance(aderencia, str):
                try:
                    aderencia = float(aderencia.replace('%', '').replace(',', '.'))
                except:
                    aderencia = 0
            
            # Se os valores estão entre 0-1, converter para 0-100
            if av_real_num <= 1:
                av_real_num *= 100
            if av_plan_num <= 1:
                av_plan_num *= 100
            if aderencia <= 1:
                aderencia *= 100
            
            # Velocímetro simplificado e limpo
            fig_velocimetro = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=av_real_num,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={
                    'text': "Avanço Físico Real vs Planejado",
                    'font': {'size': 16, 'color': 'white'}
                },
                number={
                    'font': {'size': 40, 'color': 'white'},
                    'suffix': '%',
                    'valueformat': '.1f'
                },
                delta={
                    'reference': av_plan_num,
                    'increasing': {'color': "#10B981"},
                    'decreasing': {'color': "#EF4444"},
                    'font': {'size': 16}
                },
                gauge={
                    'axis': {
                        'range': [0, 100],
                        'tickwidth': 1,
                        'tickcolor': "white",
                        'tickfont': {'size': 12, 'color': 'white'}
                    },
                    'bar': {'color': "#3B82F6", 'thickness': 0.25},
                    'bgcolor': "rgba(0,0,0,0)",
                    'borderwidth': 2,
                    'bordercolor': "gray",
                    'steps': [
                        {'range': [0, 70], 'color': 'rgba(239, 68, 68, 0.3)'},
                        {'range': [70, 90], 'color': 'rgba(245, 158, 11, 0.3)'},
                        {'range': [90, 100], 'color': 'rgba(16, 185, 129, 0.3)'}
                    ],
                    'threshold': {
                        'line': {'color': "#F59E0B", 'width': 4},
                        'thickness': 0.75,
                        'value': av_plan_num
                    }
                }
            ))
            
            fig_velocimetro.update_layout(
                height=400,
                font={'color': "white", 'family': "Arial"},
                margin=dict(l=30, r=30, t=80, b=30),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            
            st.plotly_chart(fig_velocimetro, use_container_width=True)
        
        with col10:
            st.markdown(f'<div class="metric-card"><p class="metric-title">Avanço Planejado</p><p class="metric-value">{format_percent(av_plan_num)}</p></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-card"><p class="metric-title">Avanço Real</p><p class="metric-value">{format_percent(av_real_num)}</p></div>', unsafe_allow_html=True)
        
        with col11:
            st.markdown(f'<div class="metric-card"><p class="metric-title">Aderência Física</p><p class="metric-value">{format_percent(aderencia)}</p></div>', unsafe_allow_html=True)
            desvio = get_value("Desvio")
            st.markdown(f'<div class="metric-card"><p class="metric-title">Desvio</p><p class="metric-value">{str(desvio)}</p></div>', unsafe_allow_html=True)
        
        # Quarta seção - Linha do tempo
        st.markdown('<p class="sub-header">⏰ Linha do Tempo</p>', unsafe_allow_html=True)
        
        # Obter datas
        inicio = get_value("Início", "N/A")
        tend = get_value("Tend", "N/A")
        prazo_concl = get_value("Prazo Concl.", "N/A")
        prazo_cliente = get_value("Prazo Cliente", "N/A")
        
        # Criar linha do tempo
        fig_timeline = go.Figure()
        
        # Adicionar marcadores para cada data
        dates = [inicio, tend, prazo_concl, prazo_cliente]
        labels = ["Início", "Tendência", "Prazo Conclusão", "Prazo Cliente"]
        colors = ["#3B82F6", "#F59E0B", "#10B981", "#EF4444"]
        
        # Converter para datas se possível
        date_values = []
        for d in dates:
            if isinstance(d, (datetime, pd.Timestamp)):
                date_values.append(d)
            elif isinstance(d, str) and d != "N/A":
                try:
                    date_values.append(pd.to_datetime(d))
                except:
                    date_values.append(None)
            else:
                date_values.append(None)
        
        # Criar linha do tempo apenas se temos pelo menos duas datas válidas
        valid_dates = [d for d in date_values if d is not None]
        if len(valid_dates) >= 2:
            min_date = min(valid_dates)
            max_date = max(valid_dates)
            
            # Adicionar linha de tempo
            fig_timeline.add_trace(go.Scatter(
                x=[min_date, max_date],
                y=[0, 0],
                mode='lines',
                line=dict(color='white', width=3),
                showlegend=False
            ))
            
            # Adicionar marcadores
            for i, (date, label, color) in enumerate(zip(date_values, labels, colors)):
                if date is not None:
                    fig_timeline.add_trace(go.Scatter(
                        x=[date],
                        y=[0],
                        mode='markers+text',
                        marker=dict(size=15, color=color),
                        text=[label],
                        textposition="top center",
                        name=label,
                        textfont=dict(color='white', size=12)
                    ))
            
            fig_timeline.update_layout(
                title='Cronograma da Obra',
                showlegend=True,
                height=300,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                xaxis=dict(showgrid=False, zeroline=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
            )
            
            st.plotly_chart(fig_timeline, use_container_width=True)
        else:
            st.info("Não há datas suficientes para criar a linha do tempo.")
        
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
st.markdown("<div style='text-align: center; color: #6B7280;'>Dashboard atualizado em tempo real | Dados da obra selecionada</div>", unsafe_allow_html=True)
