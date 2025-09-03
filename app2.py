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
st.title("📊 Dashboard do Projeto de Construção")

# Dados do projeto
data = {
    'Métrica': [
        'AC(m²)', 'AP(m²)', 'Ef', 'Total Unidades', 'Avanço Físico Planejado',
        'Avanço Físico Real', 'Aderência Física', 'Início', 'Tend', 'Prazo Concl.',
        'Prazo Cliente', 'Orçamento Base', 'Orçamento Reajustado', 'Custo Final',
        'Desvio', 'Desembolso', 'Saldo', 'Índice Econômico', 'Rentab. Viabilidade',
        'Rentab. Projetada', 'Custo Atual AC', 'Custo Atual AP'
    ],
    'Valor': [
        29651.00, 14887.00, '50,21%', 80.00, 0.99, 0.92, 0.94, '1-jun', '1-set',
        '1-ago', '1-nov', 'R$ 102.593.965,36', 'R$ 104.856.979,36', 'R$ 104.856.979,36',
        1.12, 'R$ 95.337.442,00', 'R$ 9.519.537,36', 1.01, '22%', '17%',
        'R$ 3.574,04', 'R$ 7.118,56'
    ]
}

df = pd.DataFrame(data)

# Layout em colunas
col1, col2, col3 = st.columns([1, 1, 1])

# Primeira coluna - Métricas Físicas
with col1:
    st.subheader("📐 Métricas Físicas")
    
    # Cards de métricas físicas
    st.metric("Área Construída (AC)", "29.651 m²", delta=None)
    st.metric("Área Privativa (AP)", "14.887 m²", delta=None)
    st.metric("Eficiência", "50,21%", delta=None)
    st.metric("Total de Unidades", "80", delta=None)
    
    # Gráfico de avanço físico
    fig_avanço = go.Figure()
    fig_avanço.add_trace(go.Bar(
        x=['Planejado', 'Real'],
        y=[0.99, 0.92],
        marker_color=['#2E86C1', '#E74C3C'],
        text=['99%', '92%'],
        textposition='auto',
    ))
    fig_avanço.update_layout(
        title="Avanço Físico",
        yaxis_title="Percentual",
        showlegend=False,
        height=300
    )
    st.plotly_chart(fig_avanço, use_container_width=True)

# Segunda coluna - Cronograma
with col2:
    st.subheader("📅 Cronograma")
    
    # Timeline do projeto
    st.metric("Aderência Física", "94%", delta="-6%")
    
    cronograma_data = {
        'Marco': ['Início', 'Tendência', 'Prazo Conclusão', 'Prazo Cliente'],
        'Data': ['1-jun', '1-set', '1-ago', '1-nov'],
        'Status': ['Concluído', 'Em Progresso', 'Atrasado', 'Meta']
    }
    
    cronograma_df = pd.DataFrame(cronograma_data)
    st.dataframe(cronograma_df, use_container_width=True, hide_index=True)
    
    # Gráfico de Gantt simplificado
    fig_gantt = go.Figure()
    dates = ['2024-06-01', '2024-08-01', '2024-09-01', '2024-11-01']
    colors = ['#27AE60', '#F39C12', '#E74C3C', '#8E44AD']
    
    for i, (marco, color) in enumerate(zip(cronograma_data['Marco'], colors)):
        fig_gantt.add_trace(go.Scatter(
            x=[dates[i]], y=[marco],
            mode='markers',
            marker=dict(size=15, color=color),
            name=marco
        ))
    
    fig_gantt.update_layout(
        title="Timeline do Projeto",
        xaxis_title="Data",
        height=300,
        showlegend=False
    )
    st.plotly_chart(fig_gantt, use_container_width=True)

# Terceira coluna - Financeiro
with col3:
    st.subheader("💰 Indicadores Financeiros")
    
    # Métricas financeiras principais
    st.metric("Orçamento Base", "R$ 102.593.965", delta=None)
    st.metric("Custo Final", "R$ 104.856.979", delta="R$ 2.263.014")
    st.metric("Desembolso", "R$ 95.337.442", delta=None)
    st.metric("Saldo", "R$ 9.519.537", delta=None)
    
    # Gráfico de rentabilidade
    fig_rent = go.Figure()
    fig_rent.add_trace(go.Bar(
        x=['Viabilidade', 'Projetada'],
        y=[22, 17],
        marker_color=['#28B463', '#F4D03F'],
        text=['22%', '17%'],
        textposition='auto',
    ))
    fig_rent.update_layout(
        title="Rentabilidade (%)",
        yaxis_title="Percentual",
        showlegend=False,
        height=300
    )
    st.plotly_chart(fig_rent, use_container_width=True)

# Seção de indicadores principais
st.subheader("🎯 Indicadores Principais")

col4, col5, col6, col7 = st.columns(4)

with col4:
    st.metric("Desvio Orçamentário", "1,12", delta="12%")

with col5:
    st.metric("Índice Econômico", "1,01", delta="1%")

with col6:
    st.metric("Custo m² AC", "R$ 3.574", delta=None)

with col7:
    st.metric("Custo m² AP", "R$ 7.119", delta=None)

# Gráfico de distribuição financeira
st.subheader("📊 Distribuição Financeira")

col8, col9 = st.columns(2)

with col8:
    # Gráfico pizza - distribuição orçamentária
    labels = ['Desembolsado', 'Saldo']
    values = [95337442, 9519537]
    
    fig_pizza = go.Figure(data=[go.Pie(
        labels=labels, 
        values=values,
        hole=.3,
        marker_colors=['#3498DB', '#E67E22']
    )])
    fig_pizza.update_layout(title="Distribuição do Orçamento")
    st.plotly_chart(fig_pizza, use_container_width=True)

with col9:
    # Comparativo de custos
    categorias = ['Orçamento Base', 'Orçamento Reajustado', 'Custo Final']
    valores = [102593965, 104856979, 104856979]
    
    fig_comparativo = go.Figure()
    fig_comparativo.add_trace(go.Bar(
        x=categorias,
        y=valores,
        marker_color=['#3498DB', '#F39C12', '#E74C3C'],
        text=[f'R$ {v:,.0f}' for v in valores],
        textposition='auto',
    ))
    fig_comparativo.update_layout(
        title="Comparativo de Custos",
        yaxis_title="Valor (R$)",
        showlegend=False
    )
    st.plotly_chart(fig_comparativo, use_container_width=True)

# Tabela completa dos dados
st.subheader("📋 Dados Completos do Projeto")
st.dataframe(df, use_container_width=True, hide_index=True)

# Footer
st.markdown("---")
st.markdown("Dashboard atualizado em tempo real | Dados do projeto de construção")
