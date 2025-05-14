import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- Configuração da página ---
st.set_page_config(page_title="Dashboard Integrado", layout="wide")

# --- Estilo escuro e CSS customizado ---
modo_escuro = st.sidebar.toggle("🌙 Modo Escuro", value=False)

cor_fundo = "#0e1117" if modo_escuro else "#ffffff"
cor_texto = "#ffffff" if modo_escuro else "#000000"
cor_sidebar = "#161b22" if modo_escuro else "#f0f2f6"

css = f"""
<style>
body {{
    background-color: {cor_fundo};
    color: {cor_texto};
}}
[data-testid="stSidebar"] {{
    background-color: {cor_sidebar};
}}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# --- Funções compartilhadas ---
@st.cache_data
def carregar_dados_produtividade():
    df = pd.read_excel("produtividade.xlsx")
    df['DATA'] = pd.to_datetime(df['DATA'], format='%d/%m/%Y')
    df['DATA_FORMATADA'] = df['DATA'].dt.strftime('%b/%y')
    return df

@st.cache_data
def carregar_dados_efetivo():
    df = pd.read_excel("efetivo_abril.xlsx", engine="openpyxl")
    df.columns = df.columns.str.strip()
    df = df.fillna(0)

    for col in ['Hora Extra 70% - Sabado', 'Hora Extra 70% - Semana', 'PRODUÇÃO']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    df['Tipo'] = df.get('DIRETO / INDIRETO', 'INDEFINIDO').astype(str).str.upper().str.strip()
    df['Total Extra'] = df['Hora Extra 70% - Sabado'] + df['Hora Extra 70% - Semana']
    return df

# --- Tabs do app ---
aba = st.tabs(["📈 Produtividade", "📊 Efetivo"])

# ========== PRODUTIVIDADE ==========
with aba[0]:
    st.title("📈 Dashboard de Produtividade")

    df_prod = carregar_dados_produtividade()

    tipo_obra_opcoes = ["Todos"] + df_prod['TIPO_OBRA'].unique().tolist()
    tipo_obra = st.sidebar.selectbox('Tipo de Obra', tipo_obra_opcoes)

    servicos_opcoes = df_prod['SERVIÇO'].unique().tolist()
    servico = st.sidebar.selectbox('Serviço', servicos_opcoes)

    datas_opcoes = ["Todos"] + df_prod['DATA_FORMATADA'].unique().tolist()
    datas_sel = st.sidebar.multiselect("Mês/Ano", datas_opcoes, default=datas_opcoes)

    # Filtro
    df_f = df_prod.copy()
    if tipo_obra != "Todos":
        df_f = df_f[df_f['TIPO_OBRA'] == tipo_obra]
    if servico:
        df_f = df_f[df_f['SERVIÇO'] == servico]
    if datas_sel and "Todos" not in datas_sel:
        df_f = df_f[df_f['DATA_FORMATADA'].isin(datas_sel)]

    # Gráficos
    df_mensal = df_f.groupby('DATA_FORMATADA').agg({
        'PRODUTIVIDADE_PROF_DIAM2': 'mean',
        'PRODUTIVIDADE_ORCADA_DIAM2': 'mean'
    }).reset_index()

    fig_linha = px.line(df_mensal, x='DATA_FORMATADA',
                        y=['PRODUTIVIDADE_PROF_DIAM2', 'PRODUTIVIDADE_ORCADA_DIAM2'],
                        labels={'value': 'Produtividade', 'DATA_FORMATADA': 'Mês/Ano'},
                        title="Produtividade Real x Orçada",
                        markers=True,
                        template='plotly_dark' if modo_escuro else 'plotly_white')
    fig_linha.update_layout(width=900, height=500)
    st.plotly_chart(fig_linha)

    df_tipo = df_f.groupby('TIPO_OBRA').agg({'PRODUTIVIDADE_PROF_DIAM2': 'mean'}).reset_index()
    fig_barra = px.bar(df_tipo, x='TIPO_OBRA', y='PRODUTIVIDADE_PROF_DIAM2',
                       title="Produtividade Média por Tipo de Obra",
                       template='plotly_dark' if modo_escuro else 'plotly_white')
    fig_barra.update_layout(width=900, height=500)
    st.plotly_chart(fig_barra)


# ========== EFETIVO ==========
with aba[1]:
    st.title("📊 Dashboard de Efetivo")

    # Carregar os dados de efetivo
    df_efetivo = carregar_dados_efetivo()

    # Filtros
    tipo_obra_efetivo_opcoes = ["Todos"] + df_efetivo['Obra'].unique().tolist()
    tipo_obra_efetivo = st.sidebar.selectbox('Tipo de Obra', tipo_obra_efetivo_opcoes)

    tipo_efetivo_opcoes = ['Todos', 'DIRETO', 'INDIRETO', 'TERCEIRO']
    tipo_efetivo = st.sidebar.selectbox('Tipo de Efetivo', tipo_efetivo_opcoes)

    # Filtro de mês (considerando que já existe a coluna 'DATA_FORMATADA')
    datas_opcoes_efetivo = ["Todos"] + df_efetivo['DATA_FORMATADA'].unique().tolist()
    datas_sel_efetivo = st.sidebar.multiselect("Mês/Ano", datas_opcoes_efetivo, default=datas_opcoes_efetivo)

    # Aplicando os filtros
    df_efetivo_filtrado = df_efetivo.copy()
    if tipo_obra_efetivo != "Todos":
        df_efetivo_filtrado = df_efetivo_filtrado[df_efetivo_filtrado['Obra'] == tipo_obra_efetivo]
    if tipo_efetivo != "Todos":
        df_efetivo_filtrado = df_efetivo_filtrado[df_efetivo_filtrado['Tipo'] == tipo_efetivo]
    if datas_sel_efetivo and "Todos" not in datas_sel_efetivo:
        df_efetivo_filtrado = df_efetivo_filtrado[df_efetivo_filtrado['DATA_FORMATADA'].isin(datas_sel_efetivo)]

    # Tabela com os dados filtrados
    st.markdown("### 📋 Efetivo - Dados Filtrados")
    st.dataframe(df_efetivo_filtrado)

    # --- Gráfico de Pizza para Tipo de Efetivo ---
    tipo_efetivo_count = df_efetivo_filtrado['Tipo'].value_counts().reset_index()
    tipo_efetivo_count.columns = ['Tipo', 'Contagem']
    fig_pizza_efetivo = px.pie(tipo_efetivo_count, names='Tipo', values='Contagem',
                               title="Distribuição por Tipo de Efetivo",
                               color_discrete_sequence=px.colors.sequential.Plasma)
    st.plotly_chart(fig_pizza_efetivo, use_container_width=True)

    # --- Gráfico de Barras para Efetivo por Função ---
    funcao_efetivo_count = df_efetivo_filtrado['Função'].value_counts().reset_index()
    funcao_efetivo_count.columns = ['Função', 'Contagem']
    fig_barra_efetivo = px.bar(funcao_efetivo_count, x='Função', y='Contagem', title="Efetivo por Função",
                               color='Contagem', color_continuous_scale='Blues')
    fig_barra_efetivo.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_barra_efetivo, use_container_width=True)

    # --- Gráfico de Dispersão para Produção vs Hora Extra Total ---
    fig_disp_efetivo = px.scatter(df_efetivo_filtrado,
                                  x="Total Extra",
                                  y="PRODUÇÃO",
                                  color="Tipo",
                                  hover_data=["Funcionário", "Função", "Obra"],
                                  trendline="ols",
                                  labels={"Total Extra": "Hora Extra Total", "PRODUÇÃO": "Produção"},
                                  title="Dispersão: Hora Extra Total vs Produção")
    st.plotly_chart(fig_disp_efetivo, use_container_width=True)
